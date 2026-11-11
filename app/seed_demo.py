from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.security import hash_password

from app.models.user import User
from app.models.document import Document
from app.models.permission import DocumentPermission

from app.core.config import settings


def get_or_create_user(
    db: Session,
    username: str,
    email: str,
    password: str,
    role: str,
    department: str
):
    user = db.query(User).filter(
        User.username == username
    ).first()

    if user is None:
        user = User(
            username=username,
            email=email,
            hashed_password=hash_password(password),
            role=role,
            department=department,
            is_active=True
        )
        db.add(user)
        db.flush()
    else:
        user.role = role
        user.department = department
        user.is_active = True

    return user


def get_or_create_document(
    db: Session,
    filename: str,
    department: str,
    content: str
):
    document = db.query(Document).filter(
        Document.filename == filename
    ).first()

    if document is None:
        document = Document(
            filename=filename,
            department=department,
            content=content
        )
        db.add(document)
        db.flush()

    return document


def grant_read_permission(
    db: Session,
    user: User,
    document: Document
):
    permission = db.query(DocumentPermission).filter(
        DocumentPermission.user_id == user.id,
        DocumentPermission.document_id == document.id
    ).first()

    if permission is None:
        permission = DocumentPermission(
            user_id=user.id,
            document_id=document.id,
            permission="read"
        )
        db.add(permission)


def seed_database():
    db = SessionLocal()

    try:
        ali = get_or_create_user(
            db, "ali", "ali@example.com",
            settings.demo_ali_password,
            "employee", "Engineering"
        )

        sara = get_or_create_user(
            db, "sara", "sara@example.com",
            settings.demo_sara_password,
            "hr", "HR"
        )

        admin = get_or_create_user(
            db, "admin", "admin@example.com",
            settings.demo_admin_password,
            "admin", "Management"
        )

        engineering = get_or_create_document(
            db,
            "engineering.pdf",
            "Engineering",
            "Engineering team develops software products."
        )

        hr_policy = get_or_create_document(
            db,
            "hr_policy.pdf",
            "HR",
            "Employees receive annual leave according to company policy."
        )

        company = get_or_create_document(
            db,
            "company_overview.pdf",
            "General",
            "Our company develops AI-powered software solutions."
        )

        grant_read_permission(db, ali, engineering)
        grant_read_permission(db, ali, company)

        grant_read_permission(db, sara, hr_policy)
        grant_read_permission(db, sara, company)

        db.commit()

        print("Demo data created successfully!")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
