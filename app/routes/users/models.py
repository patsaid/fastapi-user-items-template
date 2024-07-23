from sqlalchemy import CheckConstraint, String, Boolean, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from app.db.database import Base
from app.commons.utils import get_uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid

class Users(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("LENGTH(name) >= 3", name="users_name_length_check"),
        CheckConstraint("LENGTH(email) >= 1", name="users_email_length_check"),
        CheckConstraint("LENGTH(password) >= 8", name="users_password_length_check"),
        CheckConstraint("role IN ('user', 'admin')", name="users_role_validity_check"),
        UniqueConstraint("email", name="users_unique_email"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=get_uuid
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(
        String(255), index=True, unique=True, nullable=False
    )
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false"
    )
    role = mapped_column(String(50), nullable=False, default="user")

    # Relationship to Items
    items = relationship("Items", back_populates="user", cascade="all, delete-orphan")
