from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document_chunk import DocumentChunk
from app.models.document import Document

from app.services.embedding_service import generate_embedding


def search_similar_chunks(
    db: Session,
    query: str,
    top_k: int = 5
) -> list[dict]:
    """
    Find the most semantically similar document chunks.

    INTERNAL TESTING ONLY:
    This function does not apply document-level permissions.
    Do not expose it through a public API before adding
    authorization filters in the database query.
    """

    # Step 1: Validate input
    if not isinstance(query, str) or not query.strip():
        raise ValueError("Search query cannot be empty.")

    if not isinstance(top_k, int) or isinstance(top_k, bool):
        raise ValueError("top_k must be an integer.")

    if not 1 <= top_k <= 100:
        raise ValueError("top_k must be between 1 and 100.")

    # Step 2: Generate embedding for user query
    query_embedding = generate_embedding(query)

    # Step 3: Calculate cosine distance
    distance = DocumentChunk.embedding.cosine_distance(
        query_embedding
    ).label("distance")

    # Step 4: Build semantic search query
    statement = (
        select(
            DocumentChunk,
            Document.filename,
            distance
        )
        .join(
            Document,
            Document.id == DocumentChunk.document_id
        )
        .where(
            DocumentChunk.embedding.is_not(None)
        )
        .order_by(distance.asc())
        .limit(top_k)
    )

    # Step 5: Execute query
    results = db.execute(statement).all()

    # Step 6: Format results
    search_results = []

    for chunk, filename, cosine_distance in results:

        similarity = 1.0 - float(cosine_distance)

        search_results.append({
            "chunk_id": chunk.id,
            "document_id": chunk.document_id,
            "filename": filename,
            "chunk_index": chunk.chunk_index,
            "content": chunk.content,
            "similarity": similarity
        })

    return search_results
