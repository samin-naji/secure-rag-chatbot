from fastapi import FastAPI

app = FastAPI(
    title="Secure RAG Chatbot",
    description="An AI chatbot with authentication, access control and data privacy.",
    version="0.1.0"
)


@app.get("/")
def home():
    return {
        "message": "Welcome to Secure RAG Chatbot!",
        "status": "running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }
