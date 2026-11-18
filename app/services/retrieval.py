from sqlalchemy import select, exists
from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.permission import DocumentPermission
from app.models.user import User

from app.services.embedding_service import generate_embedding


def search_similar_chunks(
    db: Session,
    user: User,
    query: str,
    top_k: int = 5
) -> list[dict]:
    """
    Secure semantic search.

    Admin:
        Can search all documents.

    Other users:
        Can search only documents with explicit read permission.

    Access control is enforced inside the database query.
    """

    # Step 1: Validate user
    if user is None or not user.is_active:
        raise ValueError("Active user is required.")

    # Step 2: Validate query
    if not isinstance(query, str) or not query.strip():
        raise ValueError("Search query cannot be empty.")

    # Step 3: Validate top_k
    if (
        not isinstance(top_k, int)
        or isinstance(top_k, bool)
        or not 1 <= top_k <= 100
    ):
        raise ValueError("top_k must be between 1 and 100.")

    # Step 4: Generate query embedding
    query_embedding = generate_embedding(query)

    # Step 5: Calculate cosine distance
    distance = DocumentChunk.embedding.cosine_distance(
        query_embedding
    ).label("distance")

    # Step 6: Build base query
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
    )

    # Step 7: Apply document-level access control
    if user.role != "admin":

        permission_check = exists(
            select(1).where(
                DocumentPermission.user_id == user.id,
                DocumentPermission.document_id == Document.id,
                DocumentPermission.permission == "read"
            )
        )

        statement = statement.where(permission_check)

    # Step 8: Sort and limit results
    statement = (
        statement
        .order_by(distance.asc())
        .limit(top_k)
    )

    # Step 9: Execute query
    results = db.execute(statement).all()

    # Step 10: Format results
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
