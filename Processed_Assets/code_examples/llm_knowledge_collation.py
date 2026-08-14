#!/usr/bin/env python3
"""
LLM Knowledge Collation System
Collates conversations from multiple LLM platforms into a unified knowledge base
"""

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright

class LLMKnowledgeCollator:
    def __init__(self):
        self.base_dir = Path('c:/ai-stack/knowledge Base/my research')
        self.raw_data_dir = self.base_dir / 'sources' / 'raw_data'
        self.personal_dir = self.base_dir / 'sources' / 'personal'
        self.processed_dir = self.base_dir / 'sources' / 'processed'

        # Ensure directories exist
        self.raw_data_dir.mkdir(parents=True, exist_ok=True)
        self.personal_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)

        # LLM configurations
        self.llm_configs = {
            'chatgpt': {
                'name': 'ChatGPT',
                'url': 'https://chat.openai.com',
                'selectors': {
                    'conversation_list': '[data-testid="conversation-list"]',
                    'conversation_item': '[data-testid="conversation-item"]',
                    'message': '[data-message-id]'
                }
            },
            'gemini': {
                'name': 'Gemini',
                'url': 'https://gemini.google.com',
                'selectors': {
                    'conversation_list': '[data-testid="conversation-list"]',
                    'conversation_item': '[data-testid="conversation-item"]',
                    'message': '[data-message-role]'
                }
            },
            'copilot': {
                'name': 'Copilot',
                'url': 'https://copilot.microsoft.com',
                'selectors': {
                    'conversation_list': '[data-testid="conversation-list"]',
                    'conversation_item': '[data-testid="conversation-item"]',
                    'message': '[data-message-role]'
                }
            },
            'perplexity': {
                'name': 'Perplexity',
                'url': 'https://www.perplexity.ai',
                'selectors': {
                    'conversation_list': '.conversation-list',
                    'conversation_item': '.conversation-item',
                    'message': '.message'
                }
            },
            'groq': {
                'name': 'Groq',
                'url': 'https://groq.com',
                'selectors': {
                    'conversation_list': '[data-testid="chat-list"]',
                    'conversation_item': '[data-testid="chat-item"]',
                    'message': '[data-testid="message"]'
                }
            },
            'google_aistudio': {
                'name': 'Google AI Studio',
                'url': 'https://aistudio.google.com',
                'selectors': {
                    'conversation_list': '.conversation-list',
                    'conversation_item': '.conversation-item',
                    'message': '.message'
                }
            }
        }

    def check_chrome_session(self):
        """Check if Chrome is running with remote debugging"""
        try:
            playwright = sync_playwright().start()
            browser = playwright.chromium.connect_over_cdp("http://localhost:9222")
            print("✓ Connected to Chrome session")
            browser.close()
            playwright.stop()
            return True
        except Exception as e:
            print(f"⚠️ Chrome remote debugging not available: {str(e)}")
            print("Please start Chrome with: chrome.exe --remote-debugging-port=9222")
            return False

    def extract_llm_conversations(self, llm_name):
        """Extract conversations from a specific LLM"""
        if llm_name not in self.llm_configs:
            print(f"❌ Unsupported LLM: {llm_name}")
            return None

        config = self.llm_configs[llm_name]
        print(f"\n🔄 Extracting conversations from {config['name']}...")

        try:
            playwright = sync_playwright().start()
            browser = playwright.chromium.connect_over_cdp("http://localhost:9222")
            context = browser.new_context()
            page = context.new_page()

            # Navigate to LLM interface
            print(f"🌐 Navigating to {config['url']}")
            page.goto(config['url'])
            time.sleep(5)

            # Wait for interface to load
            try:
                page.wait_for_selector(config['selectors']['conversation_list'], timeout=15000)
                print("✓ Interface loaded successfully")
            except:
                print(f"⚠️ Could not detect {config['name']} interface. Please ensure you're logged in.")
                browser.close()
                playwright.stop()
                return None

            # Extract conversations
            conversations = self._extract_conversation_data(page, config)

            if conversations:
                # Save to JSON
                json_file = self._save_conversations_json(conversations, config)
                print(f"✓ Extracted {len(conversations)} conversations from {config['name']}")

                # Convert to DOCX
                docx_file = self._convert_to_docx(json_file, config)
                print(f"✓ Created DOCX: {docx_file}")

                browser.close()
                playwright.stop()
                return {'json': json_file, 'docx': docx_file}
            else:
                print(f"⚠️ No conversations found for {config['name']}")
                browser.close()
                playwright.stop()
                return None

        except Exception as e:
            print(f"❌ Error extracting from {config['name']}: {str(e)}")
            return None

    def _extract_conversation_data(self, page, config):
        """Extract conversation data from the page"""
        conversations = []

        try:
            # Get conversation list
            conversation_items = page.query_selector_all(config['selectors']['conversation_item'])

            if not conversation_items:
                print("No conversation items found")
                return conversations

            print(f"Found {len(conversation_items)} conversations")

            for i, item in enumerate(conversation_items[:10]):  # Limit to first 10 for testing
                try:
                    # Get conversation title
                    title = item.text_content().strip()
                    if not title:
                        title = f"Conversation {i+1}"

                    print(f"Processing: {title}")

                    # Click to open conversation
                    item.click()
                    time.sleep(3)

                    # Extract messages
                    messages = []
                    message_elements = page.query_selector_all(config['selectors']['message'])

                    for msg_elem in message_elements:
                        try:
                            # Determine role based on LLM
                            if config['name'] == 'ChatGPT':
                                role = "assistant" if "assistant" in msg_elem.get_attribute("class", "") else "user"
                            elif config['name'] == 'Gemini':
                                role = msg_elem.get_attribute('data-message-role', 'user')
                            elif config['name'] == 'Copilot':
                                role = "assistant" if "bot" in msg_elem.get_attribute("class", "").lower() else "user"
                            else:
                                role = "assistant" if "assistant" in msg_elem.get_attribute("class", "").lower() else "user"

                            content = msg_elem.text_content().strip()

                            if content:
                                messages.append({
                                    'role': role,
                                    'content': content,
                                    'timestamp': datetime.now().isoformat()
                                })

                        except Exception as e:
                            print(f"Error extracting message: {str(e)}")
                            continue

                    if messages:
                        conversations.append({
                            'id': f"{llm_name.lower()}_{i+1}",
                            'title': title,
                            'thread': messages,
                            'source': llm_name.lower(),
                            'export_date': datetime.now().isoformat(),
                            'url': page.url
                        })

                except Exception as e:
                    print(f"Error processing conversation: {str(e)}")
                    continue

        except Exception as e:
            print(f"Error extracting conversations: {str(e)}")

        return conversations

    def _save_conversations_json(self, conversations, config):
        """Save conversations to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{config['name'].lower()}_conversations_{timestamp}.json"
        filepath = self.raw_data_dir / filename

        data = {
            'conversations': conversations,
            'summary': {
                'llm_platform': config['name'],
                'total_conversations': len(conversations),
                'extraction_date': datetime.now().isoformat()
            }
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return filepath

    def _convert_to_docx(self, json_file, config):
        """Convert JSON to DOCX using the converter script"""
        try:
            # Import the converter function
            sys.path.append(str(self.base_dir / 'sources' / 'code_examples'))
            from json_to_docx_converter import convert_json_to_docx

            docx_filename = json_file.stem + '.docx'
            docx_path = self.raw_data_dir / docx_filename

            convert_json_to_docx(json_file, docx_path)
            return docx_path

        except Exception as e:
            print(f"Error converting to DOCX: {str(e)}")
            return None

    def collate_all_llms(self, llm_list=None):
        """Extract conversations from all specified LLMs"""
        if llm_list is None:
            llm_list = list(self.llm_configs.keys())

        print("🚀 Starting LLM Knowledge Collation Process")
        print("=" * 50)

        # Check Chrome session
        if not self.check_chrome_session():
            print("❌ Please start Chrome with remote debugging and try again.")
            return

        results = {}

        for llm in llm_list:
            result = self.extract_llm_conversations(llm)
            if result:
                results[llm] = result
            time.sleep(2)  # Brief pause between extractions

        # Generate summary report
        self._generate_summary_report(results)

        print("\n✅ Knowledge collation process complete!")
        print(f"📁 Files saved to: {self.raw_data_dir}")

        return results

    def _generate_summary_report(self, results):
        """Generate a summary report of the collation process"""
        report_path = self.processed_dir / f"llm_collation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# LLM Knowledge Collation Report\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write("## Summary\n\n")
            f.write(f"- **Total LLMs Processed:** {len(results)}\n")
            f.write(f"- **Successful Extractions:** {len([r for r in results.values() if r is not None])}\n\n")

            f.write("## Extracted Conversations\n\n")
            for llm, result in results.items():
                if result:
                    json_file = result.get('json', 'N/A')
                    docx_file = result.get('docx', 'N/A')
                    f.write(f"### {llm.upper()}\n")
                    f.write(f"- **JSON:** {json_file}\n")
                    f.write(f"- **DOCX:** {docx_file}\n\n")

            f.write("## Next Steps\n\n")
            f.write("1. Review the extracted conversations in the DOCX files\n")
            f.write("2. Use the content processing pipeline for further analysis\n")
            f.write("3. Integrate insights into your knowledge base MOCs\n")

        print(f"📋 Summary report saved to: {report_path}")

def main():
    collator = LLMKnowledgeCollator()

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python llm_knowledge_collation.py <llm_name>")
        print("  python llm_knowledge_collation.py --all")
        print("\nAvailable LLMs:")
        for llm in collator.llm_configs.keys():
            print(f"  - {llm}")
        return

    if sys.argv[1] == '--all':
        collator.collate_all_llms()
    else:
        llm_name = sys.argv[1].lower()
        collator.extract_llm_conversations(llm_name)

if __name__ == '__main__':
    main()
