from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user

from app.models.user import User
from app.models.document import Document

from app.services.permissions import (
    can_access_document,
    get_accessible_documents
)


router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)


@router.get("/")
def list_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    documents = get_accessible_documents(
        db,
        current_user
    )

    return [
        {
            "id": document.id,
            "filename": document.filename,
            "department": document.department
        }
        for document in documents
    ]


@router.get("/{document_id}")
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    document = db.query(Document).filter(
        Document.id == document_id
    ).first()

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    if not can_access_document(
        db,
        current_user,
        document_id
    ):
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to access this document"
        )

    return {
        "id": document.id,
        "filename": document.filename,
        "department": document.department,
        "content": document.content
    }