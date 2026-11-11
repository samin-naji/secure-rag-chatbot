from fastapi import FastAPI

from app.routers import auth, documents


app = FastAPI(
    title="Secure RAG Chatbot",
    description="Secure AI Chatbot with Authentication and Access Control",
    version="0.3.0"
)

app.include_router(auth.router)
app.include_router(documents.router)


@app.get("/")
def home():
    return {
        "message": "Welcome to Secure RAG Chatbot!",
        "status": "running"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}