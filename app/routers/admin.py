from fastapi import APIRouter, Depends

from app.core.dependencies import require_role
from app.models.user import User


router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)


@router.get("/access-check")
def admin_access_check(
    current_user: User = Depends(
        require_role("admin")
    )
):
    return {
        "message": "Admin access granted!",
        "username": current_user.username,
        "role": current_user.role
    }
