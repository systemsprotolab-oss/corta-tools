from pypdf import PdfReader

reader = PdfReader("3 pages.pdf")
for page in reader.pages:
    
    print(page.extract_text())
