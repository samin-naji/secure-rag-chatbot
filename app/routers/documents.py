from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File
)
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import (
    get_current_user,
    require_role
)

from app.models.user import User
from app.models.document import Document
from app.models.document_chunk import DocumentChunk

from app.services.permissions import (
    get_accessible_documents,
    get_accessible_document
)

from app.services.document_extraction import (
    extract_document_text,
    DocumentExtractionError
)

from app.services.text_chunking import split_text_into_chunks

from app.services.embedding_service import generate_embeddings

from app.services.audit_service import log_event


router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)


@router.post("/upload", status_code=201)
def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """
    Upload PDF or TXT documents.
    Only administrators can upload documents.
    """

    # Step 1: Read uploaded file
    try:
        file_bytes = file.file.read()

        # Step 2: Extract and validate text
        extracted_text = extract_document_text(
            filename=file.filename,
            file_bytes=file_bytes
        )

        # Step 3: Split text into chunks
        chunks = split_text_into_chunks(extracted_text)

        if not chunks:
            raise HTTPException(
                status_code=400,
                detail="Document contains no valid chunks."
            )

        # Step 4: Generate embeddings for all chunks
        embeddings = generate_embeddings(chunks)

        # Step 5: Create document record
        document = Document(
            filename=file.filename,
            department=current_user.department,
            content=extracted_text
        )

        db.add(document)
        db.flush()

        # Step 6: Create document chunks with embeddings
        document_chunks = [
            DocumentChunk(
                document_id=document.id,
                chunk_index=index,
                content=chunk,
                embedding=embedding
            )
            for index, (chunk, embedding) in enumerate(
                zip(chunks, embeddings)
            )
        ]

        db.add_all(document_chunks)

        # Step 7: Commit transaction
        db.commit()
        db.refresh(document)

        log_event(
            db=db,
            event_type="document_upload",
            status="success",
            username=current_user.username,
            user_id=current_user.id,
            resource_type="document",
            resource_id=document.id
        )

        return {
            "message": "Document uploaded successfully.",
            "document_id": document.id,
            "filename": document.filename,
            "department": document.department,
            "total_chunks": len(document_chunks)
        }

    except DocumentExtractionError as exc:
        db.rollback()

        log_event(
            db=db,
            event_type="document_upload",
            status="failure",
            username=current_user.username,
            user_id=current_user.id,
            resource_type="document",
            resource_id=None
        )

        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )

    except HTTPException:
        db.rollback()

        log_event(
            db=db,
            event_type="document_upload",
            status="failure",
            username=current_user.username,
            user_id=current_user.id,
            resource_type="document",
            resource_id=None
        )

        raise

    except Exception:
        db.rollback()
        
        log_event(
            db=db,
            event_type="document_upload",
            status="failure",
            username=current_user.username,
            user_id=current_user.id,
            resource_type="document",
            resource_id=None
        )

        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing or saving the document."
        )

    finally:
        file.file.close()


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
    document = get_accessible_document(
        db,
        current_user,
        document_id
    )

    if document is None:
        log_event(
            db=db,
            event_type="document_view",
            status="failure",
            username=current_user.username,
            user_id=current_user.id,
            resource_type="document",
            resource_id=document_id
        )

        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    log_event(
        db=db,
        event_type="document_view",
        status="success",
        username=current_user.username,
        user_id=current_user.id,
        resource_type="document",
        resource_id=document.id
    )

    return {
        "id": document.id,
        "filename": document.filename,
        "department": document.department,
        "content": document.content
    }
