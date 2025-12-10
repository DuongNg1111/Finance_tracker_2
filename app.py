import streamlit as st
import config

# import model
from database.category_models import CategoryModel
from database.transaction_model import TransactionModel
from database.user_model import UserModel

# import analytics
from analytics.analyzer import FinanceAnalyzer
from analytics.visualizer import FinanceVisualizer

# import view module
from views.category_view import render_categories
from views.transaction_view import render_transactions
from views.user_view import render_user_profile
from views.home_views import render_dashboard

# initialize models
@st.cache_resource
def init_models():
    """Initialize and cached models"""
    return {
        "category": CategoryModel(),
        "transaction": TransactionModel(),
        "user": UserModel(),
    }

# initialize session per user
if "models" not in st.session_state:
    # initialize models
    st.session_state['models'] = init_models()


models = st.session_state['models']

# Page configuration
st.set_page_config(
    page_title = "Personal Finance Tracking",
    page_icon = "📊",
    layout = "wide"
)

# =============================================
# CUSTOM CSS FOR BETTER NAVIGATION
# =============================================
st.markdown("""
<style>
    /* Navigation styling */
    div[data-testid="stSidebar"] {
        background-color: #f8f9fa;
    }
    
    /* Radio buttons - larger and cleaner */
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
    
    /* Selected radio button */
    div[role="radiogroup"] label:has(input[type="radio"]:checked) {
        background-color: #ff4b4b !important;
        color: white !important;
        border-color: #ff4b4b !important;
        font-weight: 600 !important;
    }
    
    /* Radio button text */
    div[role="radiogroup"] label span {
        font-size: 16px !important;
        font-weight: 500 !important;
    }
    
    /* Selected radio button text */
    div[role="radiogroup"] label:has(input[type="radio"]:checked) span {
        color: white !important;
    }
    
    /* Hide radio circles */
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
# 1. Authen User
# =============================================

def login_screen():
    with st.container():
        st.header("This app is private")
        st.subheader("Please login to continue")
        st.button("Login with Google", on_click = st.login)


if not st.user.is_logged_in:
    login_screen()
else:
    # Get mongo_user
    user_model: UserModel = models['user']
    try:
        mongo_user_id = user_model.login(st.user.email)
    except Exception as e:
        st.error(f"Error during user login: {e}")
        st.stop()

    # set user_id for models
    # currently we have category and transaction models
    # you can optimize this by doing it in the model init function
    models['category'].set_user_id(mongo_user_id)
    models['transaction'].set_user_id(mongo_user_id)


    user = st.user.to_dict() # convert google_user to dict
    user.update({
        "id": mongo_user_id
    })

    # Display user profile after update user with mongo_user_id
    render_user_profile(user_model, user)

    # init analyzer
    # because transaction_model has set user_id already in line 74
    analyzer_model = FinanceAnalyzer(models['transaction'])

    # =============================================
    # 2. Navigation
    # =============================================

    # Navigation header
    st.sidebar.markdown("<div class='nav-header'>📊 Navigation</div>", unsafe_allow_html=True)
    
    # Navigation radio with better styling
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
        # get category_model and transaction from models
        category_model = models['category']
        transaction_model = models['transaction']

        # display transaction views
        render_transactions(transaction_model=transaction_model, category_model=category_model)

    elif page == "🏷️ Category":
        # get category_model from models
        category_model = models['category']
        print(list(category_model.collection.find()))
        
        # display category views
        render_categories(category_model=category_model)