import os 
import streamlit as st
from dotenv import load_dotenv

# Load .env file FIRST
load_dotenv()

APP_NAME = "FINANCE-TRACKER" 

# Mongo configuration - prioritize .env file for local development
def get_mongo_uri():
    # First try environment variable (from .env file) - LOCAL DEVELOPMENT
    env_uri = os.getenv("MONGO_URI")
    if env_uri:
        print("✓ Using MONGO_URI from .env file")
        return env_uri
    
    # Then try Streamlit secrets (for deployment only)
    try:
        secrets_uri = st.secrets["mongo"]["MONGO_URI"]
        print("✓ Using MONGO_URI from Streamlit secrets")
        return secrets_uri
    except (FileNotFoundError, KeyError, AttributeError):
        pass
    
    # If neither found, raise error
    raise ValueError(
        "MongoDB URI not found!\n"
        "For local development: Add MONGO_URI to your .env file\n"
        "For Streamlit Cloud: Add MONGO_URI to secrets.toml"
    )

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
