from .database_manager import DatabaseManager
from typing import Optional
from datetime import datetime
from bson import ObjectId
import config


class CategoryModel:
    def __init__(self, user_id: Optional[str] = None):
        self.db_manager = DatabaseManager()
        self.collection = self.db_manager.get_collection("categories")
        self.transactions = self.db_manager.get_collection("transactions")

        self.user_id = ObjectId(user_id) if user_id else None

        # Initialize default categories for the user
        if self.user_id:
            self._initialize_user_default_categories()

    # ---------------------------------------------------------------------
    # USER SETUP
    # ---------------------------------------------------------------------
    def set_user_id(self, user_id: str):
        self.user_id = ObjectId(user_id) if user_id else None
        if self.user_id:
            self._initialize_user_default_categories()

    def _initialize_user_default_categories(self):
        """Create default categories for this user if missing."""
        if not self.user_id:
            return

        # Expense defaults
        for name in config.DEFAULT_CATEGORIES_EXPENSE:
            self.upsert_category("Expense", name)

        # Income defaults
        for name in config.DEFAULT_CATEGORIES_INCOME:
            self.upsert_category("Income", name)

    # ---------------------------------------------------------------------
    # UPSERT CATEGORY + HANDLE RENAME
    # ---------------------------------------------------------------------
    def upsert_category(self, category_type: str, category_name: str, old_name: Optional[str] = None):
        """
        Create, update, or rename a category.
        When renaming: update all linked transactions.
        """
        if not self.user_id:
            return None

        # RENAME CATEGORY
        if old_name and old_name != category_name:
            # Update category name
            self.collection.update_one(
                {"user_id": self.user_id, "type": category_type, "name": old_name},
                {"$set": {"name": category_name, "last_modified": datetime.now()}}
            )

            # Also update linked transactions
            return self.update_transactions_category(old_name, category_name, category_type)

        # CREATE OR UPDATE CATEGORY (normal upsert)
        result = self.collection.update_one(
            {"user_id": self.user_id, "type": category_type, "name": category_name},
            {
                "$set": {"last_modified": datetime.now()},
                "$setOnInsert": {"created_at": datetime.now()}
            },
            upsert=True
        )

        return result.upserted_id or True

    # ---------------------------------------------------------------------
    # SAFE DELETE
    # ---------------------------------------------------------------------
    def get_other_categories(self, category_type: str, exclude_name: str):
        """Return all other categories for reassignment."""
        if not self.user_id:
            return []

        return list(self.collection.find(
            {
                "user_id": self.user_id,
                "type": category_type,
                "name": {"$ne": exclude_name}
            },
            {"name": 1}
        ))
    
    def delete_category_safe(
        self,
        category_type: str,
        category_name: str,
        strategy: str = "Block",
        new_category: Optional[str] = None
    ) -> bool:
        """
        Delete a category safely.

        Strategies:
        - Block     → prevent delete if linked to transactions.
        - Reassign  → move transactions to another chosen category.
        - Cascade   → delete all transactions in this category.
        """
        if not self.user_id:
            return False

        tx_count = self.count_transactions_by_category(category_type, category_name)

        # ----------------------
        # STRATEGY: BLOCK
        # ----------------------
        if strategy == "Block":
            if tx_count > 0:
                return False

        # ----------------------
        # STRATEGY: REASSIGN
        # ----------------------
        elif strategy == "Reassign":
            if tx_count > 0:
                if not new_category:
                    # UI error prevention
                    return False

                # Update transactions to the new category
                self.transactions.update_many(
                    {
                        "user_id": self.user_id,
                        "type": category_type,
                        "category": category_name
                    },
                    {"$set": {"category": new_category}}
                )

        # ----------------------
        # STRATEGY: CASCADE
        # ----------------------
        elif strategy == "Cascade":
            if tx_count > 0:
                self.transactions.delete_many(
                    {
                        "user_id": self.user_id,
                        "type": category_type,
                        "category": category_name
                    }
                )

        else:
            raise ValueError("Strategy must be 'Block', 'Reassign', or 'Cascade'")

        # ----------------------
        # DELETE CATEGORY ITSELF
        # ----------------------
        result = self.collection.delete_one({
            "user_id": self.user_id,
            "type": category_type,
            "name": category_name
        })

        return result.deleted_count > 0

    # ---------------------------------------------------------------------
    # HELPERS
    # ---------------------------------------------------------------------
    def count_transactions_by_category(self, category_type: str, category_name: str) -> int:
        """Return how many transactions use this category."""
        if not self.user_id:
            return 0
        return self.transactions.count_documents({
            "user_id": self.user_id,
            "type": category_type,
            "category": category_name
        })
    
    def rename_category(self, category_type: str, old_name: str, new_name: str) -> int:
        """
        Rename a category and update all related transactions.
        Returns number of updated transactions.
        """
        if not self.user_id:
            return 0

        # Update category document
        self.collection.update_one(
            {"user_id": self.user_id, "type": category_type, "name": old_name},
            {"$set": {
                "name": new_name,
                "last_modified": datetime.now()
            }}
        )

        # Corrected transaction update (self.transactions)
        result = self.transactions.update_many(
            {
                "user_id": self.user_id,
                "type": category_type,
                "category": old_name
            },
            {"$set": {"category": new_name}}
        )

        return result.modified_count


    def update_transactions_category(self, old_name: str, new_name: str, category_type: str) -> int:
        """Update all transactions linked to a renamed category."""
        if not self.user_id:
            return 0

        result = self.transactions.update_many(
            {
                "user_id": self.user_id,
                "type": category_type,
                "category": old_name
            },
            {"$set": {"category": new_name}}
        )

        return result.modified_count

    # ---------------------------------------------------------------------
    # GETTERS
    # ---------------------------------------------------------------------
    def get_categories_by_type(self, category_type: str):
        """Return all categories (name + timestamps) for UI listing."""
        if not self.user_id:
            return []

        return list(self.collection.find(
            {"user_id": self.user_id, "type": category_type},
            {"name": 1, "type": 1, "created_at": 1, "last_modified": 1}
        ))


class InvalidCategoryError(Exception):
    pass


    # DELETE USER

    def count_user_categories(self, exclude_defaults=True) -> int:
        """
        Count categories created by the current user.
        
        Args:
            exclude_defaults: If True, excludes system default categories
            
        Returns:
            int: Number of user categories
        """
        if not self.user_id:
            return 0
        
        query = {"user_id": self.user_id}
        
        if exclude_defaults:
            import config
            default_categories = config.DEFAULT_CATEGORIES_EXPENSE + config.DEFAULT_CATEGORIES_INCOME
            query["name"] = {"$nin": default_categories}
        
        return self.collection.count_documents(query)



    def delete_user_categories(self, exclude_defaults=True) -> int:
        """
        Delete all categories created by the current user.
        
        Args:
            exclude_defaults: If True, only deletes custom categories (preserves defaults)
            
        Returns:
            int: Number of categories deleted
        """
        if not self.user_id:
            return 0
        
        query = {"user_id": self.user_id}
        
        if exclude_defaults:
            import config
            default_categories = config.DEFAULT_CATEGORIES_EXPENSE + config.DEFAULT_CATEGORIES_INCOME
            query["name"] = {"$nin": default_categories}
        
        result = self.collection.delete_many(query)
        return result.deleted_count
