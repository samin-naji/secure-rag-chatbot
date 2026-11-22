from app.core.database import SessionLocal
from app.services.audit_service import log_event


def test_audit_log():
    db = SessionLocal()

    try:
        audit_log = log_event(
            db=db,
            event_type="audit_test",
            status="success",
            username="audit_test_user",
            user_id=None,
            resource_type="system",
            resource_id=None,
        )

        print("Audit log created successfully")
        print(f"ID: {audit_log.id}")
        print(f"Username: {audit_log.username}")
        print(f"Event: {audit_log.event_type}")
        print(f"Status: {audit_log.status}")
        print(f"Created at: {audit_log.created_at}")

    finally:
        db.close()


if __name__ == "__main__":
    test_audit_log()