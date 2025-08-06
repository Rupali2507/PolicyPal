import PyPDF2
import os
from typing import Dict, List
from .chunker import TextChunker

class PDFExtractor:
    def __init__(self, data_folder: str = "data"):
        self.data_folder = data_folder
        self.chunker = TextChunker()
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from a single PDF"""
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page_num, page in enumerate(reader.pages):
                    page_text = page.extract_text()
                    if page_text.strip():
                        text += f"\n--- Page {page_num + 1} ---\n{page_text}"
                return text.strip()
        except Exception as e:
            print(f"Error extracting text from {pdf_path}: {e}")
            return ""
    
    def load_all_company_pdfs(self) -> Dict[str, Dict]:
        """Load all PDFs from data folder"""
        company_data = {}
        
        if not os.path.exists(self.data_folder):
            print(f"Creating {self.data_folder} folder...")
            os.makedirs(self.data_folder)
            return company_data
        
        pdf_files = [f for f in os.listdir(self.data_folder) if f.endswith('.pdf')]
        
        if not pdf_files:
            print(f"No PDF files found in {self.data_folder}/ folder")
            return company_data
        
        print(f"Loading {len(pdf_files)} company PDFs...")
        
        for filename in pdf_files:
            company_name = self._clean_company_name(filename)
            pdf_path = os.path.join(self.data_folder, filename)
            
            # Extract text
            full_text = self.extract_text_from_pdf(pdf_path)
            
            if full_text:
                # Create chunks
                chunks = self.chunker.create_chunks(full_text)
                
                company_data[company_name] = {
                    'filename': filename,
                    'full_text': full_text,
                    'chunks': chunks,
                    'chunk_count': len(chunks)
                }
                
                print(f"✓ {company_name}: {len(chunks)} chunks")
            else:
                print(f"✗ Failed to extract text from {filename}")
        
        return company_data
    
    def _clean_company_name(self, filename: str) -> str:
        """Clean filename to get company name"""
        return filename.replace('.pdf', '').replace('_', ' ').replace('-', ' ').title()