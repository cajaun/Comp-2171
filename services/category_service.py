from __future__ import annotations

from sqlalchemy.orm import joinedload

from data.models import Category, Item
from services.base import ServiceBase
from services.view_models import CategoryStats, CategorySummary


class CategoryService(ServiceBase):
    def list_categories(self) -> list[CategorySummary]:
        with self.session_scope() as session:
            categories = (
                session.query(Category)
                .options(joinedload(Category.items))
                .order_by(Category.name.asc())
                .all()
            )
            return [
                CategorySummary(
                    category_id=category.category_id,
                    name=category.name,
                    description=category.description or "",
                    item_count=len(category.items),
                )
                for category in categories
            ]

    def get_category(self, category_id: int) -> CategorySummary | None:
        with self.session_scope() as session:
            category = session.get(Category, category_id)
            if not category:
                return None
            return CategorySummary(
                category_id=category.category_id,
                name=category.name,
                description=category.description or "",
                item_count=len(category.items),
            )

    def create_category(self, name: str, description: str) -> CategorySummary:
        self._validate(name, description)
        with self.session_scope() as session:
            category = Category(name=name.strip(), description=description.strip())
            session.add(category)
            session.flush()
            return CategorySummary(
                category_id=category.category_id,
                name=category.name,
                description=category.description,
                item_count=0,
            )

    def update_category(self, category_id: int, name: str, description: str) -> CategorySummary:
        self._validate(name, description)
        with self.session_scope() as session:
            category = session.get(Category, category_id)
            if not category:
                raise ValueError("Category not found")

            category.name = name.strip()
            category.description = description.strip()
            session.flush()
            return CategorySummary(
                category_id=category.category_id,
                name=category.name,
                description=category.description,
                item_count=len(category.items),
            )

    def delete_category(self, category_id: int) -> None:
        with self.session_scope() as session:
            category = session.get(Category, category_id)
            if not category:
                raise ValueError("Category not found")
            session.delete(category)

    def get_category_stats(self) -> CategoryStats:
        with self.session_scope() as session:
            categories = (
                session.query(Category)
                .options(joinedload(Category.items))
                .all()
            )
            items = session.query(Item).all()

        most_items = "-"
        if categories:
            category = max(categories, key=lambda current: len(current.items))
            most_items = f"{category.name} ({len(category.items)})"

        most_valuable = "-"
        if categories:
            values = {
                category.name: sum((item.price or 0) * (item.current_stock or 0) for item in category.items)
                for category in categories
            }
            if values:
                category_name = max(values, key=values.get)
                most_valuable = f"{category_name} (${values[category_name]:.2f})"

        low_stock = sum(
            1 for item in items if (item.current_stock or 0) < (item.reorder_level or 10)
        )

        return CategoryStats(
            total=len(categories),
            most_items=most_items,
            most_valuable=most_valuable,
            low_stock=low_stock,
        )

    def _validate(self, name: str, description: str) -> None:
        if not name.strip():
            raise ValueError("Name is required")
        if not description.strip():
            raise ValueError("Description is required")
