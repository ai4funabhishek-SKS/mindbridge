import json
import os
import time
import sys
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright

class UniversalLLMExtractor:
    def __init__(self, llm_name, base_url=None, conversation_selector=None):
        self.llm_name = llm_name
        self.base_url = base_url
        self.conversation_selector = conversation_selector
        self.output_dir = Path('c:/ai-stack/knowledge Base/my research/sources/raw_data')
        self.output_dir.mkdir(exist_ok=True)

    def extract_conversations(self):
        """Main extraction method"""
        start_time = datetime.now()
        print(f"\n[{start_time.strftime('%H:%M:%S')}] Initiating {self.llm_name} conversation extraction")

        try:
            playwright = sync_playwright().start()

            # Try to connect to existing Chrome session first
            try:
                print(f"\n[1/3] Attempting to connect to existing Chrome session...")
                browser = playwright.chromium.connect_over_cdp("http://localhost:9222")
                print("✓ Connected to existing Chrome session")
            except Exception as e:
                print(f"⚠️ No active Chrome session found: {str(e)}")
                print("Please ensure Chrome is running with remote debugging enabled")
                print("Run: chrome.exe --remote-debugging-port=9222")
                return None

            context = browser.new_context()
            page = context.new_page()

            # Navigate to the LLM interface
            if self.base_url:
                print(f'\n[2/3] Navigating to {self.llm_name}...')
                page.goto(self.base_url)
                time.sleep(3)

            # Extract conversations
            conversations = self._extract_conversation_data(page)

            # Save to file
            if conversations:
                output_file = self._save_conversations(conversations, start_time)
                print(f'\n✓ Successfully extracted {len(conversations)} conversations')
                print(f'Output saved to: {output_file}')
            else:
                print(f'\n⚠️ No conversations found for {self.llm_name}')

            browser.close()
            playwright.stop()

        except Exception as e:
            print(f"\n[ERROR] Extraction failed: {str(e)}")
            return None

    def _extract_conversation_data(self, page):
        """Extract conversation data - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement _extract_conversation_data")

    def _save_conversations(self, conversations, start_time):
        """Save conversations to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f'{self.llm_name.lower()}_conversations_{timestamp}.json'

        extraction_summary = {
            'conversations': conversations,
            'summary': {
                'llm_platform': self.llm_name,
                'total_conversations': len(conversations),
                'extraction_start': start_time.isoformat(),
                'extraction_end': datetime.now().isoformat(),
                'extraction_duration_seconds': (datetime.now() - start_time).total_seconds()
            }
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(extraction_summary, f, indent=2, ensure_ascii=False)

        return output_file

class ChatGPTExtractor(UniversalLLMExtractor):
    def __init__(self):
        super().__init__(
            llm_name="ChatGPT",
            base_url="https://chat.openai.com"
        )

    def _extract_conversation_data(self, page):
        conversations = []

        # Wait for ChatGPT interface to load
        try:
            page.wait_for_selector('[data-testid="conversation-list"]', timeout=10000)
        except:
            print("ChatGPT interface not detected. Please ensure you're logged in.")
            return conversations

        # Get conversation list
        conversation_items = page.query_selector_all('[data-testid="conversation-item"]')

        for item in conversation_items:
            try:
                title = item.text_content().strip()
                if not title:
                    title = "Untitled Chat"

                # Click to open conversation
                item.click()
                time.sleep(2)

                # Extract messages
                messages = []
                message_elements = page.query_selector_all('[data-message-id]')

                for msg_elem in message_elements:
                    role = "assistant" if "assistant" in msg_elem.get_attribute("class") else "user"
                    content = msg_elem.text_content().strip()

                    if content:
                        messages.append({
                            'role': role,
                            'content': content,
                            'timestamp': datetime.now().isoformat()
                        })

                if messages:
                    conversations.append({
                        'id': f"chatgpt_{len(conversations)}",
                        'title': title,
                        'thread': messages,
                        'source': 'chatgpt',
                        'export_date': datetime.now().isoformat(),
                        'url': page.url
                    })

            except Exception as e:
                print(f"Error extracting ChatGPT conversation: {str(e)}")
                continue

        return conversations

class GeminiExtractor(UniversalLLMExtractor):
    def __init__(self):
        super().__init__(
            llm_name="Gemini",
            base_url="https://gemini.google.com"
        )

    def _extract_conversation_data(self, page):
        conversations = []

        try:
            page.wait_for_selector('[data-testid="conversation-list"]', timeout=10000)
        except:
            print("Gemini interface not detected. Please ensure you're logged in.")
            return conversations

        conversation_items = page.query_selector_all('[data-testid="conversation-item"]')

        for item in conversation_items:
            try:
                title = item.text_content().strip() or "Untitled Gemini Chat"
                item.click()
                time.sleep(2)

                messages = []
                message_elements = page.query_selector_all('[data-message-role]')

                for msg_elem in message_elements:
                    role = msg_elem.get_attribute('data-message-role')
                    content = msg_elem.text_content().strip()

                    if content:
                        messages.append({
                            'role': role,
                            'content': content,
                            'timestamp': datetime.now().isoformat()
                        })

                if messages:
                    conversations.append({
                        'id': f"gemini_{len(conversations)}",
                        'title': title,
                        'thread': messages,
                        'source': 'gemini',
                        'export_date': datetime.now().isoformat(),
                        'url': page.url
                    })

            except Exception as e:
                print(f"Error extracting Gemini conversation: {str(e)}")
                continue

        return conversations

class CopilotExtractor(UniversalLLMExtractor):
    def __init__(self):
        super().__init__(
            llm_name="Copilot",
            base_url="https://copilot.microsoft.com"
        )

    def _extract_conversation_data(self, page):
        conversations = []

        try:
            page.wait_for_selector('[data-testid="conversation-list"]', timeout=10000)
        except:
            print("Copilot interface not detected. Please ensure you're logged in.")
            return conversations

        conversation_items = page.query_selector_all('[data-testid="conversation-item"]')

        for item in conversation_items:
            try:
                title = item.text_content().strip() or "Untitled Copilot Chat"
                item.click()
                time.sleep(2)

                messages = []
                message_elements = page.query_selector_all('[data-message-role]')

                for msg_elem in message_elements:
                    role = "assistant" if "bot" in msg_elem.get_attribute("class").lower() else "user"
                    content = msg_elem.text_content().strip()

                    if content:
                        messages.append({
                            'role': role,
                            'content': content,
                            'timestamp': datetime.now().isoformat()
                        })

                if messages:
                    conversations.append({
                        'id': f"copilot_{len(conversations)}",
                        'title': title,
                        'thread': messages,
                        'source': 'copilot',
                        'export_date': datetime.now().isoformat(),
                        'url': page.url
                    })

            except Exception as e:
                print(f"Error extracting Copilot conversation: {str(e)}")
                continue

        return conversations

def main():
    if len(sys.argv) < 2:
        print("Usage: python universal_llm_extractor.py <llm_name>")
        print("Available LLMs: chatgpt, gemini, copilot, perplexity, groq, google_aistudio")
        return

    llm_name = sys.argv[1].lower()

    extractors = {
        'chatgpt': ChatGPTExtractor,
        'gemini': GeminiExtractor,
        'copilot': CopilotExtractor,
    }

    if llm_name not in extractors:
        print(f"Unsupported LLM: {llm_name}")
        print("Available LLMs: chatgpt, gemini, copilot")
        return

    extractor = extractors[llm_name]()
    extractor.extract_conversations()

if __name__ == '__main__':
    main()
