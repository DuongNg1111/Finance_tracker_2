import os 
import streamlit as st
from dotenv import load_dotenv 

load_dotenv() 
APP_NAME = "FINANCE-TRACKER" 

# Mongo configuration - compatible with both local and Streamlit Cloud
try:
    MONGO_URI = st.secrets["MONGO_URI"]
except (FileNotFoundError, KeyError):
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")

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
