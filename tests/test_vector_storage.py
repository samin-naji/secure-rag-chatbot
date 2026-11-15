from sqlalchemy import select

from app.core.database import SessionLocal
from app.models.document_chunk import DocumentChunk
from app.services.embedding_service import generate_embedding


db = SessionLocal()

try:
    chunk = db.execute(
        select(DocumentChunk).where(DocumentChunk.id == 1)
    ).scalar_one_or_none()

    if chunk is None:
        print("Chunk with ID 1 was not found.")
    else:
        embedding = generate_embedding(chunk.content)

        chunk.embedding = embedding
        db.commit()
        db.refresh(chunk)

        print("Embedding saved successfully!")
        print("Chunk ID:", chunk.id)
        print("Embedding dimensions:", len(chunk.embedding))
        print("First 5 values:", chunk.embedding[:5])

except Exception:
    db.rollback()
    raise

finally:
    db.close()