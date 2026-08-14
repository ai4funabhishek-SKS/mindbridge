# LLM Knowledge Collation System

This system allows you to extract conversations from multiple LLM platforms and collate them into your knowledge base.

## Supported LLMs

- **ChatGPT** (chat.openai.com)
- **Gemini** (gemini.google.com)
- **Copilot** (copilot.microsoft.com)
- **Perplexity** (perplexity.ai)
- **Groq** (groq.com)
- **Google AI Studio** (aistudio.google.com)

## Prerequisites

1. **Chrome Browser** with remote debugging enabled
2. **Python dependencies** installed (playwright, python-docx)
3. **Logged into your LLM accounts** in Chrome

## Setup Instructions

### 1. Start Chrome with Remote Debugging

Open Command Prompt or PowerShell and run:

```bash
chrome.exe --remote-debugging-port=9222
```

### 2. Log into Your LLM Accounts

In the Chrome window that opens:
1. Navigate to each LLM platform
2. Log in to your accounts
3. Keep the tabs open

### 3. Install Dependencies (if needed)

```bash
pip install playwright python-docx
```

## Usage

### Extract from a Single LLM

```bash
python sources/code_examples/llm_knowledge_collation.py chatgpt
```

Replace `chatgpt` with any supported LLM: `gemini`, `copilot`, `perplexity`, `groq`, `google_aistudio`

### Extract from All LLMs

```bash
python sources/code_examples/llm_knowledge_collation.py --all
```

## Output Files

The system creates two files for each LLM in `sources/raw_data/`:

1. **JSON file**: Raw conversation data
   - Format: `{llm_name}_conversations_{timestamp}.json`

2. **DOCX file**: Formatted document
   - Format: `{llm_name}_conversations_{timestamp}.docx`

## File Structure

```
sources/raw_data/
├── chatgpt_conversations_20241209_123000.json
├── chatgpt_conversations_20241209_123000.docx
├── gemini_conversations_20241209_123005.json
├── gemini_conversations_20241209_123005.docx
└── ...

sources/processed/
└── llm_collation_report_20241209_123010.md
```

## Troubleshooting

### Chrome Connection Issues

If you see "Chrome remote debugging not available":
1. Close all Chrome windows
2. Run: `chrome.exe --remote-debugging-port=9222`
3. Try the extraction again

### LLM Interface Not Detected

If extraction fails:
1. Ensure you're logged into the LLM platform
2. Make sure the conversation list is visible
3. Try refreshing the page
4. Check if the LLM has updated their interface

### Permission Issues

If you get permission errors:
1. Run Command Prompt as Administrator
2. Or use PowerShell with execution policy bypass

## Integration with Knowledge Base

After extraction, the DOCX files can be:

1. **Moved to `sources/personal/`** for personal conversations
2. **Processed using existing pipeline** (`content_processor.py`)
3. **Integrated into MOCs** for knowledge organization

## Advanced Usage

### Custom Selectors

If LLM interfaces change, update selectors in `llm_knowledge_collation.py`:

```python
'llm_name': {
    'name': 'LLM Display Name',
    'url': 'https://llm.url',
    'selectors': {
        'conversation_list': 'css_selector_for_list',
        'conversation_item': 'css_selector_for_item',
        'message': 'css_selector_for_message'
    }
}
```

### Batch Processing

For automated processing, create a scheduled task:

```bash
# Windows Task Scheduler
schtasks /create /tn "LLM Collation" /tr "python c:\path\to\llm_knowledge_collation.py --all" /sc daily /st 02:00
```

## Security Notes

- Conversations are saved locally only
- No data is transmitted to external servers
- Chrome remote debugging provides secure local access
- Review extracted content before sharing

## Support

If you encounter issues:

1. Check the console output for error messages
2. Verify Chrome is running with debugging enabled
3. Ensure you're logged into the LLM platforms
4. Try extracting from one LLM at a time for debugging
