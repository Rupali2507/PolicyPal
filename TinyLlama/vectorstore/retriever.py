from typing import List, Dict, Tuple
import numpy as np
from pdfutils.chunker import TextChunker

class SimpleRetriever:
    """Simple keyword-based retriever. Can be upgraded to use embeddings later"""
    
    def __init__(self):
        self.chunker = TextChunker()
    
    def retrieve_contexts(self, 
                         question: str, 
                         company_data: Dict, 
                         company_name: str = None,
                         top_k: int = 2) -> List[Tuple[str, str]]:
        """
        Retrieve relevant contexts for question
        Returns: List of (company_name, context) tuples
        """
        results = []
        
        if company_name and company_name in company_data:
            # Query specific company
            chunks = company_data[company_name]['chunks']
            relevant_chunks = self.chunker.find_relevant_chunks(question, chunks, top_k)
            for chunk in relevant_chunks:
                results.append((company_name, chunk))
        else:
            # Query all companies
            for comp_name, comp_data in company_data.items():
                chunks = comp_data['chunks']
                relevant_chunks = self.chunker.find_relevant_chunks(question, chunks, 1)  # 1 chunk per company
                for chunk in relevant_chunks:
                    results.append((comp_name, chunk))
        
        return results