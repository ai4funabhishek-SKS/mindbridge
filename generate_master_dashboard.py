import pandas as pd
from pathlib import Path

BASE_DIR = Path(r"C:\KnowledgeBase_Staging")
REPORT_MD = BASE_DIR / "raw_copies_index.md"
OUTPUT_DIR = BASE_DIR / "00_Index_and_Dashboards"
EXCEL_OUTPUT = OUTPUT_DIR / "Master_Second_Brain_Dashboard.xlsx"

def infer_asset_type(filename: str) -> str:
    """Categorize asset format based on extension/name."""
    fn = filename.lower()
    if fn.endswith('.json') and ('agent' in fn or 'workflow' in fn or 'node' in fn):
        return "n8n_or_Agent_Config"
    elif fn.endswith('.json'):
        return "JSON_Config"
    elif fn.endswith('.pdf'):
        return "PDF_Document"
    elif fn.endswith(('.doc', '.docx')):
        return "Word_Document"
    elif fn.endswith(('.xls', '.xlsx', '.csv')):
        return "Spreadsheet"
    elif fn.endswith(('.txt', '.md')):
        return "Note_or_Prompt"
    else:
        return "General_Asset"

def generate_dashboard():
    if not REPORT_MD.exists():
        print("Error: raw_copies_index.md not found. Please run inspect_raw.py first.")
        return

    print("Parsing file index for Excel Dashboard...")
    lines = REPORT_MD.read_text(encoding='utf-8').splitlines()
    
    data = []
    for line in lines:
        if line.startswith("| `"):
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 5:
                fname = parts[1].replace("`", "")
                size = parts[2]
                desc = parts[3]
                rating = parts[4].replace("**", "")
                asset_type = infer_asset_type(fname)
                
                data.append({
                    "File Name": fname,
                    "Asset Format": asset_type,
                    "Size": size,
                    "Description": desc,
                    "Content Rating": rating
                })

    df = pd.DataFrame(data)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Writing multi-tab Excel workbook...")
    with pd.ExcelWriter(EXCEL_OUTPUT, engine='openpyxl') as writer:
        # Tab 1: Master Searchable Inventory
        df.to_excel(writer, sheet_name='Master Index', index=False)
        
        # Tab 2: Asset Format Breakdown Summary
        format_summary = df["Asset Format"].value_counts().reset_index()
        format_summary.columns = ["Asset Format", "Count"]
        format_summary.to_excel(writer, sheet_name='Asset Format Summary', index=False)

        # Tab 3: Content Rating Summary
        rating_summary = df["Content Rating"].value_counts().reset_index()
        rating_summary.columns = ["Content Rating", "Count"]
        rating_summary.to_excel(writer, sheet_name='Rating Summary', index=False)

    print(f"\nSuccess! Master Dashboard created at:\n{EXCEL_OUTPUT}")

if __name__ == "__main__":
    generate_dashboard()