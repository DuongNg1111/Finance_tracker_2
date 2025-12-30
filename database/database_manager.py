from pymongo import MongoClient, DESCENDING
import streamlit as st
import os
import sys

# Đảm bảo nhận diện được file config.py ở thư mục gốc
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    import config
except ImportError:
    config = None

class DatabaseManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        # 1. Lấy URI từ Streamlit Secrets (Ưu tiên trên Web) hoặc file Config (Local)
        mongo_uri = None
        try:
            if "mongo" in st.secrets:
                mongo_uri = st.secrets["mongo"]["MONGO_URI"]
        except:
            pass
            
        if not mongo_uri and config:
            mongo_uri = config.MONGO_URI_FINAL

        # 2. Kết nối
        print(f"Connecting to MongoDB...") 
        self.client = MongoClient(mongo_uri)
        self.db = self.client["finance_tracker_db"]
        
        try:
            # Kiểm tra kết nối thực tế
            self.client.admin.command('ping')
            print("MongoDB Connected Successfully!")
            self._create_index()
        except Exception as e:
            print(f"Connection Failed: {e}")
            raise e

    def _create_index(self):
        """Tạo index để tăng tốc độ truy vấn"""
        try:
            self.db.transactions.create_index([("user_id", DESCENDING), ("date", DESCENDING)])
        except:
            pass

    def get_collection(self, collection_name: str):
        return self.db[collection_name]

    def close_connection(self):
        if self.client:
            self.client.close()
