import fitz

def extract_text_from_pdf(pdf_path):
    """
    Extract text from a PDF file using PyMuPDF (fitz).
    
    Args:
        pdf_path (str): The path to the PDF file.
        
    Returns:
        str: The extracted text from the PDF.
    """
    pdf = fitz.open(pdf_path)
    extracted_text = ""

    for page_number, page in enumerate(pdf):
        text = page.get_text()
        extracted_text += f"{text}\n"  # Append the text of each page with a newline
    print(f"--------------Extracted text from {pdf_path} (Total pages: {len(pdf)}):--------------")

    pdf.close()
    return extracted_text

if __name__ == "__main__":
    # Test the PDF text extraction function with a sample PDF file
    pdf_path = "test/functionalsample.pdf"  # Replace with your PDF file path
    extracted_text = extract_text_from_pdf(pdf_path)
    print(extracted_text)