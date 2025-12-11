import os 
import streamlit as st
from dotenv import load_dotenv 

load_dotenv() 
APP_NAME = "FINANCE-TRACKER" 

# Mongo configuration - compatible with both local and Streamlit Cloud
def get_mongo_uri():
    try:
        return st.secrets["mongo"]["MONGO_URI"]
    except (FileNotFoundError, KeyError, AttributeError):
        env_uri = os.getenv("MONGO_URI")
        if not env_uri:
            raise ValueError("MongoDB Atlas URI not found in st.secrets or environment variables.")
        return env_uri


MONGO_URI_FINAL = get_mongo_uri()

DATABASE_NAME = "finance_tracker_db"
COLLECTIONS = { 
    "user": "users", 
    "transaction": "transactions", 
    "category": "categories", 
    "budget": "budgets" 
} 

TRANSACTION_TYPES = ['Expense', "Income"] 
DEFAULT_CATEGORIES_EXPENSE = ["Groceries", "Transportation", "Housing"]
DEFAULT_CATEGORIES_INCOME = ["Salary", "Freelance", "Gift/Voucher"]
