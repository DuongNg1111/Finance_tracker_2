import os 
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

APP_NAME = "FINANCE-TRACKER" 

def get_mongo_uri():
    # Force the correct URI directly
    uri = "mongodb+srv://nguyenthuyduong9712_db_user:Duong2025@cluster1.w1oaowb.mongodb.net/finance_tracker_db?retryWrites=true&w=majority"
    print(f"--- DEBUG: Connecting to MongoDB with user: nguyenthuyduong9712_db_user ---")
    return uri

MONGO_URI_FINAL = get_mongo_uri()
DATABASE_NAME = "finance_tracker_db"

COLLECTIONS = { 
    "user": "users", 
    "transaction": "transactions", 
    "category": "categories", 
    "budget": "budgets" 
} 

TRANSACTION_TYPES = ['Expense', "Income"] 
DEFAULT_CATEGORIES_EXPENSE = ["Groceries", "Transportation", "Housing", "Food", "Bills"] 
DEFAULT_CATEGORIES_INCOME = ["Salary", "Freelance", "Gift", "Bonus"]
