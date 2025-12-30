def _initialize(self):
    import streamlit as st
    
    try:
        if "mongo" in st.secrets:
            mongo_uri = st.secrets["mongo"]["MONGO_URI"]
        else:
            mongo_uri = config.MONGO_URI_FINAL
    except:
        mongo_uri = config.MONGO_URI_FINAL

    print(f"Connecting to MongoDB...") 

    self.client = MongoClient(mongo_uri)
    db_name = "finance_tracker_db" 
    self.db = self.client[db_name]
    
    try:
        self.client.admin.command('ping')
        print("MongoDB Connected Successfully!")
        self._create_index()
    except Exception as e:
        print(f"Connection Failed: {e}")
        raise e
