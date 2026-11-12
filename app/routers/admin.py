from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_role
from app.models.user import User
from app.schemas.admin import UserRoleUpdate, UserStatusUpdate


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
