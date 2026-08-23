#!/usr/bin/env python3
"""Rebuild 01_Vault_Private/MASTER_CREDENTIALS_REGISTRY.md as the single
authoritative registry holding ACTUAL secret values (owner decision 2026-08-23).

Sources consolidated:
  - credentials_and_keys/my_api_keys_backup.md   (OmniRoute export, 47 accounts)
  - credentials_and_keys/key.txt                 (DeepInfra/Jina/Hyperbolic/Cohere)
  - credentials_and_keys/test.env.txt            (Groq/HF/z.ai snippets)
  - credentials_and_keys/Fiecrawal ai.txt        (Firecrawl)
  - credentials_and_keys/client_secret_*.json    (Google OAuth)
  - Raw_copies/Tavily's AI.txt                   (Tavily #1)
  - Raw_copies/YouTube_Content_Idea_Generator (1).json (Tavily #2, previously missing)
  - vault n8n workflow JSONs                     (embedded OpenAI-style keys)

Console output is masked; full values are written ONLY into gitignored vault.
"""
import json
import os
import re
import sys

VAULT = "01_Vault_Private"
CK = os.path.join(VAULT, "credentials_and_keys")
REG_PATH = os.path.join(VAULT, "MASTER_CREDENTIALS_REGISTRY.md")
INV_PATH = os.path.join(VAULT, "_credentials_inventory.json")

TABLE_ROW = re.compile(r"^\|\s*\*\*(.+?)\*\*\s*\|\s*`?(.+?)`?\s*\|\s*`?(.+?)`?\s*\|\s*`?(.+?)`?\s*\|")


def mask(v):
    v = str(v)
    return v[:6] + "***" + v[-4:] if len(v) > 14 else v[:3] + "***"


def norm_provider(p):
    return p.strip().upper().replace("_", "-")


def read(path):
    return open(path, encoding="utf-8", errors="ignore").read()


