from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def log_event(
    db: Session,
    event_type: str,
    status: str,
    username: str,
    user_id: int | None = None,
    resource_type: str | None = None,
    resource_id: int | None = None,
    commit: bool = True,
) -> AuditLog:
    """
    Create a security audit event.

    commit=True:
        Persist the event immediately.

    commit=False:
        Add the event to the current transaction.
        The caller must commit or rollback.
    """

    audit_log = AuditLog(
        user_id=user_id,
        username=username,
        event_type=event_type,
        status=status,
        resource_type=resource_type,
        resource_id=resource_id,
    )

    try:
        db.add(audit_log)

        if commit:
            db.commit()
            db.refresh(audit_log)

        return audit_log

    except Exception:
        db.rollback()
        raise
