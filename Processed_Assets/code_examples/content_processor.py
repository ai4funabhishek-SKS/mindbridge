import json
import re
from pathlib import Path

def extract_sections(content):
    sections = {
        'summaries': [],
        'prompts': [],
        'code_examples': [],
        'flowcharts': [],
        'troubleshooting': [],
        'best_practices': [],
        'learnings': []
    }
    
    # Extract sections using regex patterns
    sections['summaries'] = re.findall(r'(?:^|\n)(?:Summary|Overview):?[^\n]+(?:\n(?! *(?:Summary|Overview):)[^\n]+)*', content)
    sections['prompts'] = re.findall(r'(?:^|\n)(?:Prompt|Template):?[^\n]+(?:\n(?! *(?:Prompt|Template):)[^\n]+)*', content)
    sections['code_examples'] = re.findall(r'```[^`]+```', content)
    sections['troubleshooting'] = re.findall(r'(?:^|\n)(?:Troubleshooting|Error|Fix):?[^\n]+(?:\n(?! *(?:Troubleshooting|Error|Fix):)[^\n]+)*', content)
    sections['best_practices'] = re.findall(r'(?:^|\n)(?:Best Practice|Tip|Recommendation):?[^\n]+(?:\n(?! *(?:Best Practice|Tip|Recommendation):)[^\n]+)*', content)
    sections['learnings'] = re.findall(r'(?:^|\n)(?:Learning|Lesson|Note):?[^\n]+(?:\n(?! *(?:Learning|Lesson|Note):)[^\n]+)*', content)
    
    return sections

def process_content():
    input_path = Path('c:/ai-stack/knowledge Base/my research/sources/processed/deepseek_content.txt')
    output_dir = Path('c:/ai-stack/knowledge Base/my research/sources/processed')
    
    # Read content
    content = input_path.read_text(encoding='utf-8')
    
    # Extract sections
    sections = extract_sections(content)
    
    # Save organized content
    organized_path = output_dir / 'organized_content.json'
    with open(organized_path, 'w', encoding='utf-8') as f:
        json.dump(sections, f, indent=2)
    
    # Create markdown summary
    markdown = []
    markdown.append('# DeepSeek Conversation Analysis')
    markdown.append('\n## Table of Contents')
    for section in sections:
        markdown.append(f'- [{section.title()}](#{section})')
    
    for section, items in sections.items():
        markdown.append(f'\n## {section.title()}')
        for i, item in enumerate(items, 1):
            markdown.append(f'\n### {i}. {item[:100]}...' if len(item) > 100 else f'\n### {i}. {item}')
    
    markdown_path = output_dir / 'analysis.md'
    with open(markdown_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(markdown))
    
    print(f'Content processed and saved to:\n- {organized_path}\n- {markdown_path}')

if __name__ == '__main__':
    process_content()