import docx
import pypdf
import os

def extract_text_from_file(file_path):
    """
    Extract text from PDF or DOCX files.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        str: Extracted text content
    """
    if not os.path.exists(file_path):
        return "File not found."
    
    try:
        if file_path.lower().endswith('.docx'):
            doc = docx.Document(file_path)
            text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
            return text if text.strip() else "No text found in document."
            
        elif file_path.lower().endswith('.pdf'):
            with open(file_path, "rb") as f:
                reader = pypdf.PdfReader(f)
                text_pages = []
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_pages.append(page_text)
                
                full_text = "\n".join(text_pages)
                return full_text if full_text.strip() else "No text found in PDF."
                
        else:
            return "Unsupported file format. Please use PDF or DOCX."
            
    except Exception as e:
        return f"Error extracting text: {str(e)}"