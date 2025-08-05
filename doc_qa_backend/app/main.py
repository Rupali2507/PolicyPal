# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import router as api_router

app = FastAPI(
    title="PolicyPal ML Backend",
    description="API for answering questions about uploaded policy documents.",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the API endpoint(s) from api.py
app.include_router(api_router, prefix="/api", tags=["Document Processing"])

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "ML Service is running. Access the API docs at /docs"}