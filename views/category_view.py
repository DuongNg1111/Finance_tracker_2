import streamlit as st
from datetime import datetime
import config
import time


# ---------------------------------------------------------
# RENDER DELETE CONFIRMATION POPUP
# ---------------------------------------------------------
def _render_delete_dialog(category_model):
    data = st.session_state["delete_category"]  # {type, name}

    cat_type = data["type"]
    cat_name = data["name"]
    cat_id = data["id"]  # use id from session_state
    reassign_key = f"reassign_mode_{cat_id}"
    if reassign_key not in st.session_state:
        st.session_state[reassign_key] = False

    st.write("### ⚠️ Confirm Delete")
    st.warning(
        f"Category **{cat_name}** has **{category_model.count_transactions_by_category(cat_type, cat_name)}** transactions."
    )

    colA, colB = st.columns([1, 1])

    # DELETE ALL
    with colA:
        # ✅ FIX: Use delete_key directly, not from session_state
        delete_key = f"delete_all_{cat_id}"
        
        if st.button("❌ Delete all", key=delete_key):
            category_model.delete_category_safe(
                category_type=cat_type,
                category_name=cat_name,
                strategy="Cascade"
            )
            st.success(f"Category '{cat_name}' deleted with all transactions.")
            if "delete_category" in st.session_state:
                del st.session_state["delete_category"]
            if reassign_key in st.session_state:
                del st.session_state[reassign_key]  
            st.rerun()

    # REASSIGN
    with colB:
        if st.button("🔄 Reassign Transactions", key=f"reassign_btn_{cat_id}"):
            st.session_state[reassign_key] = True

    # REASSIGN UI
    if st.session_state[reassign_key]:
        st.info("Select a category to move all transactions into:")
        other = category_model.get_other_categories(cat_type, cat_name)
        other_names = [o["name"] for o in other]

        if not other_names:
            st.error("No other categories available to reassign into.")
        else:
            new_cat = st.selectbox("New Category", other_names, key=f"reassign_select_{cat_id}")

            if st.button("💾 Change Category and Delete", key=f"reassign_delete_{cat_id}"):
                category_model.update_transactions_category(
                    old_name=cat_name,
                    new_name=new_cat,
                    category_type=cat_type
                )
                category_model.delete_category_safe(
                    category_type=cat_type,
                    category_name=cat_name,
                    strategy="Reassign",
                    new_category=new_cat
                )
                st.success(f"Moved all transactions → '{new_cat}' and deleted '{cat_name}'.")
                del st.session_state["delete_category"]
                del st.session_state[reassign_key]  
                st.rerun()

    # CANCEL BUTTON (outside the if block so it's always available)
    if st.button("Cancel", key=f"cancel_delete_{cat_id}"):
        del st.session_state["delete_category"]
        if reassign_key in st.session_state:
            del st.session_state[reassign_key]
        st.rerun()

# ---------------------------------------------------------
# CATEGORY LIST + DELETE + EDIT
# ---------------------------------------------------------
def _render_category_list(category_model, category_type: str):
    st.subheader(f"{category_type} Categories")

    category_lst = category_model.get_categories_by_type(category_type)

    if not category_lst:
        st.info("No categories found.")
        return

    DEFAULT = config.DEFAULT_CATEGORIES_EXPENSE + config.DEFAULT_CATEGORIES_INCOME

    for idx, item in enumerate(category_lst):
        st.write("---")

        name = item.get("name")
        created = item.get("created_at")

        with st.container():
            st.write(f"📌 **{name}**")
            if created:
                st.caption(f"Created at: {created.strftime('%d-%m-%Y')}")

        tx_count = category_model.count_transactions_by_category(category_type, name)

        cat_id = f"{category_type}_{name}_{idx}".replace(" ", "_")
        col1, col2 = st.columns([1, 1])

        # ---------------- DELETE BUTTON ----------------
        with col1:
            if name in DEFAULT:
                st.info("Default category")
            else:
                cat_id = f"{category_type}_{name}_{idx}".replace(" ", "_")
                del_btn_key = f"del_{cat_id}"  # stable unique key

                if st.button("❌ Delete", key=del_btn_key):
                    st.session_state["delete_category"] = {
                        "type": category_type,
                        "name": name,
                        "id": cat_id
                    }
                    st.session_state[f"reassign_mode_{cat_id}"] = False

        # ---------------- EDIT CATEGORY ----------------
        with col2:
            if name not in DEFAULT:
                with st.expander("✏️ Edit Category"):
                    with st.form(f"edit_form_{item['_id']}"):
                        new_name = st.text_input("New Name", value=name)

                        # Show warning inside form
                        if tx_count > 0:
                            st.warning(f"{tx_count} transactions will update to the new name.")

                        confirm = st.checkbox("I understand the changes")
                        save = st.form_submit_button("💾 Save")

                        if save:
                            if not confirm:
                                st.error("Please confirm first.")
                            else:
                                updated = category_model.rename_category(
                                    category_type, name, new_name
                                )
                                st.success(
                                    f"Renamed '{name}' → '{new_name}'. "
                                    f"{updated} transactions updated."
                                )
                                st.rerun()
        if "delete_category" in st.session_state:
            if st.session_state["delete_category"]["id"] == cat_id:
                with st.container():
                    st.write("")  # Small spacing
                    _render_delete_dialog(category_model)

# ---------------------------------------------------------
# RENDER CATEGORY TABS
# ---------------------------------------------------------
def _render_category_detail(category_model):
    st.subheader("Category Details")

    tab_exp, tab_inc = st.tabs(["Expense", "Income"])

    with tab_exp:
        _render_category_list(category_model, "Expense")
    with tab_inc:
        _render_category_list(category_model, "Income")

    # #Render dialog ONCE after both tabs
    # if "delete_category" in st.session_state:
    #     st.write("---")  # Visual separator
    #     _render_delete_dialog(category_model)

# ---------------------------------------------------------
# ADD CATEGORY
# ---------------------------------------------------------
def _render_add_category(category_model):
    st.subheader("Add New Category")

    with st.form("add_category_form"):
        col1, col2 = st.columns(2)

        cat_type = col1.selectbox("Category Type", config.TRANSACTION_TYPES)
        cat_name = col2.text_input("Category Name", placeholder="e.g., Groceries")

        add = st.form_submit_button("➕ Add Category")

        if add:
            if not cat_name:
                st.error("Please enter a category name.")
            else:
                category_model.upsert_category(cat_type, cat_name)
                st.success(f"Category '{cat_name}' created.")
                st.rerun()


# ---------------------------------------------------------
# MAIN RENDER FUNCTION
# ---------------------------------------------------------
def render_categories(category_model):
    st.title("🏷️ Category Management")

    _render_add_category(category_model)

    st.divider()
    
    _render_category_detail(category_model)