def main():
    entries = []  # dicts: provider, account, value, sources(set), notes

    def add(provider, account, value, source, note=""):
        if not value or value.lower() in ("none", "null", "") or "your_api_key" in value.lower():
            return False
        for e in entries:
            if e["value"] == value:
                e["sources"].add(source)
                if account not in e["accounts"]:
                    e["accounts"].append(account)
                if note and note not in e["notes"]:
                    e["notes"].append(note)
                return True
        entries.append({
            "provider": norm_provider(provider),
            "accounts": [account],
            "value": value,
            "sources": {source},
            "notes": [note] if note else [],
        })
        return True

    # 1) OmniRoute master table -------------------------------------------------
    backup = read(os.path.join(CK, "my_api_keys_backup.md"))
    omni_rows = 0
    for line in backup.splitlines():
        m = TABLE_ROW.match(line.strip())
        if not m:
            continue
        provider, account, _auth, value = [x.strip() for x in m.groups()]
        if add(provider, account, value, "my_api_keys_backup.md"):
            omni_rows += 1

    # 2) key.txt -----------------------------------------------------------------
    for line in read(os.path.join(CK, "key.txt")).splitlines():
        mm = re.match(r"\s*Deep infra API KEY\s*:?\s*-?\s*(\S+)", line, re.I)
        if mm:
            add("DEEPINFRA", "key.txt entry", mm.group(1), "key.txt", "cross-check vs OmniRoute")
            continue
        mm = re.match(r"\s*Jina AI API\s*-?\s*(\S+)", line, re.I)
        if mm:
            add("JINA-AI", "key.txt entry", mm.group(1), "key.txt", "cross-check vs OmniRoute")
            continue
        mm = re.match(r"\s*Hyperbolic AI API\s*-?\s*(\S+)", line, re.I)
        if mm:
            add("HYPERBOLIC", "key.txt entry", mm.group(1), "key.txt", "cross-check vs OmniRoute")
            continue
        mm = re.match(r"\s*Cohere API\s*-?\s*(\S+)", line, re.I)
        if mm:
            add("COHERE", "key.txt entry", mm.group(1), "key.txt", "cross-check vs OmniRoute")

    # 3) test.env.txt ------------------------------------------------------------
    env_txt = read(os.path.join(CK, "test.env.txt"))
    for mm in re.finditer(r'Groq\(api_key="([^"]+)"\)', env_txt):
        add("GROQ", "test.env snippet", mm.group(1), "test.env.txt", "cross-check vs OmniRoute")
    for mm in re.finditer(r'Authorization":\s*f?"(hf_[^"]+)"', env_txt):
        add("HUGGINGFACE", "test.env snippet", mm.group(1), "test.env.txt", "cross-check vs OmniRoute")
    zai_block = re.search(r"#z\.ai(.*)$", env_txt, re.S | re.I)
    if zai_block:
        zb = zai_block.group(1)
        uid = re.search(r"User ID\s+(\S+)", zb)
        api_key_line = re.search(r"API key\s+(\S+)", zb)
        key_id = re.search(r"API Key ID\s+(\S+)", zb)
        if api_key_line:
            add("ZAI", "z.ai console record" + (f" (user {uid.group(1)})" if uid else ""),
                api_key_line.group(1), "test.env.txt",
                f"console Key ID {key_id.group(1) if key_id else '?'}")

    # 4) Firecrawl ----------------------------------------------------------------
    fc = read(os.path.join(CK, "Fiecrawal ai.txt"))
    for mm in re.finditer(r"(fc-[A-Za-z0-9\-_]{16,})", fc):
        add("FIRECRAWL", "Firecrawl MCP/CLI", mm.group(1), "Fiecrawal ai.txt")

    # 5) Google OAuth ---------------------------------------------------------------
    import glob as gmod
    for jp in gmod.glob(os.path.join(CK, "client_secret_*.json")):
        try:
            data = json.load(open(jp, encoding="utf-8"))
        except Exception:
            continue
        d = data.get("installed") or data.get("web") or data
        cid, csec = d.get("client_id", ""), d.get("client_secret", "")
        proj = d.get("project_id", "")
        if csec:
            add("GOOGLE-OAUTH", f"client secret ({proj})",
                csec, os.path.basename(jp), f"client_id={cid}")

    # 6) Tavily x2 ---------------------------------------------------------------
    tav = read(os.path.join("Raw_copies", "Tavily's AI.txt"))
    seen_tav = set()
    for mm in re.finditer(r"(tvly-[A-Za-z0-9\-_]{10,})", tav):
        if mm.group(1) not in seen_tav:
            seen_tav.add(mm.group(1))
            add("TAVILY", "Tavily's AI.txt", mm.group(1), "Raw_copies/Tavily's AI.txt")
    yt = read(os.path.join("Raw_copies", "YouTube_Content_Idea_Generator (1).json"))
    for mm in set(re.findall(r"(tvly-[A-Za-z0-9\-_]{10,})", yt)):
        add("TAVILY", "YouTube_Content_Idea_Generator n8n workflow", mm,
            "Raw_copies/YouTube_Content_Idea_Generator (1).json",
            "MISSING from previous registry - added 2026-08-23")

    # 7) Embedded keys in vault workflow JSONs ------------------------------------
    inv = json.load(open(INV_PATH, encoding="utf-8")) if os.path.exists(INV_PATH) else {}
    for item in inv.get("bare", {}).get("openai_style", []):
        src = item["source"]
        if "workflow" in src.lower() or ".json" in src.lower():
            add("OPENAI-STYLE-EMBEDDED", f"in {os.path.basename(src)}", item["value"], src,
                "embedded project key found during M5 audit")

    # ---- write registry ----------------------------------------------------------
    by_provider = {}
    for e in entries:
        by_provider.setdefault(e["provider"], []).append(e)

    L = []
    L.append("---")
    L.append('title: Master Credentials Registry')
    L.append('created_date: 2026-08-17')
    L.append('rebuilt_date: 2026-08-23')
    L.append('purpose: SINGLE authoritative private registry of ALL API keys/tokens with actual values.')
    L.append('policy: OWNER-ONLY. Never commit, share, print, or sync outside this machine.')
    L.append('gitignore: covered by 01_Vault_Private/ rule (.gitignore line 6)')
    L.append("---")
    L.append("")
    L.append("# Master Credentials Registry — FULL VALUES (OWNER ONLY)")
    L.append("")
    L.append("> [!DANGER]")
    L.append("> This file now contains REAL secret values (owner decision 2026-08-23).")
    L.append("> It lives only in the gitignored vault. Never paste its content into any")
    L.append("> chat, ticket, screenshot, or cloud sync folder. Rotate any key before it")
    L.append("> is ever used in anything public-facing.")
    L.append("")
    total = 0
    for prov in sorted(by_provider):
        items = by_provider[prov]
        total += len(items)
        L.append(f"## {prov} ({len(items)} account{'s' if len(items)>1 else ''})")
        L.append("")
        L.append("| Account | Value | Source(s) | Notes |")
        L.append("| :--- | :--- | :--- | :--- |")
        for e in items:
            acc = " / ".join(e["accounts"])
            srcs = ", ".join(sorted(e["sources"]))
            notes = "; ".join(n for n in e["notes"] if n)
            L.append(f"| {acc} | `{e['value']}` | {srcs} | {notes} |")
        L.append("")

    L.append("## 🔗 Cross-Reference Usage")
    L.append("")
    L.append("- **OmniRoute**: bulk of keys imported from its own export (`my_api_keys_backup.md`, 47 accounts configured).")
    L.append("- **MCP servers / CLI**: Firecrawl + Tavily keys configure remote MCP connections.")
    L.append("- **Python integrations**: Groq + HuggingFace keys appear in `test.env.txt` code snippets.")
    L.append("- **z.ai console**: user ID + key ID recorded alongside the key for portal management.")
    L.append("")
    L.append("## 🛡️ Security Notes")
    L.append("")
    L.append("- Vault (this file) is gitignored; test suite asserts it never enters git.")
    L.append("- Public-tier copies of documents that contained these keys were redacted in M5 security pass.")
    L.append("- Excel `AI_Lab_Credential_Manager_v2 (1).xlsx` still needs manual review (binary format).")
    L.append("- If any key below stops working, mark Status here and rotate via provider portal.")
    L.append("")

    open(REG_PATH, "w", encoding="utf-8").write("\n".join(L))

    # ---- verification report (masked) --------------------------------------------
    print(f"REGISTRY REBUILT -> {REG_PATH}")
    print(f"providers: {len(by_provider)} | unique secrets: {total}")
    dup_crosscheck = sum(1 for e in entries if len(e['sources']) > 1)
    print(f"secrets confirmed by 2+ independent sources: {dup_crosscheck}")
    print("\nPer-provider (masked):")
    for prov in sorted(by_provider):
        vals = {e["value"] for e in by_provider[prov]}
        print(f"  {prov}: {len(vals)} unique value(s)")
        for v in sorted(vals):
            print(f"     {mask(v)}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
