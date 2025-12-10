from pymongo import MongoClient
import random

MONGO_URI = "mongodb+srv://nguyenthuyduong9712_db_user:1EF4bSOaWR218z3k@cluster1.w1oaowb.mongodb.net/?appName=Cluster1"

client = MongoClient(MONGO_URI)
db = client["Finance_app_Duong"]
transaction = db["transaction"]

db.command("ping")
print("Database connected successfully")
print(f"Database names {db.name}")
print(f"Collection names {transaction.name}")

# #insert one
# print("======== Insert One Document ========")

# my_transaction = {
#     "type": "Wave"
#     , "amount": 1000
#     , "unit": "VND"

# }

# transaction.insert_one(my_transaction)
# print("Insert done")

#insert many
#transaction.insert_many(list[dict])

# TYPE = ["in", "out"]
# UNIT = ["VND"]

# multi_transaction = []
# for i in range(10):
#     fake_trans = {
#         "type": random.choice(TYPE),
#         "amount": random.randint(1, 10000),
#         "unit": "VND"
#     }
#     multi_transaction.append(fake_trans)

# #print (multi_transaction)

# result = transaction.insert_many(multi_transaction)
# print(f"Insert {len(result.inserted_ids)} transactions insrrted")
# print(f"Inserted IDs: {result.inserted_ids}")

#embeded docs
# my_emp_transaction = {
#     "type": "wave",
#     "amount": 1000,
#     "unit": "VND",
#     "detail": [
#         {
#             "item": "apple",
#             "qty": 10,
#             "discount": 0.1
#         },
#         {
#             "item": "rice",
#             "qty": 5,
#             "discount": 0.2
#         }
#     ]
# }
# transaction.insert_one(my_emp_transaction)
# print("Insert embedded document done")

print("="*60)
print("Read data")
print("="*60)
all_transaction = transaction.find() # Retrieve all documents from the 'transaction' collection
all_transaction = list(all_transaction)
print(f"Retrieved {len(all_transaction)} documents:")
for trans in all_transaction[:5]:
    print(trans.get("_id", "None"), end=" | ")
    print(trans.get("type", "Other type"), end=" | ")
    print(trans.get("amount", "No amount"), end="\n")

all_trans_in = transaction.find({"type": "in"})
all_trans_in = list(all_trans_in)
print(f"Retrieved {len(all_trans_in)} income documents:")
for trans_in in all_trans_in:
    print(trans_in)

# get docs with amount greater than 50, less than 100
high_value_transactions = transaction.find({"amount": {"$gt": 50, "$lt": 100}, "unit": "VND"})

#sắp xếp theo amount giảm dần
sorted_transactions = transaction.find().sort("amount", -1)

#top 3 giao dịch cao nhất 
top_3_transactions = transaction.find().sort("amount", -1).limit(3)
big_expenses = transaction.find({"type": "out"}).sort("amount", -1).limit(3)

print("Top 3 biggest expenses:")
#tìm giao dịch cần update
transaction_to_update = transaction.find_one({"category": "Food"})

#update amount and 







