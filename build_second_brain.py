import os
from pathlib import Path

BASE_DIR = Path(r"C:\KnowledgeBase_Staging")

# Define the Master Dual-Axis Architecture
DIRECTORIES = [
    # Index & Dashboards
    "00_Index_and_Dashboards",
    
    # 1. Private Vault (Secure / Git Ignored)
    "01_Vault_Private/credentials_and_keys",
    "01_Vault_Private/financial_statements",
    "01_Vault_Private/personal_identity",
    
    # 2. Assets Library (Browse by Format)
    "02_Assets_Library/01_Agents_and_Configs",
    "02_Assets_Library/02_Automations_n8n",
    "02_Assets_Library/03_Prompts_and_Engineering",
    "02_Assets_Library/04_Code_and_Scripts",
    "02_Assets_Library/05_Media_and_YouTube",
    "02_Assets_Library/06_Skool_and_Resources",
    "02_Assets_Library/07_Documents_and_PDFs",
    "02_Assets_Library/08_Notes_and_Brainstorms",
    
    # 3. Topics & Projects (Browse by Subject)
    "03_Topics_and_Projects/AI_Agents_and_Automation",
    "03_Topics_and_Projects/Financial_Trading_Systems",
    "03_Topics_and_Projects/Content_Creation_and_YouTube",
    "03_Topics_and_Projects/Business_Subbroking",
    "03_Topics_and_Projects/General_Research_and_Ideas"
]

def build_structure():
    print("Building Master Second Brain Folder Structure...")
    for rel_path in DIRECTORIES:
        full_path = BASE_DIR / rel_path
        full_path.mkdir(parents=True, exist_ok=True)
        print(f"Verified/Created: {rel_path}")
        
    # Ensure .gitignore is properly configured to protect the private vault
    gitignore_path = BASE_DIR / ".gitignore"
    gitignore_content = "# Ignore private vault folder entirely\n01_Vault_Private/\n\n# Ignore environment files and system junk\n.env\n*.log\nThumbs.db\nDesktop.ini\n$RECYCLE.BIN/\n"
    gitignore_path.write_text(gitignore_content, encoding='utf-8')
    print(".gitignore updated to protect 01_Vault_Private/")

    print("\nMaster Second Brain scaffolding complete!")

if __name__ == "__main__":
    build_structure()