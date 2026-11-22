from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.database import get_db
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
)
from app.core.dependencies import get_current_user

from app.models.user import User
from app.schemas.user import (
    UserRegister,
    UserResponse,
    TokenResponse,
)

from app.services.audit_service import log_event


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    user_data: UserRegister,
    db: Session = Depends(get_db),
):
    existing_user = db.query(User).filter(
        (User.username == user_data.username)
        | (User.email == str(user_data.email))
    ).first()

    if existing_user:
        log_event(
            db=db,
            user_id=None,
            username=user_data.username,
            event_type="register",
            status="failure",
            resource_type="user",
            resource_id=None,
        )

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email already exists",
        )

    new_user = User(
        username=user_data.username,
        email=str(user_data.email),
        hashed_password=hash_password(user_data.password),
        role="employee",
        department="general",
        is_active=True,
    )

    db.add(new_user)

    try:
        db.commit()
        db.refresh(new_user)

    except IntegrityError:
        db.rollback()

        log_event(
            db=db,
            user_id=None,
            username=user_data.username,
            event_type="register",
            status="failure",
            resource_type="user",
            resource_id=None,
        )

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email already exists",
        )

    log_event(
        db=db,
        user_id=new_user.id,
        username=new_user.username,
        event_type="register",
        status="success",
        resource_type="user",
        resource_id=new_user.id,
    )

    return new_user


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(
        User.username == form_data.username
    ).first()

    # User does not exist
    if user is None:
        log_event(
            db=db,
            user_id=None,
            username=form_data.username,
            event_type="login",
            status="failure",
            resource_type="user",
            resource_id=None,
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Password is incorrect
    if not verify_password(
        form_data.password,
        user.hashed_password,
    ):
        log_event(
            db=db,
            user_id=user.id,
            username=user.username,
            event_type="login",
            status="failure",
            resource_type="user",
            resource_id=user.id,
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # User account is inactive
    if not user.is_active:
        log_event(
            db=db,
            user_id=user.id,
            username=user.username,
            event_type="login",
            status="failure",
            resource_type="user",
            resource_id=user.id,
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Successful login
    log_event(
        db=db,
        user_id=user.id,
        username=user.username,
        event_type="login",
        status="success",
        resource_type="user",
        resource_id=user.id,
    )

    access_token = create_access_token(user.id)

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.get(
    "/me",
    response_model=UserResponse,
)
def get_my_profile(
    current_user: User = Depends(get_current_user),
):
    return current_user