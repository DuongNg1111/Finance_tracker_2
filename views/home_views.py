import streamlit as st
import pandas as pd
import time
from utils import format_currency, get_date_range_options
from analytics.analyzer import FinanceAnalyzer
from analytics.visualizer import FinanceVisualizer
from database.transaction_model import TransactionModel

# ------------------------------
# Main Dashboard Renderer
# ------------------------------
def render_dashboard(analyzer_model: FinanceAnalyzer, 
                     transaction_model: TransactionModel,
                     visualizer_model: FinanceVisualizer):
    """
    Render the main financial dashboard.
    
    Args:
        analyzer_model: FinanceAnalyzer
        transaction_model: TransactionModel
        visualizer_model: FinanceVisualizer
    """
    st.title("📊 Financial Dashboard")
    
    # Date range selector
    col1, _ = st.columns([2, 1])
    with col1:
        date_range_option = st.selectbox(
            "Select Date Range",
            list(get_date_range_options().keys()),
            index=3  # Default to "Last 30 Days"
        )
    
    date_ranges = get_date_range_options()
    start_date, end_date = date_ranges[date_range_option]

    # Display metrics
    _render_metrics(analyzer_model, start_date, end_date)
    st.divider()
    
    # Display charts
    _render_charts(analyzer_model, visualizer_model, start_date, end_date)
    st.divider()
    
    # Optional: Display recent transactions
    _render_recent_transactions(transaction_model)


# ------------------------------
# Metrics Section
# ------------------------------
def _render_metrics(analyzer_model: FinanceAnalyzer, start_date, end_date):
    """Render the metrics cards at the top of dashboard"""
    total_expenses = analyzer_model.calculate_total_by_type("Expense", start_date, end_date)
    total_income = analyzer_model.calculate_total_by_type("Income", start_date, end_date)
    net_balance = total_income - total_expenses
    daily_avg = analyzer_model.get_daily_average()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("💸 Total Expenses", format_currency(total_expenses))
    with col2:
        st.metric("💰 Total Income", format_currency(total_income))
    with col3:
        delta_color = "normal" if net_balance >= 0 else "inverse"
        st.metric("📈 Net Balance", format_currency(net_balance), delta_color=delta_color)
    with col4:
        st.metric("📅 Daily Avg Expense", format_currency(daily_avg))


# ------------------------------
# Charts Section
# ------------------------------
def _render_charts(analyzer_model: FinanceAnalyzer, visualizer_model: FinanceVisualizer, start_date, end_date):
    """Render category and trend charts"""
    col1, col2 = st.columns(2)

    # Spending by category
    with col1:
        st.subheader("Spending by Category")
        category_spending = analyzer_model.get_spending_by_category(start_date, end_date)
        if not category_spending.empty:
            fig = visualizer_model.plot_category_spending(category_spending)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No expense data available for this period")

    # Pie chart
    with col2:
        st.subheader("Category Breakdown")
        if not category_spending.empty:
            fig = visualizer_model.plot_pie_chart(category_spending)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No expense data available for this period")

    # Monthly trend
    st.subheader("Monthly Trend")
    monthly_trend = analyzer_model.get_monthly_trend(months=6)
    if not monthly_trend.empty:
        fig = visualizer_model.plot_monthly_trend(monthly_trend)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data available for monthly trend")


# ------------------------------
# Recent Transactions (optional)
# ------------------------------
def _render_recent_transactions(transaction_model: TransactionModel):
    """Render the recent transactions table"""
    st.subheader("Recent Transactions")
    recent = transaction_model.get_transactions()

    if recent:
        df_recent = pd.DataFrame(recent)
        df_recent['date'] = pd.to_datetime(df_recent['date']).dt.date
        df_recent['amount'] = df_recent['amount'].apply(format_currency)
        st.dataframe(
            df_recent[['date', 'type', 'category', 'amount', 'description']],
            use_container_width=True
        )
    else:
        st.info("No transactions yet")


# ------------------------------
# initializing models and running dashboard
# ------------------------------
if __name__ == "__main__":
    # Initialize models
    transaction_model = TransactionModel()
    analyzer_model = FinanceAnalyzer(transaction_model)
    visualizer_model = FinanceVisualizer()

    # Render the dashboard
    render_dashboard(
        analyzer_model=analyzer_model,
        transaction_model=transaction_model,
        visualizer_model=visualizer_model
    )
