from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class DocumentPermission(Base):
    __tablename__ = "document_permissions"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "document_id",
            name="uq_user_document_permission"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    document_id: Mapped[int] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False
    )

    permission: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="read"
    )