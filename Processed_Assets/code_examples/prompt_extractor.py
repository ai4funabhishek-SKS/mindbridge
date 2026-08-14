import json
import re
import os
from datetime import datetime

def extract_prompts(content_file):
    """Extract prompts from the content file and categorize them."""
    with open(content_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract different types of prompts using regex patterns
    prompts = {
        'ai_tools': extract_ai_tool_prompts(content),
        'trading': extract_trading_prompts(content),
        'workflow': extract_workflow_prompts(content)
    }
    
    return prompts

def extract_ai_tool_prompts(content):
    """Extract AI tool-related prompts."""
    prompts = []
    # Look for sections discussing AI tools, LLMs, and system setups
    ai_sections = re.finditer(r'(?i)(?:system instructions?|prompt template|AI setup).*?(?=\n\n|$)', content, re.DOTALL)
    
    for section in ai_sections:
        prompt_text = section.group(0).strip()
        if len(prompt_text) > 50:  # Filter out too short matches
            prompts.append({
                'text': prompt_text,
                'category': 'ai_tools',
                'metadata': create_metadata('ai_tools')
            })
    
    return prompts

def extract_trading_prompts(content):
    """Extract trading-related prompts."""
    prompts = []
    # Look for sections about trading, market analysis, and stock advice
    trading_sections = re.finditer(r'(?i)(?:stock advisor|market analysis|trading bot).*?(?=\n\n|$)', content, re.DOTALL)
    
    for section in trading_sections:
        prompt_text = section.group(0).strip()
        if len(prompt_text) > 50:
            prompts.append({
                'text': prompt_text,
                'category': 'trading',
                'metadata': create_metadata('trading')
            })
    
    return prompts

def extract_workflow_prompts(content):
    """Extract workflow automation prompts."""
    prompts = []
    # Look for sections about workflows, automation, and processes
    workflow_sections = re.finditer(r'(?i)(?:workflow|automation|process flow).*?(?=\n\n|$)', content, re.DOTALL)
    
    for section in workflow_sections:
        prompt_text = section.group(0).strip()
        if len(prompt_text) > 50:
            prompts.append({
                'text': prompt_text,
                'category': 'workflow',
                'metadata': create_metadata('workflow')
            })
    
    return prompts

def create_metadata(category):
    """Create metadata for the prompt."""
    return {
        'creation_date': datetime.now().isoformat(),
        'version': '1.0',
        'category': category,
        'source': 'DeepSeek LLM Research',
        'author': 'Prompt Extractor'
    }

def save_prompts(prompts, base_dir):
    """Save extracted prompts to appropriate directories."""
    for category, category_prompts in prompts.items():
        category_dir = os.path.join(base_dir, 'sources', 'prompts', category)
        os.makedirs(category_dir, exist_ok=True)
        
        for i, prompt in enumerate(category_prompts, 1):
            filename = f"{category}_{i}_v1.md"
            filepath = os.path.join(category_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"# Original Context\n\n{prompt['text']}\n\n")
                f.write("# Extracted Prompt\n\n[Clean prompt text with variables marked]\n\n")
                f.write("# Usage Notes\n- Original purpose/context\n- Required inputs\n- Expected outputs\n\n")
                f.write(f"# Metadata\n```json\n{json.dumps(prompt['metadata'], indent=2)}\n```\n")

def main():
    content_file = 'c:/ai-stack/knowledge Base/my research/sources/processed/deepseek_content.txt'
    base_dir = 'c:/ai-stack/knowledge Base/my research'
    
    # Extract prompts from content
    prompts = extract_prompts(content_file)
    
    # Save prompts to appropriate directories
    save_prompts(prompts, base_dir)
    
    # Create a summary report
    summary = {
        'extraction_date': datetime.now().isoformat(),
        'prompt_counts': {category: len(prompts_list) for category, prompts_list in prompts.items()},
        'total_prompts': sum(len(prompts_list) for prompts_list in prompts.values())
    }
    
    with open(os.path.join(base_dir, 'sources', 'processed', 'prompt_extraction_summary.json'), 'w') as f:
        json.dump(summary, f, indent=2)

if __name__ == '__main__':
    main()