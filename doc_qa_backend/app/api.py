from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import tempfile
import os
from .core.logic import rag_processor, FinalResponse

router = APIRouter()

@router.post("/process")
async def process_document_and_get_answer(
    query: str = Form(...),
    file: UploadFile = File(...)
):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    try:
        file_bytes = await file.read()

        fd, temp_path = tempfile.mkstemp(suffix=".pdf")
        os.close(fd)

        try:
            with open(temp_path, "wb") as f:
                f.write(file_bytes)

            result = rag_processor.process_document_and_query(file_path=temp_path, query=query)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

        response_data = result.dict()
        return response_data

    except Exception as e:
        import traceback
        print("---! PYTHON SERVER ERROR !---")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        traceback.print_exc()
        print("---------------------------")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
