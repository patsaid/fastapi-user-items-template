from sqlalchemy import String, CheckConstraint, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base


class Categories(Base):
    __tablename__ = "categories"
    __table_args__ = (
        CheckConstraint("LENGTH(name) > 0", name="categories_name_length_check"),
        UniqueConstraint("name", name="categories_unique_name"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(36), nullable=False, unique=True)
    items = relationship(
        "Items", secondary="category_item_association", back_populates="categories"
    )


class Category_Item_association(Base):
    __tablename__ = "category_item_association"

    category_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("categories.id"), primary_key=True
    )
    item_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("items.id"), primary_key=True
    )
