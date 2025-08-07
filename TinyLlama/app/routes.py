from flask import Blueprint, request, jsonify
from model.llama_model import TinyLlamaModel
from pdfutils.extractor import PDFExtractor
from vectorstore.retriever import SimpleRetriever

# Initialize components
llama_model = None
company_data = {}
retriever = SimpleRetriever()

def initialize_service():
    """Initialize the service with model and data"""
    global llama_model, company_data
    
    # Load TinyLlama model
    llama_model = TinyLlamaModel()
    
    # Load all PDF data
    pdf_extractor = PDFExtractor()
    company_data = pdf_extractor.load_all_company_pdfs()
    
    print(f"✓ Service initialized with {len(company_data)} companies")

# Create blueprint
api = Blueprint('api', __name__)

@api.route('/query', methods=['POST'])
def query_policy():
    try:
        data = request.json
        question = data.get('question', '').strip()
        company = data.get('company', 'all')
        print(f"llama_model: {llama_model}, company_data keys: {list(company_data.keys())}")

        if not question:
            return jsonify({"error": "Question is required"}), 400
        
        if not company_data:
            return jsonify({"error": "No policies loaded"}), 503
        
        # Retrieve relevant contexts
        if company != 'all':
            if company not in company_data:
                return jsonify({
                    "error": f"Company '{company}' not found",
                    "available_companies": list(company_data.keys())
                }), 404
            
            contexts = retriever.retrieve_contexts(question, company_data, company)
            if not contexts:
                return jsonify({
                    "company": company,
                    "answer": "No relevant information found in the policy.",
                    "question": question
                })
            
            # Generate answer
            context = "\n\n".join([ctx for _, ctx in contexts])
            answer = llama_model.generate_answer(question, context, company)
            
            return jsonify({
                "company": company,
                "answer": answer,
                "question": question
            })
        else:
            # Query all companies
            results = []
            for comp_name in company_data.keys():
                contexts = retriever.retrieve_contexts(question, company_data, comp_name)
                if contexts:
                    context = "\n\n".join([ctx for _, ctx in contexts])
                    answer = llama_model.generate_answer(question, context, comp_name)
                    results.append({
                        "company": comp_name,
                        "answer": answer
                    })
            
            return jsonify({
                "question": question,
                "results": results,
                "total_companies": len(results)
            })
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Internal server error"}), 500

@api.route('/companies', methods=['GET'])
def list_companies():
    companies_info = [
        {
            "name": name,
            "filename": data['filename'],
            "chunk_count": data['chunk_count']
        }
        for name, data in company_data.items()
    ]
    return jsonify({
        "companies": companies_info,
        "total": len(companies_info)
    })

@api.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "companies_loaded": len(company_data),
        "model_loaded": llama_model is not None
    })