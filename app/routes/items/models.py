from sqlalchemy import String, ForeignKey, CheckConstraint, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base
from sqlalchemy.dialects.postgresql import UUID
import uuid


class Items(Base):
    __tablename__ = "items"
    __table_args__ = (
        CheckConstraint("LENGTH(name) > 0", name="items_name_length_check"),
    )

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('users.id'), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Relationship to Categories
    categories = relationship(
        "Categories", secondary="category_item_association", back_populates="items"
    )

    # Relationship to Users
    user = relationship("Users", back_populates="items")
