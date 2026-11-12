from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_role
from app.models.user import User
from app.schemas.admin import UserRoleUpdate, UserStatusUpdate

from app.models.document import Document
from app.models.permission import DocumentPermission
from app.schemas.admin import DocumentPermissionUpdate


router = APIRouter(prefix="/admin", tags=["Admin"])


def user_to_dict(user: User):
    """
    Return safe user information.
    Never expose hashed_password.
    """
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "department": user.department,
        "is_active": user.is_active,
    }


def prevent_last_admin_removal(db: Session, target_user: User):
    """
    Prevent removing or deactivating the last active admin.
    """
    if target_user.role != "admin" or not target_user.is_active:
        return

    active_admin_count = (
        db.query(User)
        .filter(
            User.role == "admin",
            User.is_active.is_(True)
        )
        .count()
    )

    if active_admin_count <= 1:
        raise HTTPException(
            status_code=409,
            detail="The last active admin cannot be removed or deactivated."
        )


@router.get("/access-check")
def admin_access_check(
    current_user: User = Depends(require_role("admin"))
):
    return {
        "message": "Admin access granted!",
        "username": current_user.username,
        "role": current_user.role,
    }


@router.get("/users")
def list_users(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    users = (
        db.query(User)
        .order_by(User.id)
        .offset(offset)
        .limit(limit)
        .all()
    )

    return {
        "users": [user_to_dict(user) for user in users],
        "limit": limit,
        "offset": offset,
    }


@router.patch("/users/{user_id}/role")
def update_user_role(
    user_id: int,
    payload: UserRoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    target_user = db.query(User).filter(User.id == user_id).first()

    if target_user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found."
        )

    if target_user.id == current_user.id:
        raise HTTPException(
            status_code=400,
            detail="You cannot change your own role."
        )

    if target_user.role == "admin" and payload.role != "admin":
        prevent_last_admin_removal(db, target_user)

    target_user.role = payload.role

    db.commit()
    db.refresh(target_user)

    return {
        "message": "User role updated successfully.",
        "user": user_to_dict(target_user),
    }


@router.patch("/users/{user_id}/status")
def update_user_status(
    user_id: int,
    payload: UserStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    target_user = db.query(User).filter(User.id == user_id).first()

    if target_user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found."
        )

    if target_user.id == current_user.id and not payload.is_active:
        raise HTTPException(
            status_code=400,
            detail="You cannot deactivate your own account."
        )

    if target_user.is_active and not payload.is_active:
        prevent_last_admin_removal(db, target_user)

    target_user.is_active = payload.is_active

    db.commit()
    db.refresh(target_user)

    return {
        "message": "User status updated successfully.",
        "user": user_to_dict(target_user),
    }





@router.get("/documents/{document_id}/permissions")
def list_document_permissions(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    document = (
        db.query(Document)
        .filter(Document.id == document_id)
        .first()
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found."
        )

    results = (
        db.query(DocumentPermission, User)
        .join(User, DocumentPermission.user_id == User.id)
        .filter(DocumentPermission.document_id == document_id)
        .order_by(User.id)
        .all()
    )

    permissions = [
        {
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active,
            "permission": permission.permission,
        }
        for permission, user in results
    ]

    return {
        "document_id": document.id,
        "filename": document.filename,
        "permissions": permissions,
    }


@router.put("/documents/{document_id}/permissions/{user_id}")
def grant_document_permission(
    document_id: int,
    user_id: int,
    payload: DocumentPermissionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    document = (
        db.query(Document)
        .filter(Document.id == document_id)
        .first()
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found."
        )

    target_user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if target_user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found."
        )

    if not target_user.is_active:
        raise HTTPException(
            status_code=409,
            detail="Cannot grant access to an inactive user."
        )

    if target_user.role == "admin":
        raise HTTPException(
            status_code=400,
            detail="Admins already have access to all documents."
        )

    permission = (
        db.query(DocumentPermission)
        .filter(
            DocumentPermission.document_id == document_id,
            DocumentPermission.user_id == user_id,
        )
        .first()
    )

    if permission is None:
        permission = DocumentPermission(
            document_id=document_id,
            user_id=user_id,
            permission=payload.permission,
        )
        db.add(permission)
        message = "Document permission granted successfully."
    else:
        permission.permission = payload.permission
        message = "Document permission updated successfully."

    db.commit()
    db.refresh(permission)

    return {
        "message": message,
        "document_id": document_id,
        "user_id": user_id,
        "permission": permission.permission,
    }


@router.delete("/documents/{document_id}/permissions/{user_id}")
def revoke_document_permission(
    document_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    permission = (
        db.query(DocumentPermission)
        .filter(
            DocumentPermission.document_id == document_id,
            DocumentPermission.user_id == user_id,
        )
        .first()
    )

    if permission is None:
        raise HTTPException(
            status_code=404,
            detail="Document permission not found."
        )

    db.delete(permission)
    db.commit()

    return {
        "message": "Document permission revoked successfully.",
        "document_id": document_id,
        "user_id": user_id,
    }
