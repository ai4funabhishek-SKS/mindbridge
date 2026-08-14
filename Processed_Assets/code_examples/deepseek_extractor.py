from playwright.sync_api import sync_playwright
import json
from datetime import datetime
import os
import time
import sys
import re
from tqdm import tqdm

def extract_conversations():
    # Initialize progress tracking
    start_time = datetime.now()
    print(f"\n[{start_time.strftime('%H:%M:%S')}] Initiating DeepSeek conversation extraction")
    print("Status: Extraction process starting...")
    
    try:
        # Initialize Playwright outside the with block to avoid event loop issues
        playwright = sync_playwright().start()
        
        # Chrome session management
        active_session = False
        try:
            print("\n[1/4] Checking for active Chrome sessions...")
            browser = playwright.chromium.connect_over_cdp("http://localhost:9222")
            print("✓ Connected to existing Chrome session")
            active_session = True
        except Exception as e:
            print(f"⚠️ No active Chrome session found: {str(e)}")
            print("\n[1/4] Launching new Chrome instance with debugging...")
            print("Please ensure Chrome is closed or approve new browser window")
            browser = playwright.chromium.launch(
                headless=False,
                args=["--remote-debugging-port=9222"]
            )
            active_session = False

        # Session conflict check
        if not active_session:
            print("\n⚠️ Warning: New browser instance created")
            print("If this conflicts with existing sessions, press Ctrl+C to abort")
            time.sleep(2)
        
        context = browser.new_context()
        page = context.new_page()
        
        # Attach to existing DeepSeek session
        target_url = 'https://chat.deepseek.com/a/chat/s/260d07ba-1383-4d25-9f3b-e638ef03409d'
        print(f'\n[2/4] Attaching to existing chat: {target_url}')
        
        # Check if already on target page
        if page.url != target_url:
            print('Navigating to specified conversation...')
            page.goto(target_url)
        else:
            print('Already on target conversation page')
        
        # Check if we need authentication
        print('Checking authentication status...')
        time.sleep(3)  # Give page time to load
        
        # Check if login is required
        login_button = page.query_selector('button:has-text("Sign In"), button:has-text("Log In")')
        if login_button:
            print('Authentication required. Please log in to DeepSeek.')
            print('Please open the browser window that appeared, log in to DeepSeek,')
            print('and navigate to the chat interface.')
            print('Press Enter when you have successfully logged in...')
            input()
        else:
            print('Already authenticated or no login required.')
        
        # Estimate completion time
        print('\nEstimating task size...')
        print('This process may take several minutes depending on the volume of conversations.')
        print('A progress bar will be displayed once extraction begins.\n')
        
        # Wait for the main chat interface to load with more flexible selectors
        print('Waiting for chat interface to load...')
        try:
            # Try different selectors that might indicate the chat interface is loaded
            selectors = [
                f'a[href="/a/chat/s/260d07ba-1383-4d25-9f3b-e638ef03409d"]',
            'div[data-testid="conversation-panel"]',
            'div[class*="MessageList__message"]',
            'div[role="log"]',
            'div[class*="ChatLayout__content"]'
            ]
            
            for selector in selectors:
                try:
                    print(f"Trying to locate element with selector: {selector}")
                    if page.wait_for_selector(selector, timeout=15000):
                        print(f"Found element with selector: {selector}")
                        break
                except Exception as e:
                    print(f"Selector '{selector}' not found: {str(e)}")
                    continue
            
            # Additional wait to ensure dynamic content loads
            print("Waiting for dynamic content to load...")
            time.sleep(5)
        except Exception as e:
            print(f"Warning: Could not detect chat interface using standard selectors: {str(e)}")
            print("Continuing anyway - please ensure you're on the DeepSeek chat page")
            time.sleep(5)  # Give more time for page to load
        
        # Extract conversations from the sidebar
        print('Extracting conversations...')
        conversations = []
        total_messages = 0
        
        # Find all conversation items in the sidebar
        sidebar = page.query_selector('nav')
        if not sidebar:
            print('Could not find conversation sidebar. Please make sure you are logged in.')
            return
        
        sidebar_items = sidebar.query_selector_all('a[href^="/chat"]')
        if not sidebar_items:
            print('No conversations found in the sidebar. Please make sure you have some chat history.')
            return
            
        # Progress tracking setup
        conversation_count = len(sidebar_items)
        avg_time_per_conv = 8.5  # Base seconds per conversation
        est_total_time = conversation_count * avg_time_per_conv
        
        print(f"\n[2/4] Found {conversation_count} conversations")
        print(f"Estimated extraction time: {est_total_time//60}min {int(est_total_time%60)}sec")
        print(f"Progress updates every 10% completion (~{conversation_count//10} conversations)")
        
        progress_bar = tqdm(
            total=conversation_count,
            desc="Extracting",
            unit="conv",
            bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]'
        )
        
        for item in sidebar_items:
            try:
                # Click on each conversation to load its content
                item.click()
                time.sleep(2)  # Wait for conversation to load
                
                # Get conversation title and creation date
                title = item.text_content().strip()
                if not title:
                    title = 'Untitled'
                    
                # Try to extract date from the conversation item
                date_element = item.query_selector('div[class*="text-xs"]')
                creation_date = None
                if date_element:
                    date_text = date_element.text_content().strip()
                    # Try to parse common date formats
                    try:
                        # Extract date patterns like "Jan 1, 2023" or "2023-01-01"
                        date_match = re.search(r'\d{4}-\d{2}-\d{2}|\w{3}\s\d{1,2},\s\d{4}', date_text)
                        if date_match:
                            creation_date = date_match.group(0)
                    except:
                        pass
                
                # Get conversation ID
                conv_id = item.get_attribute('href').split('/')[-1] or str(len(conversations))
                
                conversation = {
                    'id': conv_id,
                    'title': title,
                    'thread': [],
                    'source': 'deepseek',
                    'export_date': datetime.now().isoformat(),
                    'creation_date': creation_date,
                    'url': f"https://deepseek.com/chat/{conv_id}",
                    'metadata': {
                        'extraction_tool': 'deepseek_extractor.py',
                        'extraction_version': '1.1',
                        'browser': 'Chrome',
                        'platform': 'DeepSeek Chat'
                    }
                }
                
                # Extract messages from the main chat area
                chat_container = page.query_selector('div[role="main"]')
                if chat_container:
                    messages = chat_container.query_selector_all('div[role="listitem"]')
                    for msg in messages:
                        try:
                            # Determine message role and participant details
                            avatar = msg.query_selector('img[alt*="avatar"]')
                            
                            # Default role
                            role = 'user'
                            participant = 'User'
                            
                            # Check if it's the assistant
                            if avatar and 'assistant' in avatar.get_attribute('alt').lower():
                                role = 'assistant'
                                participant = 'DeepSeek AI'
                            
                            # Try to get timestamp
                            timestamp = None
                            time_element = msg.query_selector('div[class*="text-xs"], span[class*="text-xs"]')
                            if time_element:
                                time_text = time_element.text_content().strip()
                                if time_text:
                                    timestamp = time_text
                            
                            if not timestamp:
                                timestamp = datetime.now().isoformat()
                            
                            # Get message content
                            content_parts = []
                            
                            # Get text content
                            text_content = msg.query_selector('div[class*="whitespace-pre-wrap"]')
                            if text_content:
                                content_parts.append(text_content.text_content().strip())
                            
                            # Get code blocks
                            code_blocks = msg.query_selector_all('pre code')
                            for code in code_blocks:
                                content_parts.append(f"```\n{code.text_content().strip()}\n```")
                            
                            content = '\n\n'.join(filter(None, content_parts))
                            
                            if content:  # Only add messages with content
                                # Extract any model information if available
                                model_info = None
                                model_element = msg.query_selector('div[class*="text-xs"] span:has-text("Model:")')
                                if model_element:
                                    model_info = model_element.text_content().replace('Model:', '').strip()
                                
                                message_id = f"{conversation['id']}_{len(conversation['thread'])}"
                                
                                conversation['thread'].append({
                                    'role': role,
                                    'content': content,
                                    'participant': participant,
                                    'message_id': message_id,
                                    'metadata': {
                                        'timestamp': timestamp,
                                        'context_id': message_id,
                                        'memory_reference': f"deepseek_{conversation['id']}",
                                        'model': model_info,
                                        'index_in_thread': len(conversation['thread'])
                                    }
                                })
                                
                                total_messages += 1
                        except Exception as e:
                            print(f'Error extracting message: {str(e)}')
                            continue
                
                if conversation['thread']:  # Only add conversations with messages
                    conversations.append(conversation)
                    progress_bar.set_postfix(messages=len(conversation["thread"]), title=title[:20])
                
                # Progress reporting
                progress_bar.update(1)
                if progress_bar.n % max(1, conversation_count//10) == 0:
                    elapsed = time.time() - start_time.timestamp()
                    remaining = (conversation_count - progress_bar.n) * (elapsed/progress_bar.n)
                    print(f"\nProgress: {progress_bar.n}/{conversation_count} "
                          f"({progress_bar.n/conversation_count:.0%})\n"
                          f"Elapsed: {timedelta(seconds=int(elapsed))} • "
                          f"Remaining: ~{timedelta(seconds=int(remaining))}")
                
            except Exception as e:
                print(f'\nError processing conversation: {str(e)}')
                continue
        
        # Close progress bar
        progress_bar.close()
        
        # Save to file
        output_dir = r'C:\ai-stack\knowledge Base\my research\sources\raw_data'
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(output_dir, f'deepseek_conversations_{timestamp}.json')
        
        # Add summary statistics
        extraction_summary = {
            'conversations': conversations,
            'summary': {
                'total_conversations': len(conversations),
                'total_messages': total_messages,
                'extraction_start': start_time.isoformat(),
                'extraction_end': datetime.now().isoformat(),
                'extraction_duration_seconds': (datetime.now() - start_time).total_seconds()
            }
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(extraction_summary, f, indent=2, ensure_ascii=False)
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        print(f'\n[{end_time.strftime("%H:%M:%S")}] Extraction completed successfully!')
        print(f'Extracted {len(conversations)} conversations with {total_messages} messages')
        print(f'Output saved to: {output_file}')
        print(f'Total extraction time: {duration.total_seconds():.2f} seconds')
        
        # Properly close browser and playwright
        browser.close()
        playwright.stop()
    except Exception as e:
        print(f"\n[ERROR] Extraction failed: {str(e)}")
        print("Please check if DeepSeek is accessible and try again.")
        # Make sure to close playwright if it was initialized
        if 'playwright' in locals():
            try:
                playwright.stop()
            except:
                pass
        return None

if __name__ == '__main__':
    extract_conversations()