import json
import os
import yaml
import glob
import re

# Paths
BASE_DIR = r"C:\knowledgeBase_staging"
MANIFEST_PATH = os.path.join(BASE_DIR, "Processed_Assets", "file_classification_manifest.json")
RAW_DIR = os.path.join(BASE_DIR, "Raw_copies")
GM_DIR = os.path.join(BASE_DIR, "03_Topics_and_Projects")

domains_to_process = [
    "01_AI_Agents_and_Autonomous_Systems",
    "02_Workflow_Automations_n8n",
    "03_Prompt_Engineering_and_Frameworks",
    "04_Mobile_and_Android_Ecosystem",
    "05_Code_Snippets_and_Dev_Tools"
]

def load_manifest():
    with open(MANIFEST_PATH, "r", encoding="utf-8", errors="ignore") as f:
        return json.load(f)

def extract_content(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return f"Reference document: {os.path.basename(file_path)}. (Binary PDF content not extracted)."
    elif ext == ".json":
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                data = json.load(f)
                # extract key info instead of full json
                # just dump it formatted but maybe truncated or summarize nodes
                if isinstance(data, dict) and "nodes" in data:
                    nodes = [n.get("name", "Unknown Node") for n in data["nodes"]]
                    return f"JSON Workflow Configuration. Nodes included: {', '.join(nodes)}"
                elif isinstance(data, list):
                    return f"JSON Data Array with {len(data)} items."
                else:
                    s = json.dumps(data, indent=2)
                    return s[:1000] + "\n... (truncated)"
        except Exception as e:
            return f"Error parsing JSON: {e}"
    else: # txt, md, docx (docx will be garbled but we read as text)
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                return content[:2000] + ("\n... (truncated)" if len(content) > 2000 else "")
        except Exception as e:
            return f"Error reading file: {e}"

def update_gm(target_gm_path, source_file, content, rationale):
    if not os.path.exists(target_gm_path):
        return False
    
    with open(target_gm_path, "r", encoding="utf-8", errors="ignore") as f:
        gm_content = f.read()

    # Update YAML frontmatter
    source_files_pattern = r"(source_files_synthesized:\s*\n)((?:[-]\s*[^\n]+\n)*)"
    
    def replacement(match):
        prefix = match.group(1)
        list_content = match.group(2)
        new_entry = f"- {os.path.basename(source_file)}\n"
        if new_entry not in list_content:
            return prefix + list_content + new_entry
        return match.group(0)

    if "source_files_synthesized:" in gm_content:
        gm_content = re.sub(source_files_pattern, replacement, gm_content, count=1)
    
    # Append content
    new_section = f"\n\n## Content Integrated from {os.path.basename(source_file)}\n"
    new_section += f"**Source Lineage / Rationale:** {rationale}\n\n"
    if content.startswith("Reference") or content.startswith("JSON Workflow"):
        new_section += f"{content}\n"
    else:
        new_section += f"```\n{content}\n```\n"

    gm_content += new_section

    with open(target_gm_path, "w", encoding="utf-8") as f:
        f.write(gm_content)
    return True

def create_new_gm(filename, title, domain, source_file_name, content, rationale):
    domain_path = os.path.join(GM_DIR, domain)
    if not os.path.exists(domain_path):
        os.makedirs(domain_path)
    
    target_path = os.path.join(domain_path, filename)
    
    frontmatter = f'''---
title: {title}
domain: {domain}
tags:
  - newly-created
  - synthesized
source_files_synthesized:
  - {source_file_name}
---

# {title}

## Source Lineage
**Source:** {source_file_name}
**Rationale:** {rationale}

## Integrated Content
'''
    if content.startswith("Reference") or content.startswith("JSON Workflow"):
        frontmatter += f"{content}\n"
    else:
        frontmatter += f"```\n{content}\n```\n"

    with open(target_path, "w", encoding="utf-8") as f:
        f.write(frontmatter)

def main():
    manifest = load_manifest()
    expanded_count = 0
    new_gm_count = 0
    total_sources_integrated = 0
    failed_files = []

    for entry in manifest:
        domain = entry.get("domain")
        action = entry.get("action")
        target_gm = entry.get("target_gm")
        raw_path = entry.get("raw_path")
        rationale = entry.get("rationale")
        
        full_source_path = os.path.join(BASE_DIR, raw_path.replace("/", "\\"))
        
        if domain in domains_to_process and action == "merge_into_existing_gm" and target_gm:
            target_gm_path = os.path.join(GM_DIR, domain, target_gm)
            if not os.path.exists(target_gm_path):
                failed_files.append(f"{raw_path} - Target GM {target_gm} not found in {domain}")
                continue
            
            content = extract_content(full_source_path)
            success = update_gm(target_gm_path, full_source_path, content, rationale)
            if success:
                expanded_count += 1
                total_sources_integrated += 1
            else:
                failed_files.append(f"{raw_path} - Failed to update target GM")
                
        elif entry.get("raw_path").endswith("AIS Resume Indeed.json"):
            content = extract_content(full_source_path)
            # best domain: 02_Workflow_Automations_n8n or maybe 01_AI_Agents? Let's use 02
            create_new_gm(
                "GM_Recruitment_and_Resume_Parsing_Automation.md",
                "Recruitment and Resume Parsing Automation",
                "02_Workflow_Automations_n8n",
                "AIS Resume Indeed.json",
                content,
                rationale
            )
            new_gm_count += 1
            total_sources_integrated += 1
            
        elif entry.get("raw_path").endswith("Hormozi AI.json"):
            content = extract_content(full_source_path)
            create_new_gm(
                "GM_Expert_Persona_Cloning_and_Marketing_Copy_Engine.md",
                "Expert Persona Cloning and Marketing Copy Engine",
                "03_Prompt_Engineering_and_Frameworks",
                "Hormozi AI.json",
                content,
                rationale
            )
            new_gm_count += 1
            total_sources_integrated += 1

    print(f"GMs expanded: {expanded_count}")
    print(f"New GMs created: {new_gm_count}")
    print(f"Total sources integrated: {total_sources_integrated}")
    print("Failed files:")
    for f in failed_files:
        print(f)

if __name__ == "__main__":
    main()
