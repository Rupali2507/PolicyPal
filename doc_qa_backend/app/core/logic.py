import os
import re
import sys
import tempfile
from typing import Optional, List
from langchain_community.llms import Ollama
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pydantic.v1 import BaseModel

class FinalResponse(BaseModel):
    decision: str
    amount_covered: Optional[float]
    justification: List[str]
    narrative_response: str

class StructuredQuery(BaseModel):
    procedure: Optional[str] = None
    age: Optional[int] = None
    policy_duration_months: Optional[int] = None

class SimpleRAGProcessor:
    def __init__(self):
        self.llm = Ollama(model="gemma:2b", temperature=0)
        self.embedding_model = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )
        print(">> Simple RAG Processor Ready.", file=sys.stderr)

    def extract_key_info_from_query(self, query: str) -> StructuredQuery:
        age_match = re.search(r'\b(\d{1,2})\s*(?:years?\s*old|yr|age)', query.lower())
        age = int(age_match.group(1)) if age_match else None
        procedure = query.strip()
        return StructuredQuery(procedure=procedure, age=age, policy_duration_months=None)

    def analyze_context_simple(self, context: str, procedure: str) -> dict:
        context_lower = context.lower()
        procedure_lower = procedure.lower() if procedure else ""
        covered_phrases = ["is covered", "are covered", "coverage includes", "benefits include", "eligible for", "reimbursed", "we pay", "covered expense"]
        excluded_phrases = ["not covered", "excluded", "not eligible", "exception", "limitation", "we do not pay", "excluded from coverage"]
        coverage_found = any(phrase in context_lower for phrase in covered_phrases)
        exclusion_found = any(phrase in context_lower for phrase in excluded_phrases)
        return {"coverage_found": coverage_found, "exclusion_found": exclusion_found}

    def generate_decision_step_by_step(self, context: str, query: str, analysis: dict) -> dict:
        decision_prompt = f"""Reviewing policy for: {query}\n\nPolicy info:\n{context}\n\nAnswer ONE word: APPROVED, REJECTED, or UNCLEAR"""
        decision_raw = self.llm.invoke(decision_prompt).strip().upper()
        if "APPROVED" in decision_raw:
            decision = "Approved"
        elif "REJECTED" in decision_raw:
            decision = "Rejected"
        else:
            decision = "Needs Review"

        amount_prompt = f"""Policy text for: {query}\n\nPolicy:\n{context}\n\nWhat is the dollar amount covered? Respond with just the number. If none, respond with 0."""
        amount_raw = self.llm.invoke(amount_prompt).strip()
        amount_match = re.search(r'(\d+(?:,\d{3})*(?:\.\d{2})?)', amount_raw.replace(',', ''))
        amount_covered = float(amount_match.group(1)) if amount_match else 0.0

        reason_prompt = f"""Policy for: {query}\nDecision: {decision}\n\nPolicy text:\n{context}\n\nExplain the main reason in ONE simple sentence starting with 'Because'."""
        main_reason = self.llm.invoke(reason_prompt).strip()
        if not main_reason.lower().startswith("because"):
            main_reason = f"Because {main_reason}"

        details_prompt = f"""Policy for: {query}\n\nPolicy text:\n{context}\n\nFind ONE specific supporting detail (e.g., a policy section number or rule)."""
        supporting_detail = self.llm.invoke(details_prompt).strip()
        return {"decision": decision, "amount_covered": amount_covered, "main_reason": main_reason, "supporting_detail": supporting_detail}

    def create_natural_response(self, decision_info: dict, query: str) -> str:
        response_prompt = f"""Write a friendly, 2-3 sentence response for a customer who asked: "{query}"\n\nDecision: {decision_info['decision']}\nAmount: ${decision_info['amount_covered']}\nReason: {decision_info['main_reason']}\nDetail: {decision_info['supporting_detail']}"""
        return self.llm.invoke(response_prompt).strip()

    def process_document_and_query(self, *, file_bytes=None, file_path=None, query):
     if file_bytes is not None:
        # Create temp file path (no open file handle kept)
        fd, temp_path = tempfile.mkstemp(suffix=".pdf")
        os.close(fd)  # Close low-level file descriptor immediately

        try:
            # Write bytes with open (context auto closes file)
            with open(temp_path, "wb") as f:
                f.write(file_bytes)

            # Now process the temp file path
            return self._process_document_file(temp_path, query)
        finally:
            # Remove temp file after processing
            if os.path.exists(temp_path):
                os.unlink(temp_path)
     elif file_path is not None:
        return self._process_document_file(file_path, query)
     else:
        raise ValueError("Must provide either file_bytes or file_path")

    def _process_document_file(self, file_path, query):
        loader = PyPDFLoader(file_path)
        documents = loader.load()

        if not documents:
            return FinalResponse(decision="Error", amount_covered=0,
                                 justification=["Could not read the PDF"],
                                 narrative_response="I'm sorry, I couldn't read your policy document.")

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        chunks = text_splitter.split_documents(documents)
        vector_store = Chroma.from_documents(chunks, self.embedding_model)
        retriever = vector_store.as_retriever(search_kwargs={"k": 6})

        structured_query = self.extract_key_info_from_query(query)
        print(f"[Processing] Looking for: {structured_query.procedure}", file=sys.stderr)

        search_terms = [query,
                        structured_query.procedure if structured_query.procedure else query,
                        f"{structured_query.procedure} coverage" if structured_query.procedure else f"{query} coverage"]
        all_docs = []
        for term in search_terms:
            all_docs.extend(retriever.invoke(term)[:3])

        seen, unique_docs = set(), []
        for doc in all_docs:
            doc_hash = hash(doc.page_content)
            if doc_hash not in seen:
                seen.add(doc_hash)
                unique_docs.append(doc)
                if len(unique_docs) >= 5:
                    break

        if not unique_docs:
            return FinalResponse(decision="Needs Review", amount_covered=0,
                                 justification=["No relevant information found"],
                                 narrative_response=f"I couldn't find specific information about '{query}' in your policy document.")

        context = "\n\n".join([doc.page_content for doc in unique_docs])

        print("[Processing] Analyzing policy context...", file=sys.stderr)
        analysis = self.analyze_context_simple(context, structured_query.procedure)

        print("[Processing] Making decision...", file=sys.stderr)
        decision_info = self.generate_decision_step_by_step(context, query, analysis)

        print(f"[Result] Decision: {decision_info['decision']}, Amount: ${decision_info['amount_covered']}", file=sys.stderr)

        narrative = self.create_natural_response(decision_info, query)

        justifications = []
        if decision_info['main_reason']:
            justifications.append(decision_info['main_reason'])
        if decision_info['supporting_detail']:
            justifications.append(decision_info['supporting_detail'])
        if not justifications:
            justifications = [f"Based on review of the policy sections related to {structured_query.procedure or 'your question'}"]

        return FinalResponse(
            decision=decision_info['decision'],
            amount_covered=decision_info['amount_covered'],
            justification=justifications,
            narrative_response=narrative
        )

rag_processor = SimpleRAGProcessor()
