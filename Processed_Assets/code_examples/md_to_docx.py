from docx import Document
import markdown
import os

def convert_md_to_docx(md_file_path, docx_file_path):
    # Read markdown content
    with open(md_file_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Convert markdown to HTML
    html_content = markdown.markdown(md_content)
    
    # Create a new Word document
    doc = Document()
    
    # Add title
    doc.add_heading('DeepSeek LLM Research Analysis Report', 0)
    
    # Split content by sections and add to document
    sections = html_content.split('<h2>')
    
    for section in sections[1:]:  # Skip the first empty section
        # Split section into title and content
        title, content = section.split('</h2>', 1)
        
        # Add section heading
        doc.add_heading(title, level=1)
        
        # Add content paragraphs
        paragraphs = content.split('<p>')
        for p in paragraphs:
            if p.strip():
                # Remove HTML tags
                clean_text = p.replace('</p>', '').replace('<code>', '').replace('</code>', '')
                doc.add_paragraph(clean_text)
    
    # Save the document
    doc.save(docx_file_path)
    print(f'Successfully converted {md_file_path} to {docx_file_path}')

# File paths
md_file = os.path.join('sources', 'processed', 'final_report.md')
docx_file = os.path.join('sources', 'processed', 'DeepSeek_LLM_Research_Report.docx')

# Convert markdown to docx
convert_md_to_docx(md_file, docx_file)