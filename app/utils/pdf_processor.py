"""
Utility for processing PDF files.
"""
import requests
import io
import os
from typing import Optional, List

# Try to import PyPDF2, which we'll add to requirements
try:
    import PyPDF2
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False

def extract_text_from_pdf_url(pdf_url: str) -> Optional[str]:
    """
    Download a PDF from a URL and extract its text content.
    
    Args:
        pdf_url (str): URL to the PDF file
        
    Returns:
        str: Extracted text from the PDF or None if extraction failed
    """
    if not PDF_SUPPORT:
        print("PyPDF2 not installed. Cannot extract text from PDFs.")
        return None
        
    try:
        # Download the PDF file
        response = requests.get(pdf_url)
        if response.status_code != 200:
            print(f"Failed to download PDF from {pdf_url}: {response.status_code}")
            return None
            
        # Read the PDF content
        pdf_file = io.BytesIO(response.content)
        reader = PyPDF2.PdfReader(pdf_file)
        
        # Extract text from all pages
        text = ""
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text += page.extract_text() + "\n\n"
            
        return text
    except Exception as e:
        print(f"Error extracting text from PDF {pdf_url}: {str(e)}")
        return None

def process_exam_materials(materials: List[str], max_chars: int = 10000) -> str:
    """
    Process a list of exam material URLs, extracting text from PDFs.
    
    Args:
        materials (List[str]): List of URLs to exam materials
        max_chars (int): Maximum characters to return
        
    Returns:
        str: Concatenated text from all materials, truncated to max_chars
    """
    if not materials:
        return ""
        
    extracted_text = []
    
    for material in materials:
        if material.lower().endswith('.pdf'):
            text = extract_text_from_pdf_url(material)
            if text:
                extracted_text.append(text)
        else:
            # For non-PDF materials, just add the URL as a reference
            extracted_text.append(f"Reference material: {material}")
    
    # Combine all extracted text
    combined_text = "\n\n".join(extracted_text)
    
    # Truncate if too long
    if len(combined_text) > max_chars:
        combined_text = combined_text[:max_chars] + "... (text truncated)"
        
    return combined_text 