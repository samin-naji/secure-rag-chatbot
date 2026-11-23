from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User
from app.services.audit_service import log_event


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)


# Supported application roles
VALID_ROLES = frozenset({
    "employee",
    "hr",
    "admin"
})


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired authentication token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(token)
        user_id = int(payload["sub"])

    except (
        InvalidTokenError,
        KeyError,
        TypeError,
        ValueError
    ):
        raise credentials_exception

    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if user is None or not user.is_active:
        raise credentials_exception

    return user


def require_role(*allowed_roles: str):
    """
    Allow only specified roles and audit denied access.
    """

    if not allowed_roles:
        raise ValueError(
            "At least one role must be specified."
        )

    invalid_roles = set(allowed_roles) - VALID_ROLES

    if invalid_roles:
        raise ValueError(
            f"Invalid roles: {invalid_roles}"
        )

    def role_checker(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        if current_user.role not in allowed_roles:

            log_event(
                db=db,
                event_type="access_denied",
                status="failure",
                username=current_user.username,
                user_id=current_user.id,
                resource_type="role",
                resource_id=None
            )

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action."
            )

        return current_user

    return role_checker

