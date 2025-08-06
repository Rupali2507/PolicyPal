from typing import List

class TextChunker:
    def __init__(self, chunk_size: int = 800, overlap: int = 100):
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def create_chunks(self, text: str) -> List[str]:
        """Create overlapping chunks from text"""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), self.chunk_size - self.overlap):
            chunk_words = words[i:i + self.chunk_size]
            chunk = " ".join(chunk_words)
            
            if len(chunk.strip()) > 50:  # Skip very small chunks
                chunks.append(chunk)
        
        return chunks
    
    def find_relevant_chunks(self, question: str, chunks: List[str], top_k: int = 2) -> List[str]:
        """Find most relevant chunks for a question"""
        question_lower = question.lower()
        question_words = set(question_lower.split())
        
        scored_chunks = []
        
        for chunk in chunks:
            chunk_lower = chunk.lower()
            chunk_words = set(chunk_lower.split())
            
            # Calculate relevance score
            common_words = question_words.intersection(chunk_words)
            score = len(common_words)
            
            # Boost for exact phrase matches
            if question_lower in chunk_lower:
                score += 10
            
            # Boost for health insurance keywords
            health_keywords = ['insurance', 'coverage', 'deductible', 'premium', 'benefit', 'medical', 'health', 'claim', 'copay', 'coinsurance']
            for keyword in health_keywords:
                if keyword in question_lower and keyword in chunk_lower:
                    score += 2
            
            scored_chunks.append((score, chunk))
        
        # Return top chunks with score > 0
        scored_chunks.sort(reverse=True, key=lambda x: x[0])
        return [chunk for score, chunk in scored_chunks[:top_k] if score > 0]