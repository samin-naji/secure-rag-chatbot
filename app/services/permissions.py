from sqlalchemy.orm import Session

from app.models.user import User
from app.models.document import Document
from app.models.permission import DocumentPermission


def get_accessible_documents(
    db: Session,
    user: User
):
    """
    Return only documents the user is authorized to read.
    """

    # Admin has access to all documents
    if user.role == "admin":
        return (
            db.query(Document)
            .order_by(Document.id)
            .all()
        )

    # Other users need explicit read permission
    return (
        db.query(Document)
        .join(
            DocumentPermission,
            DocumentPermission.document_id == Document.id
        )
        .filter(
            DocumentPermission.user_id == user.id,
            DocumentPermission.permission == "read"
        )
        .order_by(Document.id)
        .all()
    )


def get_accessible_document(
    db: Session,
    user: User,
    document_id: int
):
    """
    Return a document only if the user can access it.

    Unauthorized and nonexistent documents both return None.
    """

    # Admin can access every document
    if user.role == "admin":
        return (
            db.query(Document)
            .filter(Document.id == document_id)
            .first()
        )

    # Apply access control directly inside the database query
    return (
        db.query(Document)
        .join(
            DocumentPermission,
            DocumentPermission.document_id == Document.id
        )
        .filter(
            Document.id == document_id,
            DocumentPermission.user_id == user.id,
            DocumentPermission.permission == "read"
        )
        .first()
    )
