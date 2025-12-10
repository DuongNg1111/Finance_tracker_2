import streamlit as st
import config
from datetime import date, datetime, timedelta
import time
from utils import handler_datetime, format_currency, format_date
from database.transaction_model import TransactionModel
from database.category_models import CategoryModel

# -----------------------------
# Render single transaction
# -----------------------------
def _render_transaction_card(model: TransactionModel, category_model, item: dict):
    transaction_type = item.get('type', 'Unknown')
    amount = item.get('amount', 0)
    tx_date = item.get('date', datetime.now())
    category = item.get('category', 'Others')
    type_color = "🔴" if transaction_type == "Expense" else "🟢"
    amount_str = f"${amount:,.2f}"
    date_str = format_date(tx_date)
    header = f"{type_color} {date_str} | {category} | {amount_str}"

    with st.expander(header, expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Type:**", transaction_type)
            st.write("**Category:**", category)
            st.write("**Amount:**", amount_str)
        with col2:
            st.write("**Date:**", date_str)
            if item.get('description'):
                st.write("**Description:**", item['description'])
            if item.get('last_modified'):
                st.write("**Last Modified:**", format_date(item['last_modified']))
        
        st.divider()
        col_edit, col_delete, col_space = st.columns([1,1,3])
        with col_edit:
            if st.button("✏️ Edit", key=f"edit_{item['_id']}", use_container_width=True):
                st.session_state.editing_transaction = str(item['_id'])
                st.rerun()
        with col_delete:
            if st.button("🗑️ Delete", key=f"delete_{item['_id']}", use_container_width=True):
                if model.delete_transaction(str(item['_id'])):
                    st.success("Transaction deleted successfully!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Failed to delete transaction")
    
    # Show edit form RIGHT HERE if this transaction is being edited
    if st.session_state.get('editing_transaction') == str(item['_id']):
        with st.container():
            st.write("")  # Small spacing
            _render_edit_transaction_form(model, category_model, item)

# -----------------------------
# Filters
# -----------------------------
def _render_filters(transaction_model, category_model):
    st.subheader("🔍 Filters")

    col1, col2 = st.columns(2)

    with col1:
        transaction_type = st.selectbox(
            "Transaction Type",
            options=config.TRANSACTION_TYPES,
            key="filter_type",
        )

        min_amount = st.number_input(
            "Min Amount",
            min_value=0.0,
            value=0.0,
            step=10.0,
            key="filter_min_amount"
        )

        start_date = st.date_input(
            "Start Date",
            value=datetime.now() - timedelta(days=30),
            key="filter_start_date"
        )

    with col2:
        # Fetch categories depending on selected transaction type
        categories_result = category_model.get_categories_by_type(transaction_type)
        category_options = [c['name'] for c in categories_result]
        category = st.selectbox(
            "Category",
            options=["All"] + category_options,  # "All" = no filter
            key="filter_category"
        )

        max_amount = st.number_input(
            "Max Amount",
            min_value=0.0,
            value=0.0,
            step=10.0,
            key="filter_max_amount"
        )

        end_date = st.date_input(
            "End Date",
            value=datetime.now(),
            key="filter_end_date"
        )

    search_text = st.text_input(
        "Search in Description",
        key="filter_search_text"
    )

    col_apply, col_clear = st.columns(2)

    with col_apply:
        if st.button("✅ Apply Filters", use_container_width=True, type="primary"):
            filters = {}

            if transaction_type:
                filters['transaction_type'] = transaction_type

            if category and category != "All":
                filters['category'] = category

            # ✅ Only add amount filters if > 0
            if min_amount > 0:
                filters['min_amount'] = min_amount

            if max_amount > 0:
                filters['max_amount'] = max_amount

            if start_date:
                filters['start_date'] = start_date

            if end_date:
                filters['end_date'] = end_date

            if search_text:
                filters['search_text'] = search_text

            st.session_state.active_filters = filters if filters else None
            st.rerun()

    with col_clear:
        if st.button("🔄 Clear Filters", use_container_width=True):
            st.session_state.active_filters = None
            st.session_state.show_filters = False
            st.rerun()

# -----------------------------
# Create Transaction Form
# -----------------------------
def _render_create_transaction_form(transaction_model: TransactionModel, category_model):
    st.subheader("➕ Create New Transaction")
    col1, col2 = st.columns(2)
    with col1:
        transaction_type = st.selectbox("Type *", options=config.TRANSACTION_TYPES, key="create_type")
        amount = st.number_input("Amount *", min_value=0.1, value=1.0, step=1.0, format="%.2f", key="create_amount")
        date_input = st.date_input("Date *", value=datetime.now(), key="create_date")
    with col2:
        if transaction_type:
            categories_result = category_model.get_categories_by_type(transaction_type)
            category_options = [c['name'] for c in categories_result]
            category = st.selectbox("Category *", options=category_options, key="create_category")
        description = st.text_area("Description", key="create_description", placeholder="Optional notes")
    
    col_save, col_cancel = st.columns(2)
    with col_save:
        if st.button("💾 Save Transaction", use_container_width=True):
            if not category:
                st.error("Category is required"); return
            if amount <= 0:
                st.error("Amount must be greater than 0"); return
            transaction_date = datetime.combine(date_input, datetime.now().time())
            transaction_id = transaction_model.add_transaction(
                transaction_type=transaction_type,
                category=category,
                amount=amount,
                transaction_date=transaction_date,
                description=description
            )
            if transaction_id:
                st.success("✅ Transaction created successfully!")
                st.session_state.show_create_form = False
                # ✅ CLEAR FILTERS after adding new transaction
                st.session_state.active_filters = None
                st.rerun()
            else:
                st.error("❌ Failed to create transaction")
    with col_cancel:
        if st.button("❌ Cancel", use_container_width=True):
            st.session_state.show_create_form = False
            st.rerun()

# -----------------------------
# Edit Transaction Form
# -----------------------------
def _render_edit_transaction_form(transaction_model: TransactionModel, category_model, tx_item: dict):
    st.subheader("✏️ Edit Transaction")
    col1, col2 = st.columns(2)
    with col1:
        transaction_type = st.selectbox(
            "Type *",
            options=config.TRANSACTION_TYPES,
            index=config.TRANSACTION_TYPES.index(tx_item['type']),
            key=f"edit_type_{tx_item['_id']}"
        )
        amount = st.number_input("Amount *", min_value=0.1, value=tx_item['amount'], step=1.0, format="%.2f", key=f"edit_amount_{tx_item['_id']}")
        date_value = tx_item.get('date', datetime.now())
        date_input = st.date_input("Date *", value=date_value, key=f"edit_date_{tx_item['_id']}")
    with col2:
        categories_result = category_model.get_categories_by_type(transaction_type)
        category_options = [c['name'] for c in categories_result]
        category = st.selectbox(
            "Category *",
            options=category_options,
            index=category_options.index(tx_item['category']) if tx_item['category'] in category_options else 0,
            key=f"edit_category_{tx_item['_id']}"
        )
        description = st.text_area("Description", value=tx_item.get('description',''), key=f"edit_description_{tx_item['_id']}")
    
    col_save, col_cancel = st.columns(2)
    with col_save:
        if st.button("💾 Save Changes", key=f"save_{tx_item['_id']}", use_container_width=True):
            transaction_date = datetime.combine(date_input, datetime.now().time())
            success = transaction_model.update_transaction(
                transaction_id=str(tx_item['_id']),
                type=transaction_type,
                category=category,
                amount=amount,
                date=transaction_date,
                description=description
            )
            if success:
                st.success("Transaction updated successfully!")
                st.session_state.editing_transaction = None
                st.rerun()
            else:
                st.error("Failed to update transaction")
    with col_cancel:
        if st.button("❌ Cancel", key=f"cancel_{tx_item['_id']}", use_container_width=True):
            st.session_state.editing_transaction = None
            st.rerun()

# -----------------------------
# Initialize session state
# -----------------------------
def initialize_session_state():
    if 'show_filters' not in st.session_state: st.session_state.show_filters = False
    if 'active_filters' not in st.session_state: st.session_state.active_filters = None
    if 'show_create_form' not in st.session_state: st.session_state.show_create_form = False
    if 'editing_transaction' not in st.session_state: st.session_state.editing_transaction = None

# -----------------------------
# Render list of transactions
# -----------------------------
def _render_list_transaction(transaction_model: TransactionModel, category_model):
    
    # Get filtered transactions
    transactions = transaction_model.get_transactions(
        advanced_filters=st.session_state.active_filters
    )
    
    # Show transaction count
    if st.session_state.active_filters:
        filter_count = len(st.session_state.active_filters)
        transaction_count = len(transactions)
        st.info(f"👉 Found {transaction_count} transaction(s)")
    else:
        st.info(f"📊 Total: {len(transactions)} transaction(s)")
    
    if not transactions:
        if st.session_state.active_filters:
            st.warning("⚠️ No transactions match your filters. Try adjusting them or click 'Show All' above.")
        else:
            st.info("No transactions found. Add your first transaction to get started!")
    else:
        for item in transactions:
            _render_transaction_card(transaction_model, category_model, item)

# -----------------------------
# Main render function
# -----------------------------
def render_transactions(transaction_model, category_model):
    initialize_session_state()
    
    if not getattr(transaction_model, 'user_id', None):
        st.warning("Please log in to view your transactions.")
        return
    
    # title
    col_title, col_create, col_filter = st.columns([2.5, 2, 2])
    with col_title: 
        st.title("📝 Transactions")
    with col_create:
        if st.button("➕ ADD", use_container_width=True):
            st.session_state.show_create_form = not st.session_state.show_create_form
            st.rerun()
    with col_filter:
        if st.button("🔍 Filters", use_container_width=True):
            st.session_state.show_filters = not st.session_state.show_filters
            st.rerun()
   
    if st.session_state.show_create_form:
        _render_create_transaction_form(transaction_model, category_model)
        st.divider()
    
    if st.session_state.show_filters:
        _render_filters(transaction_model, category_model)
        st.divider()
    
    _render_list_transaction(transaction_model, category_model)