from typing import Optional, Any
from datetime import datetime, date
from bson.objectid import ObjectId
from .database_manager import DatabaseManager
import config
from pymongo import DESCENDING, ASCENDING
from utils import handler_datetime
from database.category_models import CategoryModel, InvalidCategoryError


class TransactionModel:

    def __init__(self, user_id: Optional[str] = None):
        self.db_manager = DatabaseManager()
        self.collection = self.db_manager.get_collection(config.COLLECTIONS["transaction"])
        self.user_id = ObjectId(user_id) if user_id else None

    def set_user_id(self, user_id: Optional[str]):
        self.user_id = ObjectId(user_id) if user_id else None

    # -----------------------------------------------------------
    # FETCH TRANSACTIONS
    # -----------------------------------------------------------
    def get_transactions(self, advanced_filters: dict[str, Any] = None) -> list[dict]:

        query = self._build_query(advanced_filters)
        cursor = self.collection.find(query).sort("created_at", -1)
        return list(cursor)

    def _build_query(self, filters: Optional[dict]) -> dict:
        conditions = []
        if not filters:
            return self._add_user_constraint(conditions)

        # Filter type
        if "transaction_type" in filters:
            conditions.append({"type": filters["transaction_type"]})

        # Filter category
        if "category" in filters:
            conditions.append({"category": filters["category"]})

        # Filter amount - only add if value > 0
        min_amount = filters.get("min_amount")
        max_amount = filters.get("max_amount")
        amount_query = {}
        
        if min_amount is not None and min_amount > 0:
            amount_query["$gte"] = min_amount
        
        if max_amount is not None and max_amount > 0:
            amount_query["$lte"] = max_amount
        
        if amount_query:
            conditions.append({"amount": amount_query})

        # Filter date range - convert date to datetime properly
        start_date = filters.get("start_date")
        end_date = filters.get("end_date")
        
        if start_date or end_date:
            date_query = {}
            
            if start_date is not None:
                # Check if it's a date object BEFORE converting
                if isinstance(start_date, date) and not isinstance(start_date, datetime):
                    start_datetime = datetime.combine(start_date, datetime.min.time())
                else:
                    start_datetime = start_date
                date_query["$gte"] = start_datetime
                
            if end_date is not None:
                # Check if it's a date object BEFORE converting
                if isinstance(end_date, date) and not isinstance(end_date, datetime):
                    end_datetime = datetime.combine(end_date, datetime.max.time())
                else:
                    end_datetime = end_date
                date_query["$lte"] = end_datetime
                
            conditions.append({"date": date_query})

        # Filter text
        if "search_text" in filters and filters["search_text"]:
            conditions.append({
                "description": {"$regex": filters["search_text"], "$options": "i"}
            })

        return self._add_user_constraint(conditions)

    def _add_user_constraint(self, conditions: list) -> dict:
        conditions.append({"user_id": self.user_id})
        return {"$and": conditions}

    # -----------------------------------------------------------
    # CREATE TRANSACTION
    # -----------------------------------------------------------
    def add_transaction(
        self,
        transaction_type: str,
        category: str,
        amount: float,
        transaction_date: datetime,
        description: str = ""
    ) -> Optional[str]:

        # Validate category
        category_model = CategoryModel(self.user_id)

        if not isinstance(transaction_date, datetime):
            transaction_date = handler_datetime(transaction_date)

        transaction = {
            "type": transaction_type,
            "category": category,
            "amount": amount,
            "date": transaction_date,
            "description": description,
            "created_at": datetime.now(),
            "last_modified": datetime.now(),
            "user_id": self.user_id
        }

        try:
            result = self.collection.insert_one(transaction)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error adding transaction: {e}")
            return None

    # -----------------------------------------------------------
    # UPDATE TRANSACTION
    # -----------------------------------------------------------
    def update_transaction(self, transaction_id: str, **kwargs) -> bool:

        # If category is being updated → validate it
        if "category" in kwargs:
            existing = self.get_transaction_by_id(transaction_id)
            if existing:
                category_model = CategoryModel(self.user_id)

        kwargs["last_modified"] = datetime.now()

        try:
            result = self.collection.update_one(
                {"_id": ObjectId(transaction_id), "user_id": self.user_id},
                {"$set": kwargs}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating transaction: {e}")
            return False

    # -----------------------------------------------------------
    # DELETE
    # -----------------------------------------------------------
    def delete_transaction(self, transaction_id: str) -> bool:
        try:
            result = self.collection.delete_one(
                {"_id": ObjectId(transaction_id), "user_id": self.user_id}
            )
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting transaction: {e}")
            return False

    # -----------------------------------------------------------
    # GET BY ID
    # -----------------------------------------------------------
    def get_transaction_by_id(self, transaction_id: str) -> Optional[dict]:
        try:
            return self.collection.find_one(
                {"_id": ObjectId(transaction_id), "user_id": self.user_id}
            )
        except Exception as e:
            print(f"Error getting transaction: {e}")
            return None

    # -----------------------------------------------------------
    # DATE RANGE
    # -----------------------------------------------------------
    def get_transactions_by_date_range(self, start_date, end_date) -> list[dict]:
        return self.get_transactions(
            advanced_filters={"start_date": start_date, "end_date": end_date}
        )