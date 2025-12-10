from datetime import datetime, timedelta, date
import streamlit as st

def format_currency(amount):
    """Format number as currency"""
    return f"${amount:,.2f}" #

def get_date_range_options():
    """Get predefined date range options"""
    today = datetime.now().date()
    
    return {
        "Today": (today, today),
        "Yesterday": (today - timedelta(days=1), today - timedelta(days=1)),
        "Last 7 Days": (today - timedelta(days=7), today),
        "Last 30 Days": (today - timedelta(days=30), today),
        "This Month": (today.replace(day=1), today),
        "Last Month": get_last_month_range(),
        "Last 3 Months": (today - timedelta(days=90), today),
        "Last 6 Months": (today - timedelta(days=180), today),
        "This Year": (today.replace(month=1, day=1), today),
        "All Time": (None, None)
    }

def get_last_month_range():
    """Get date range for last month"""
    today = datetime.now().date()
    first_day_this_month = today.replace(day=1)
    last_day_last_month = first_day_this_month - timedelta(days=1)
    first_day_last_month = last_day_last_month.replace(day=1)
    return (first_day_last_month, last_day_last_month)

def validate_amount(amount):
    """Validate amount input"""
    try:
        value = float(amount)
        if value <= 0:
            return False, "Amount must be greater than zero"
        return True, value
    except ValueError:
        return False, "Please enter a valid number"

def display_metric_card(title, value, delta=None, delta_color="normal"):
    """Display a metric card"""
    st.metric(
        label=title,
        value=value,
        delta=delta,
        delta_color=delta_color
    )

@st.cache_data(ttl=300)  # Cache for 5 minutes
def cached_data_fetch(func, *args, **kwargs):
    """Cache data fetching functions"""
    return func(*args, **kwargs)

def handler_datetime(date_: datetime | date | str) -> datetime:
    """Convert various date formats to datetime object"""
    if isinstance(date_, datetime):
        return date_
    elif isinstance(date_, date):
        return datetime.combine(date_, datetime.min.time())
    elif isinstance(date_, str):
        try:
            return datetime.fromisoformat(date_)
        except ValueError:
            raise ValueError("String date must be in ISO format (YYYY-MM-DD)")
    else:
        raise TypeError("Unsupported date type")
    
def format_date(date_obj: datetime) -> str:
    """Format datetime object to string"""
    return date_obj.strftime("%Y-%m-%d")