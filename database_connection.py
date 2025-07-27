import duckdb
import streamlit as st
import threading

# Thread-local storage for database connections
_local = threading.local()

def get_db_connection():
    """Get a database connection for the current thread/page"""
    if not hasattr(_local, 'db_connection') or _local.db_connection is None:
        try:
            _local.db_connection = duckdb.connect('job_market_std_employer.duckdb', read_only=True)
        except Exception as e:
            st.error(f"Error connecting to database: {e}")
            return None
    
    return _local.db_connection

def close_db_connection():
    """Close the database connection for the current thread"""
    if hasattr(_local, 'db_connection') and _local.db_connection is not None:
        try:
            _local.db_connection.close()
            _local.db_connection = None
        except Exception as e:
            st.error(f"Error closing database connection: {e}")

def reset_db_connection():
    """Reset the database connection (useful for troubleshooting)"""
    close_db_connection()
    return get_db_connection() 