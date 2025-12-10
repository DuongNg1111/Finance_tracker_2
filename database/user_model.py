from database.database_manager import DatabaseManager
import config
from datetime import datetime
from bson.objectid import ObjectId

collection_name = config.COLLECTIONS['user']

class UserModel:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.collection = self.db_manager.get_collection(collection_name=collection_name)

    def create_user(self, email: str) -> str:
        """Create new user"""

        user = {
            "email": email,
            "created_at": datetime.now(),
            "last_modified": datetime.now(),
            "is_activate": True
        }

        result = self.collection.insert_one(user)
        return str(result.inserted_id)
    
    def login(self, email: str) -> str:
        # check user exist (use find_one)
        user = self.collection.find_one({'email': email})
        
        # case 1: user not exist:
        # create: call create_user(email)
        if not user:
            return self.create_user(email)

        # case 2: user exist but deactivate
        # raise Error
        if user.get("is_activate") is not True:
            raise ValueError("This account is deactivated! Please connect to CS")

        # all checking passed
        return str(user.get("_id"))
    
    def deactivate(self, user_id: str) -> bool:
        # find and update:
        user = self.collection.find_one({
            "_id": ObjectId(user_id),
            "is_activate": True
        })

        # case: not exist user
        if not user:
            raise ValueError("User not found")
        
        # user is validate and ready to deactivate -> update them
        result = self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"is_activate": False}}
        )

        return result.modified_count > 0

    # =============================================
    # CASCADE DELETION - DATA LEAK PREVENTION
    # =============================================
    
    def get_user_data_summary(self, user_id: str) -> dict:
        """
        Get summary of user's data before deletion.
        Returns counts of transactions and categories.
        """
        user_oid = ObjectId(user_id)
        
        # Count transactions
        transaction_collection = self.db_manager.get_collection(config.COLLECTIONS['transaction'])
        transaction_count = transaction_collection.count_documents({"user_id": user_oid})
        
        # Count custom categories (excluding defaults)
        category_collection = self.db_manager.get_collection(config.COLLECTIONS['category'])
        default_categories = config.DEFAULT_CATEGORIES_EXPENSE + config.DEFAULT_CATEGORIES_INCOME
        
        category_count = category_collection.count_documents({
            "user_id": user_oid,
            "name": {"$nin": default_categories}
        })
        
        return {
            "transactions": transaction_count,
            "categories": category_count
        }
    
    def delete_user_cascade(self, user_id: str) -> dict:
        """
        Safely delete user and all related data.
        
        This prevents data leaks by ensuring all user data is removed:
        - All transactions belonging to the user
        - All custom categories created by the user (preserves system defaults)
        - The user document itself
        
        Args:
            user_id: The user ID to delete
            
        Returns:
            dict: Summary of deleted items
            {
                'user': 1,
                'transactions': 45,
                'categories': 2
            }
            
        Raises:
            ValueError: If user not found
        """
        user_oid = ObjectId(user_id)
        
        # Verify user exists
        user = self.collection.find_one({"_id": user_oid})
        if not user:
            raise ValueError("User not found")
        
        deletion_summary = {
            "user": 0,
            "transactions": 0,
            "categories": 0
        }
        
        try:
            # 1. Delete all user's transactions
            transaction_collection = self.db_manager.get_collection(config.COLLECTIONS['transaction'])
            transaction_result = transaction_collection.delete_many({"user_id": user_oid})
            deletion_summary["transactions"] = transaction_result.deleted_count
            
            # 2. Delete user's custom categories (preserve system defaults)
            category_collection = self.db_manager.get_collection(config.COLLECTIONS['category'])
            default_categories = config.DEFAULT_CATEGORIES_EXPENSE + config.DEFAULT_CATEGORIES_INCOME
            
            category_result = category_collection.delete_many({
                "user_id": user_oid,
                "name": {"$nin": default_categories}
            })
            deletion_summary["categories"] = category_result.deleted_count
            
            # 3. Delete the user document
            user_result = self.collection.delete_one({"_id": user_oid})
            deletion_summary["user"] = user_result.deleted_count
            
            return deletion_summary
            
        except Exception as e:
            raise Exception(f"Error during cascade deletion: {str(e)}")
    
    def get_user_by_id(self, user_id: str) -> dict:
        """Get user by ID"""
        try:
            return self.collection.find_one({"_id": ObjectId(user_id)})
        except Exception as e:
            print(f"Error getting user: {e}")
            return None