#!/usr/bin/env python3
"""
mindbridge Weekly Knowledge School
Automated weekly ingestion pipeline: Monitor → Classify → Enrich → Index → Verify → Report
Runs every Sunday 2AM via Windows Task Scheduler
"""

import os
import sys
import json
import yaml
import sqlite3
import schedule
import time
import subprocess
import smtplib
import ssl
from pathlib import Path
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Optional, Tuple
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from llm_providers import LLMManager, get_embedding, get_embeddings_batch
import search_engine as se

# ============================================================================
# CONFIGURATION
# ============================================================================

PROJECT_ROOT = Path(__file__).parent
CONFIG_PATH = PROJECT_ROOT / "mindbridge_config.yaml"
AUTO_RULES_PATH = PROJECT_ROOT / "auto_rules.yaml"
DB_PATH = PROJECT_ROOT / "Processed_Assets" / "my_rag_data.db"

# Load configuration
with open(CONFIG_PATH, 'r') as f:
    CONFIG = yaml.safe_load(f)

with open(AUTO_RULES_PATH, 'r') as f:
    AUTO_RULES = yaml.safe_load(f)

EMAIL_CONFIG = {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "username": os.environ.get("EMAIL_USERNAME"),
    "password": os.environ.get("EMAIL_APP_PASSWORD"),
    "recipient": CONFIG.get("auto_ingestion", {}).get("email_recipient", "Aiadoptionconsultant@gmail.com"),
}

# ============================================================================
# DATABASE HELPERS
# ============================================================================

def get_db_connection():
    """Get database connection with row factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_last_ingestion_time() -> float:
    """Get timestamp of last successful ingestion run."""
    conn = get_db_connection()
    try:
        row = conn.execute(
            "SELECT MAX(timestamp) FROM ingestion_log WHERE status = 'success'"
        ).fetchone()
        return row[0] if row and row[0] else 0
    finally:
        conn.close()

def log_ingestion_run(files_processed: int, status: str, report: str, duration: float) -> None:
    """Log ingestion run to database."""
    conn = get_db_connection()
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS ingestion_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                files_processed INTEGER DEFAULT 0,
                status TEXT NOT NULL,
                report TEXT,
                duration_seconds REAL DEFAULT 0
            )
        """)
        conn.execute(
            "INSERT INTO ingestion_log (timestamp, files_processed, status, report, duration_seconds) VALUES (?, ?, ?, ?, ?)",
            (time.time(), files_processed, status, report, duration)
        )
        conn.commit()
    finally:
        conn.close()

def get_watch_folders() -> List[Dict]:
    """Get watch folders from auto_rules.yaml."""
    return AUTO_RULES.get("watch_folders", [])

def get_classification_rules() -> List[Dict]:
    """Get classification rules sorted by priority."""
    rules = AUTO_RULES.get("classification_rules", [])
    return sorted(rules, key=lambda x: x.get("priority", 100))

# ============================================================================
# FILE SCANNING
# ============================================================================

class KnowledgeSchoolHandler(FileSystemEventHandler):
    """Watchdog handler for real-time file detection (optional)."""
    
    def __init__(self, school: 'KnowledgeSchool'):
        self.school = school
    
    def on_created(self, event):
        if not event.is_directory:
            self.school.queue_file(event.src_path)
    
    def on_modified(self, event):
        if not event.is_directory:
            self.school.queue_file(event.src_path)

