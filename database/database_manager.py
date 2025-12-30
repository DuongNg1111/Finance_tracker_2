from pymongo import MongoClient, DESCENDING
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

class DatabaseManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
        
    def _initialize(self):
        import streamlit as st
        
        # 1. Thử lấy URI từ Streamlit Secrets trước (Dành cho bản Web)
        try:
            mongo_uri = st.secrets["mongo"]["MONGO_URI"]
        except:
            # 2. Nếu không có Secrets (chạy ở máy), mới dùng file config
            mongo_uri = config.MONGO_URI_FINAL

        # Kết nối với URI đã tìm được
        self.client = MongoClient(mongo_uri)
        
        # Ép dùng đúng database name (bạn có thể thay thẳng tên vào đây cho chắc)
        db_name = "finance_tracker_db" 
        self.db = self.client[db_name]
        
        try:
            # Kiểm tra kết nối
            self.client.admin.command('ping')
            print("Kết nối MongoDB thành công!")
            self._create_index()
        except Exception as e:
            print(f"Lỗi kết nối: {e}")
            raise e
        
    def _create_index(self):
        "Create indexes for better performance"
        self.db.transactions.create_index([("user_id", DESCENDING), ("date", DESCENDING)])
        self.db.categories.create_index([("user_id", DESCENDING),
                                           ("type", DESCENDING),
                                           ("name", DESCENDING)], unique = True)
        
    def get_collection(self, collection_name: str):
        """Get a collection from db"""
        return self.db[collection_name]
    
    def close_connection(self):
        """Close db connection"""
        if self.client:
            self.client.close()
            print("Shutdown database connection")


if __name__=="__main__":

    # init db
    test_db = DatabaseManager()

    # collections
    collection_name = "users"
    user_collection = test_db.get_collection(collection_name=collection_name)
    test_db.close_connection()
