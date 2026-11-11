from sqlalchemy.orm import Session

from app.models.user import User
from app.models.document import Document
from app.models.permission import DocumentPermission


def can_access_document(
    db: Session,
    user: User,
    document_id: int
) -> bool:
    """
    Check whether a user can read a document.
    """

    # Admin can access all documents
    if user.role == "admin":
        return True

    # Explicit permission is required for other users
    permission = db.query(DocumentPermission).filter(
        DocumentPermission.user_id == user.id,
        DocumentPermission.document_id == document_id,
        DocumentPermission.permission == "read"
    ).first()

    return permission is not None


def get_accessible_documents(
    db: Session,
    user: User
):
    """
    Return only documents accessible to the user.
    """

    # Admin can see all documents
    if user.role == "admin":
        return db.query(Document).all()

    # Other users can only see explicitly authorized documents
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
        .all()
    )
