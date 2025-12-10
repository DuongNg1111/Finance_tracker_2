import streamlit as st
import config
from database.category_models import CategoryModel

#initialize models
@st.cache_resource
def init_models():
    return CategoryModel()

category = init_models()

#page configuration
st.set_page_config(
    page_title=config.APP_NAME,
    page_icon=":money_with_wings:",
    layout="wide"
)

#app title
st.title(config.APP_NAME)   

#overall    
st.header("Categories Overall")

col1, col2, col3 = st.columns(3)

with col1:
    st.text("Total Categories" )
    total = category.count_total()
    st.text("----")
with col2:
    st.text("Expense Categories" )
    st.text("----")
with col3:
    st.text("Income Categories" )
    st.text("----") 

st.divider()
