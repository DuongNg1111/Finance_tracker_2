# from database.transaction_model import TransactionModel
# from datetime import date

# if __name__ == "__main__":
#     #init model
#     Transaction_model = TransactionModel()

#     # # define params:
#     # transaction_type = "Income"
#     # category = "Shopping"
#     # amount = 789
#     # transaction_date = date.today()

#     # new_transaction = Transaction_model.add_transaction(
#     #     transaction_type= transaction_type,
#     #     category= category,
#     #     amount= amount,
#     #     transaction_date= transaction_date,
#     #     description= "TEST"
#     # )
#     # print(f"New transaction inserted with id: {new_transaction}")

#     #test delete
#     result = Transaction_model.delete_trasaction("6925b9764900fed8f4bbd053")
#     print(f"Deleted count: {result+1}")

# import streamlit
# import authlib
# import dotenv
# import matplotlib
# import pandas
# import plotly
# import pymongo

# print("streamlit:", streamlit.__version__)
# print("authlib:", authlib.__version__)
# # print("python-dotenv:", dotenv.__version__)
# print("matplotlib:", matplotlib.__version__)
# print("pandas:", pandas.__version__)
# print("plotly:", plotly.__version__)
# print("pymongo:", pymongo.__version__)
# import importlib

# modules = ["streamlit", "python-dotenv", "pandas", "numpy", "altair", "pyarrow"]
# for m in modules:
#     try:
#         importlib.import_module(m)
#         print(f"{m} ✅ đã cài")
#     except ModuleNotFoundError:
#         print(f"{m} ❌ chưa cài")