class KnowledgeSchool:
    """Main Knowledge School orchestrator."""
    
    def __init__(self):
        self.db_path = DB_PATH
        self.report = []
        self.start_time = time.time()
        self.observer = None
        self.file_queue = []
        
        # Load configurations
        self.config = CONFIG
        self.auto_rules = AUTO_RULES
        
        # Initialize LLM manager
        self.llm_manager = None
        self._init_llm_manager()
    
    def _init_llm_manager(self):
        """Initialize LLM manager from config."""
        try:
            from llm_providers import LLMManager
            self.llm_manager = LLMManager(str(PROJECT_ROOT / "llm_config.yaml"))
        except Exception as e:
            print(f"Warning: LLM manager initialization failed: {e}")
            self.llm_manager = None
    
    def scan_new_files(self, since_timestamp: float = None) -> List[Path]:
        """Scan watch folders for new/modified files since last run."""
        if since_timestamp is None:
            since_timestamp = get_last_ingestion_time()
        
        new_files = []
        watch_folders = get_watch_folders()
        
        for folder_config in watch_folders:
            folder_path = Path(folder_config["path"]).expanduser()
            if not folder_path.exists():
                print(f"Watch folder does not exist: {folder_path}")
                continue
            
            recursive = folder_config.get("recursive", True)
            include_patterns = folder_config.get("include_patterns", ["*"])
            exclude_patterns = folder_config.get("exclude_patterns", [])
            
            # Use rglob for recursive, glob for non-recursive
            if recursive:
                files = folder_path.rglob("*")
            else:
                files = folder_path.glob("*")
            
            for file_path in files:
                if not file_path.is_file():
                    continue
                
                # Check modification time
                try:
                    mtime = file_path.stat().st_mtime
                    if mtime <= since_timestamp:
                        continue
                except OSError:
                    continue
                
                # Check include patterns
                matched_include = False
                for pattern in include_patterns:
                    if file_path.match(pattern):
                        matched_include = True
                        break
                if not matched_include:
                    continue
                
                # Check exclude patterns
                excluded = False
                for pattern in exclude_patterns:
                    if file_path.match(pattern):
                        excluded = True
                        break
                if excluded:
                    continue
                
                new_files.append(file_path)
        
        return new_files

    def classify_file(self, file_path: Path) -> str:
        """Classify a file using classification rules."""
        file_name = file_path.name
        file_lower = file_name.lower()
        
        rules = get_classification_rules()
        for rule in rules:
            patterns = rule.get("patterns", [])
            for pattern in patterns:
                # Simple glob matching
                import fnmatch
                if fnmatch.fnmatch(file_lower, pattern.lower()):
                    return rule["action"]
        
        return "review"

    def classify_with_llm(self, file_path: Path) -> str:
        """Classify file using LLM for ambiguous cases."""
        if not self.llm_manager:
            return "review"
        
        try:
            # Read first 2000 chars of file
            content = ""
            try:
                if file_path.suffix.lower() in ['.pdf', '.docx', '.xlsx']:
                    # Skip binary files for LLM classification
                    return "review"
                content = file_path.read_text(encoding='utf-8', errors='ignore')[:2000]
            except Exception:
                return "review"
            
            if not content.strip():
                return "review"
            
            prompt = f"""Classify this file into one of these categories:
- vault (secrets, keys, PII, financial data)
- cold_storage (temp files, logs, duplicates, boilerplate, build artifacts)
- 01_AI_Agents_and_Autonomous_Systems
- 02_Workflow_Automations_n8n
- 03_Prompt_Engineering_and_Frameworks
- 04_Mobile_and_Android_Ecosystem
- 05_Code_Snippets_and_Dev_Tools
- 06_Quantitative_Finance_and_Trading
- 07_Content_Creation_and_Media_Engines
- 08_Business_Operations_and_Subbroking
- 09_LLM_Conversations_and_Syntheses
- 10_R_and_D_Incubator_Half_Baked_Ideas
- 05_Reference_Documentation
- 04_Prompt_Engineering_quick_prompts
- review (uncertain)

File: {file_path.name}
Content preview: {content[:1000]}

Respond with ONLY the category name."""
            
            messages = [
                {"role": "system", "content": "You are a file classifier. Respond with ONLY the category name."},
                {"role": "user", "content": prompt}
            ]
            
            try:
                response = self.llm_manager.chat_with_fallback(
                    messages,
                    temperature=0.1,
                    max_tokens=50
                )
                return response.strip().lower()
            except Exception as e:
                print(f"LLM classification failed for {file_path}: {e}")
                return "review"
                
        except Exception as e:
            print(f"LLM classification error: {e}")
            return "review"

    def enrich_file(self, file_path: Path, category: str) -> Dict:
        """Enrich file metadata."""
        enrichment = {
            "file_path": str(file_path),
            "file_name": file_path.name,
            "category": category,
            "size_bytes": file_path.stat().st_size,
            "extension": file_path.suffix.lower(),
            "modified_time": file_path.stat().st_mtime,
        }
        
        enrichment_config = CONFIG.get("enrichment", {})
        
        # Read file content for enrichment
        content = ""
        try:
            if file_path.suffix.lower() not in ['.pdf', '.docx', '.xlsx', '.exe', '.dll', '.so', '.dylib']:
                content = file_path.read_text(encoding='utf-8', errors='ignore')[:5000]
        except Exception:
            pass
        
        enrichment["content_preview"] = content[:500]
        
        # TODO: Add LLM-based enrichment (entities, summary, tags, related)
        # This would use the LLM manager to extract entities, generate summary, etc.
        
        return enrichment

    def ingest_file(self, file_path: Path) -> Tuple[bool, str]:
        """Ingest a single file into the knowledge base."""
        try:
            # Classify file
            category = self.classify_file(file_path)
            
            # For ambiguous cases, use LLM
            if category == "review":
                category = self.classify_with_llm(file_path)
            
            # Special handling for vault/cold_storage
            if category in ["vault", "cold_storage"]:
                # Move to appropriate location (handled by process_gms.py)
                return self._move_to_storage(file_path, category)
            
            # Enrich file
            enrichment = self.enrich_file(file_path, category)
            
            # Ingest into knowledge base
            # This would use the existing ingestion pipeline
            # For now, we'll use the existing process_gms.py
            return self._ingest_via_pipeline(file_path, category)
            
        except Exception as e:
            return False, f"Error ingesting {file_path}: {e}"
    
    def _move_to_storage(self, file_path: Path, category: str) -> Tuple[bool, str]:
        """Move file to vault or cold storage."""
        try:
            if category == "vault":
                dest_dir = PROJECT_ROOT / "01_Vault_Private" / "auto_ingested"
            else:
                dest_dir = PROJECT_ROOT / "04_Archive_Cold_Storage" / "auto_ingested"
            
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest_path = dest_dir / file_path.name
            
            # Handle name conflicts
            counter = 1
            original_dest = dest_path
            while dest_path.exists():
                stem = original_dest.stem
                suffix = original_dest.suffix
                dest_path = dest_dir / f"{stem}_{counter}{suffix}"
                counter += 1
            
            # Copy (don't move - non-destructive)
            import shutil
            shutil.copy2(file_path, dest_path)
            return True, f"Copied to {category}"
        except Exception as e:
            return False, f"Failed to move to {category}: {e}"
    
    def _ingest_via_pipeline(self, file_path: Path, category: str) -> Tuple[bool, str]:
        """Ingest file using existing pipeline."""
        try:
            # Use the existing process_gms.py or ingestion script
            result = subprocess.run([
                sys.executable, "process_gms.py",
                "--file", str(file_path),
                "--domain", category
            ], capture_output=True, text=True, timeout=120, cwd=PROJECT_ROOT)
            
            if result.returncode == 0:
                return True, "Ingested successfully"
            else:
                return False, f"Ingestion failed: {result.stderr}"
        except subprocess.TimeoutExpired:
            return False, "Ingestion timeout"
        except Exception as e:
            return False, f"Ingestion error: {e}"

    def run_weekly_school(self) -> Dict:
        """Run the complete weekly Knowledge School session."""
        print("🏫 Knowledge School in session...")
        start_time = time.time()
        
        self.report = {
            "start_time": datetime.now().isoformat(),
            "files_found": 0,
            "files_processed": 0,
            "files_failed": 0,
            "by_category": {},
            "errors": [],
            "test_results": None,
        }
        
        # Scan for new files
        print("🔍 Scanning for new files...")
        new_files = self.scan_new_files()
        self.report["files_found"] = len(new_files)
        print(f"   Found {len(new_files)} new/modified files")
        
        if not new_files:
            self.report["status"] = "no_new_files"
            self.report["end_time"] = datetime.now().isoformat()
            self.report["duration_seconds"] = time.time() - self.start_time
            self._save_report()
            return self.report
        
        # Process each file
        print("📚 Processing files...")
        for i, file_path in enumerate(new_files, 1):
            print(f"   [{i}/{len(new_files)}] {file_path.name}")
            success, message = self.ingest_file(file_path)
            
            if success:
                self.report["files_processed"] += 1
                # Get category for stats
                category = "unknown"
                self.report["by_category"][category] = self.report["by_category"].get(category, 0) + 1
            else:
                self.report["files_failed"] += 1
                self.report["errors"].append(f"{file_path.name}: {message}")
            
            # Progress indicator
            if i % 10 == 0:
                print(f"   Progress: {i}/{len(new_files)}")
        
        # Rebuild search index
        print("🔨 Rebuilding search index...")
        self._rebuild_search_index()
        
        # Run tests
        print("🧪 Running test suite...")
        test_result = self._run_tests()
        self.report["test_results"] = test_result
        
        # Finalize report
        self.report["end_time"] = datetime.now().isoformat()
        self.report["duration_seconds"] = time.time() - start_time
        self.report["status"] = "success" if self.report["files_failed"] == 0 else "partial"
        
        self._save_report()
        self._send_email_report()
        
        print(f"✅ Knowledge School complete!")
        print(f"   Processed: {self.report['files_processed']}")
        print(f"   Failed: {self.report['files_failed']}")
        print(f"   Duration: {self.report['duration_seconds']:.1f}s")
        
        return self.report
    
    def _rebuild_search_index(self):
        """Rebuild search index components."""
        try:
            # Rebuild anchors
            subprocess.run([
                sys.executable, "build_doc_anchors.py", "--force"
            ], check=True, cwd=PROJECT_ROOT, capture_output=True)
            
            # Rebuild folder indexes
            subprocess.run([
                sys.executable, "build_folder_indexes.py"
            ], check=True, cwd=PROJECT_ROOT, capture_output=True)
            
            # Regenerate dashboards
            subprocess.run([
                sys.executable, "deep_inspect_and_build_dashboard.py"
            ], check=True, cwd=PROJECT_ROOT, capture_output=True)
            
        except subprocess.CalledProcessError as e:
            print(f"Warning: Rebuild failed: {e}")
            self.report["errors"].append(f"Rebuild failed: {e}")

    def _run_tests(self) -> Dict:
        """Run test suite and return results."""
        try:
            result = subprocess.run([
                sys.executable, "-m", "pytest", "tests/", "-q", "--tb=line"
            ], capture_output=True, text=True, timeout=300, cwd=PROJECT_ROOT)
            
            return {
                "passed": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout[-2000:] if result.stdout else "",
                "stderr": result.stderr[-2000:] if result.stderr else "",
            }
        except subprocess.TimeoutExpired:
            return {"passed": False, "error": "Test timeout"}
        except Exception as e:
            return {"passed": False, "error": str(e)}

    def _save_report(self):
        """Save ingestion report to database."""
        duration = time.time() - self.start_time
        status = self.report.get("status", "unknown")
        
        report_text = f"""
Knowledge School Run Report
===========================
Start Time: {self.report.get('start_time')}
End Time: {datetime.now().isoformat()}
Duration: {self.report.get('duration_seconds', 0):.1f}s
Status: {status}

Files Found: {self.report['files_found']}
Files Processed: {self.report['files_processed']}
Files Failed: {self.report['files_failed']}

Categories:
{json.dumps(self.report.get('by_category', {}), indent=2)}

Errors:
{chr(10).join(self.report.get('errors', []))}

Test Results: {json.dumps(self.report.get('test_results'), indent=2)}
"""
        
        log_ingestion_run(
            files_processed=self.report["files_processed"],
            status=status,
            report=report_text,
            duration=self.report.get("duration_seconds", 0)
        )

    def _send_email_report(self):
        """Send email report."""
        if not EMAIL_CONFIG.get("username") or not EMAIL_CONFIG.get("password"):
            print("Email credentials not configured, skipping email report")
            return
        
        try:
            msg = MIMEMultipart()
            msg['From'] = EMAIL_CONFIG["username"]
            msg['To'] = EMAIL_CONFIG["recipient"]
            msg['Subject'] = f"🏫 Knowledge School Report - {datetime.now().strftime('%Y-%m-%d')}"
            
            body = f"""
Knowledge School Weekly Report
==============================

Run Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Duration: {self.report.get('duration_seconds', 0):.1f} seconds
Status: {self.report.get('status', 'unknown').upper()}

Files Found: {self.report['files_found']}
Files Processed: {self.report['files_processed']}
Files Failed: {self.report['files_failed']}

Categories Processed:
{json.dumps(self.report.get('by_category', {}), indent=2)}

Errors:
{chr(10).join(self.report.get('errors', [])) or 'None'}

Test Results: {'PASSED' if self.report.get('test_results', {}).get('passed') else 'FAILED'}

---
mindbridge Knowledge School
Automated Weekly Ingestion
"""
            msg.attach(MIMEText(body, 'plain'))
            
            context = ssl.create_default_context()
            with smtplib.SMTP(EMAIL_CONFIG["smtp_server"], EMAIL_CONFIG["smtp_port"]) as server:
                server.starttls(context=context)
                server.login(EMAIL_CONFIG["username"], EMAIL_CONFIG["password"])
                server.send_message(msg)
            
            print(f"📧 Email report sent to {EMAIL_CONFIG['recipient']}")
        except Exception as e:
            print(f"Failed to send email report: {e}")

    def start_observer(self):
        """Start filesystem observer for real-time detection (optional)."""
        watch_folders = get_watch_folders()
        self.observer = Observer()
        
        for folder_config in watch_folders:
            folder_path = Path(folder_config["path"]).expanduser()
            if folder_path.exists():
                handler = KnowledgeSchoolHandler(self)
                self.observer.schedule(handler, str(folder_path), recursive=folder_config.get("recursive", True))
        
        self.observer.start()
        print("👁️  File observer started")

    def stop_observer(self):
        """Stop filesystem observer."""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            print("👁️  File observer stopped")

    def queue_file(self, file_path: str):
        """Queue a file for processing (used by observer)."""
        self.file_queue.append(file_path)

    def process_queue(self):
        """Process queued files (for real-time mode)."""
        while self.file_queue:
            file_path = self.file_queue.pop(0)
            self.ingest_file(Path(file_path))

def run_manual_ingestion():
    """Run manual ingestion for testing."""
    school = KnowledgeSchool()
    return school.run_weekly_school()

def run_daemon():
    """Run as daemon with scheduler."""
    school = KnowledgeSchool()
    school.start_observer()
    
    # Schedule weekly run
    schedule.every().sunday.at("02:00").do(school.run_weekly_school)
    
    print("🏫 Knowledge School daemon started")
    print("   Scheduled: Every Sunday 02:00")
    print("   Press Ctrl+C to stop")
    
    try:
        while True:
            schedule.run_pending()
            # Process any queued files
            if school.file_queue:
                school.process_queue()
            time.sleep(60)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        school.stop_observer()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "daemon":
        run_daemon()
    elif len(sys.argv) > 1 and sys.argv[1] == "test":
        # Quick test run
        school = KnowledgeSchool()
        report = school.run_weekly_school()
        print(json.dumps(report, indent=2))
    else:
        # Normal weekly run
        school = KnowledgeSchool()
        report = school.run_weekly_school()
        print(json.dumps(report, indent=2, default=str))