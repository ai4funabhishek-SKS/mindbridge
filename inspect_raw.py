import os
from pathlib import Path

RAW_DIR = Path(r"C:\KnowledgeBase_Staging\Raw_copies")
OUTPUT_REPORT = Path(r"C:\KnowledgeBase_Staging\raw_copies_index.md")

def evaluate_content(file_path: Path) -> tuple[str, str]:
    """Inspects file name and content snippet to determine description and category rating."""
    name_lower = file_path.name.lower()
    
    # Quick content preview for text/code files
    snippet = ""
    try:
        if file_path.suffix.lower() in ['.txt', '.md', '.json', '.py', '.env', '.csv', '.yaml', '.yml']:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                snippet = f.read(500).lower()
    except Exception:
        pass

    # Check rating criteria
    if any(k in name_lower or k in snippet for k in ['credential', 'password', 'api_key', 'secret', 'token', 'auth', '.env']):
        return "Contains sensitive credentials or access keys.", "has credentials"
    elif any(k in name_lower for k in ['junk', 'temp', 'old', 'backup', 'test']):
        return "Temporary or obsolete test file with limited ongoing value.", "junk-discard"
    elif any(k in name_lower or k in snippet for k in ['boilerplate', 'template', 'starter', 'base']):
        return "Standardized template or boilerplate structure for rapid deployment.", "boilerplate"
    elif any(k in name_lower or k in snippet for k in ['draft', 'idea', 'concept', 'todo', 'rough']):
        return "Early-stage draft or conceptual note requiring further refinement.", "half baked idea"
    elif file_path.stat().st_size == 0:
        return "Empty file with no content recorded.", "junk-discard"
    else:
        return "Core reference material or documentation asset for ongoing projects.", "keep for reference / future reusable"

def generate_index():
    if not RAW_DIR.exists():
        print(f"Error: Directory not found -> {RAW_DIR}")
        return

    print(f"Inspecting files in {RAW_DIR}...")
    
    report_lines = [
        "# Raw Copies Content Index & Evaluation\n",
        "| File Name | Size (KB) | Description (2-3 lines) | Content Rating |",
        "|---|---|---|---|"
    ]

    file_count = 0
    for root, _, files in os.walk(RAW_DIR):
        for file in files:
            file_path = Path(root) / file
            file_count += 1
            
            size_kb = round(file_path.stat().st_size / 1024, 2)
            desc, rating = evaluate_content(file_path)
            
            rel_path = file_path.relative_to(RAW_DIR)
            report_lines.append(f"| `{rel_path}` | {size_kb} KB | {desc} | **{rating}** |")

    OUTPUT_REPORT.write_text("\n".join(report_lines), encoding='utf-8')
    print(f"\nInspection complete! Processed {file_count} files.")
    print(f"Report successfully saved to: {OUTPUT_REPORT}")

if __name__ == "__main__":
    generate_index()