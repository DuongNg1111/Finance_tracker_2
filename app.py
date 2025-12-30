import streamlit as st
import config     

# import models
from database.category_model import CategoryModel
from database.transaction_model import TransactionModel
from database.user_model import UserModel

# import analytics
from analytics.analyzer import FinanceAnalyzer
from analytics.visualizer import FinanceVisualizer

# import view modules
from views.category_view import render_categories
from views.transaction_view import render_transactions
from views.user_view import render_user_profile
from views.home_views import render_dashboard

# initialize models
@st.cache_resource
def init_models():
    """Initialize and cache models"""
    return {
        "category": CategoryModel(),
        "transaction": TransactionModel(),
        "user": UserModel(),
    }

# initialize session per user
if "models" not in st.session_state:
    st.session_state['models'] = init_models()

models = st.session_state['models']

# Page configuration
st.set_page_config(
    page_title="Personal Finance Tracking",
    page_icon="📊",
    layout="wide"
)

# =============================================
# CUSTOM CSS FOR BETTER NAVIGATION
# =============================================
st.markdown("""
<style>
    /* Sidebar background */
    div[data-testid="stSidebar"] {
        background-color: #f8f9fa;
    }

    /* Radio buttons styling */
    div[role="radiogroup"] label {
        padding: 12px 16px !important;
        border-radius: 8px !important;
        margin: 4px 0 !important;
        transition: all 0.2s ease !important;
        background-color: white !important;
        border: 1px solid #e0e0e0 !important;
    }

    div[role="radiogroup"] label:hover {
        background-color: #f0f2f6 !important;
        border-color: #ff4b4b !important;
    }

    div[role="radiogroup"] label:has(input[type="radio"]:checked) {
        background-color: #ff4b4b !important;
        color: white !important;
        border-color: #ff4b4b !important;
        font-weight: 600 !important;
    }

    div[role="radiogroup"] label span {
        font-size: 16px !important;
        font-weight: 500 !important;
    }

    div[role="radiogroup"] label:has(input[type="radio"]:checked) span {
        color: white !important;
    }

    div[role="radiogroup"] label input[type="radio"] {
        display: none !important;
    }

    /* Navigation header */
    .nav-header {
        text-align: center;
        font-size: 20px;
        font-weight: 700;
        color: #262730;
        margin-bottom: 20px;
        padding: 10px 0;
        border-bottom: 2px solid #ff4b4b;
    }
</style>
""", unsafe_allow_html=True)

# =============================================
# 1. Authenticate User
# =============================================
def login_screen():
    with st.container():
        st.header("This app is private")
        st.subheader("Please login to continue")
        st.button("Login with Google", on_click=st.login)

if not hasattr(st, 'user') or getattr(st.user, 'email', None) is None:
    login_screen()
    st.stop()
else:
    # Get mongo_user
    user_model: UserModel = models['user']
    try:
        mongo_user_id = user_model.login(st.user.email)
    except Exception as e:
        st.error(f"Error during user login: {e}")
        st.stop()

    # set user_id for models
    models['category'].set_user_id(mongo_user_id)
    models['transaction'].set_user_id(mongo_user_id)

    user = st.user.to_dict()
    user.update({"id": mongo_user_id})

    # Display user profile
    render_user_profile(user_model, user)

    # init analyzer
    analyzer_model = FinanceAnalyzer(models['transaction'])

    # =============================================
    # 2. Navigation
    # =============================================
    st.sidebar.markdown("<div class='nav-header'>📊 Navigation</div>", unsafe_allow_html=True)

    page = st.sidebar.radio(
        "nav",
        ["🏠 Home", "📝 Transaction", "🏷️ Category"],
        label_visibility="collapsed"
    )

    # =============================================
    # 3. Router
    # =============================================
    if page == "🏠 Home":
        st.title("Home")
        visualizer_model = FinanceVisualizer
        render_dashboard(
            analyzer_model=analyzer_model,
            transaction_model=models['transaction'],
            visualizer_model=visualizer_model
        )
    elif page == "📝 Transaction":
        category_model = models['category']
        transaction_model = models['transaction']
        render_transactions(transaction_model=transaction_model, category_model=category_model)
    elif page == "🏷️ Category":
        category_model = models['category']
        print(list(category_model.collection.find()))
        render_categories(category_model=category_model)
