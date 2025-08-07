from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from typing import List, Optional

class TinyLlamaModel:
    def __init__(self, model_name: str = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"):
        """Initialize TinyLlama model for CPU inference"""
        print("Loading TinyLlama model...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float32,
            device_map="cpu",
            low_cpu_mem_usage=True
        )
        
        # Set padding token if not exists
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
            
        print("✓ TinyLlama model loaded successfully")
    
    def generate_answer(self, 
                       question: str, 
                       context: str, 
                       company_name: str = "",
                       max_new_tokens: int = 150,
                       temperature: float = 0.3) -> str:
        """Generate answer based on context and question"""
        
        if company_name:
            prompt = f"""Based on {company_name}'s health insurance policy, answer this question:

Context: {context[:1200]}

Question: {question}

Answer:"""
        else:
            prompt = f"""Based on the health policy document, answer this question:

Context: {context[:1200]}

Question: {question}

Answer:"""
        
        try:
            inputs = self.tokenizer(
                prompt, 
                return_tensors="pt", 
                truncation=True, 
                max_length=1024,
                padding=True
            )
            
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    temperature=temperature,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id
                )
            
            # Decode and extract answer
            full_response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            answer = full_response.split("Answer:")[-1].strip()
            
            return answer if answer else "I couldn't find specific information about this."
            
        except Exception as e:
            print(f"Error generating answer: {e}")
            return "Error processing your question."
    
    def batch_generate(self, questions_contexts: List[tuple]) -> List[str]:
        """Generate answers for multiple question-context pairs"""
        answers = []
        for question, context, company_name in questions_contexts:
            answer = self.generate_answer(question, context, company_name)
            answers.append(answer)
        return answers