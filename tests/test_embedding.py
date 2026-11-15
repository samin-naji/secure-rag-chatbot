from app.services.embedding_service import generate_embedding

text = "Secure RAG chatbot with document access control."

embedding = generate_embedding(text)

print("Embedding generated successfully!")
print("Dimensions:", len(embedding))
print("First 5 values:", embedding[:5])