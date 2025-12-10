import streamlit as st


def render_user_profile(user_model, user: dict):
    """Render user profile with logout, deactivate, and delete account options"""
    
    with st.sidebar:
        st.divider()
        
        # =============================================
        # PROFILE SECTION - CENTERED & STYLED
        # =============================================
        
        # Center the profile picture
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if user.get('picture'):
                st.image(user['picture'], use_container_width=True)
        
        # Center and style the name
        st.markdown(
            f"<h3 style='text-align: center; margin-top: 10px; margin-bottom: 5px;'>{user.get('name', 'N/A')}</h3>",
            unsafe_allow_html=True
        )
        
        # Center the email
        st.markdown(
            f"<p style='text-align: center; color: #666; font-size: 14px; margin-bottom: 20px;'>{user.get('email', 'N/A')}</p>",
            unsafe_allow_html=True
        )
        
        st.divider()
        
        # =============================================
        # LOGOUT BUTTON
        # =============================================
        if st.button("🚪 Logout", use_container_width=True, type="secondary"):
            st.logout()
        
        st.divider()
        
        # =============================================
        # DEACTIVATE ACCOUNT BUTTON
        # =============================================
        with st.expander("⚠️ Deactivate Account"):
            st.warning("This will temporarily disable your account. You can reactivate by logging in again.")
            
            if st.button("Deactivate My Account", type="secondary", key="deactivate_btn"):
                try:
                    success = user_model.deactivate(user['id'])
                    if success:
                        st.success("Account deactivated successfully!")
                        st.logout()
                    else:
                        st.error("Failed to deactivate account.")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        
        # =============================================
        # DELETE ACCOUNT BUTTON - DATA LEAK PREVENTION
        # =============================================
        with st.expander("🗑️ Delete Account Permanently"):
            st.error("⚠️ **WARNING: This action cannot be undone!**")
            
            # Get data summary
            try:
                summary = user_model.get_user_data_summary(user['id'])
                
                st.markdown("**This will permanently delete:**")
                st.write(f"• Your user account")
                st.write(f"• **{summary['transactions']}** transactions")
                st.write(f"• **{summary['categories']}** custom categories")
                
                st.divider()
                
                # Initialize delete confirmation state
                if 'delete_account_confirm' not in st.session_state:
                    st.session_state.delete_account_confirm = False
                
                # Confirmation checkbox
                confirm = st.checkbox(
                    "I understand this will permanently delete all my data",
                    key="delete_account_checkbox"
                )
                
                # Delete button - only enabled if confirmed
                if st.button(
                    "🔴 DELETE MY ACCOUNT",
                    type="primary",
                    disabled=not confirm,
                    use_container_width=True,
                    key="delete_btn_1"
                ):
                    st.session_state.delete_account_confirm = True
                
                # Show final confirmation dialog
                if st.session_state.delete_account_confirm:
                    st.divider()
                    st.error("### 🚨 FINAL CONFIRMATION")
                    st.write("Are you absolutely sure? This cannot be undone.")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button("Cancel", use_container_width=True, key="cancel_delete"):
                            st.session_state.delete_account_confirm = False
                            st.rerun()
                    
                    with col2:
                        if st.button("Yes, Delete", type="primary", use_container_width=True, key="confirm_delete"):
                            try:
                                # Perform cascade deletion
                                result = user_model.delete_user_cascade(user['id'])
                                
                                # Show success message
                                st.success(
                                    f"✅ **Account Deleted**\n\n"
                                    f"Deleted: {result['user']} user, "
                                    f"{result['transactions']} transactions, "
                                    f"{result['categories']} categories"
                                )
                                
                                # Wait a moment then logout
                                import time
                                time.sleep(2)
                                st.logout()
                                
                            except Exception as e:
                                st.error(f"❌ Error: {str(e)}")
                                st.session_state.delete_account_confirm = False
                
            except Exception as e:
                st.error(f"Error loading data: {str(e)}")