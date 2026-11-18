from app.core.database import Base, engine

from app.models import (
    User,
    Document,
    DocumentPermission,
    DocumentChunk,
    AuditLog
)

Base.metadata.create_all(bind=engine)

print("Database tables created successfully!")