from app.core.database import Base, engine

from app.models import (
    User,
    Document,
    DocumentPermission,
    DocumentChunk
)

Base.metadata.create_all(bind=engine)

print("Database tables created successfully!")
