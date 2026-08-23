"""Print compact classification view for a slice of the digest file.
Usage: python m5_review_slice.py START END  (indices into remaining queue)
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
D = json.loads((ROOT / "Processed_Assets" / "m5_digests.json").read_text(encoding="utf-8"))
Q = json.loads((ROOT / "Processed_Assets" / "m5_remaining_queue.json").read_text(encoding="utf-8"))

start, end = int(sys.argv[1]), int(sys.argv[2])
for i in range(start, min(end, len(Q))):
    rel = Q[i]
    d = D.get(rel, {})
    k = d.get("kind", "?")
    name = Path(rel).name
    sig = ""
    if k == "text":
        h = " / ".join(d.get("headings", [])[:3])
        c = d.get("counts", {})
        sig = f"H[{h[:90]}] code={c.get('code_blocks')} prompt={c.get('prompt_markers')} :: {d.get('preview','')[:110]}"
    elif k == "n8n_workflow":
        sig = f"nodes={d.get('node_count')} types={','.join(d.get('node_types', [])[:6])}"
    elif k == "json_dict":
        sig = f"keys={','.join(d.get('keys', [])[:6])} :: {d.get('preview','')[:80]}"
    elif k == "json_list":
        sig = f"list[{d.get('len')}] :: {d.get('preview','')[:80]}"
    elif k.startswith("pdf"):
        sig = f"pages={d.get('pages')} :: {d.get('preview', d.get('error',''))[:110]}"
    elif k == "docx":
        sig = f"paras={d.get('paragraphs')} tables={d.get('tables')} :: {d.get('preview','')[:100]}"
    elif k.startswith("xlsx"):
        sig = f"sheets={list(d.get('sheets', {}).items())[:4]} {d.get('error','')}"
    else:
        sig = json.dumps(d)[:120]
    print(f"[{i:03}] {name[:58]} ({k})")
    print(f"      {sig}")
