import os 
from dotenv import load_dotenv 

load_dotenv() 
APP_NAME = "FINANCE-TRACKER" 
# mongo configuration 
MONGO_URI = os.getenv("MONGO_URI", "localhost:2017") 
DATABASE_NAME = "finance_tracker" 
# collections 
COLLECTIONS = { 
    "user": "users", 
    "transaction": "transactions", 
    "category": "categories", 
    "budget": "budgets" } 

# transaction types
 
TRANSACTION_TYPES = ['Expense', "Income"] 

#categories of expense
DEFAULT_CATEGORIES_EXPENSE = [ "Shopping", "Transportation", "Entertainment", "Others" ] 

#categories of Income
DEFAULT_CATEGORIES_INCOME = [ "Salary", "Freelance", "Gift/Voucher" ]