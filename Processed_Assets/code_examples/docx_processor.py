import docx
import json
import os

def extract_docx_content(docx_path):
    doc = docx.Document(docx_path)
    content = []
    
    for para in doc.paragraphs:
        if para.text.strip():
            content.append(para.text)
    
    return '\n'.join(content)

def process_document():
    input_path = 'c:/ai-stack/knowledge Base/my research/sources/raw_data/DeepSeek-LLM research threads- AAG01.docx'
    output_dir = 'c:/ai-stack/knowledge Base/my research/sources/processed'
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Extract content
    content = extract_docx_content(input_path)
    
    # Save as text file
    txt_path = os.path.join(output_dir, 'deepseek_content.txt')
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f'Content extracted and saved to {txt_path}')

if __name__ == '__main__':
    process_document()