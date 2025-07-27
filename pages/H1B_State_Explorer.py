import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
import gc

# Set page config
st.set_page_config(page_title="H-1B State-Level Explorer", layout="wide")

# Database configuration
DB_FILE = 'job_market_std_employer.duckdb'
TABLE = 'job_market_data_aggressive_normalized'

from database_connection import get_db_connection

def get_state_filter_options():
    """Get filter options for state-level analysis"""
    try:
        con = get_db_connection()
        if con is None:
            return [], [], []
        
        # Load only necessary data
        states = con.execute(f"SELECT DISTINCT EMPLOYER_STATE FROM {TABLE} WHERE VISA_CLASS = 'H-1B' AND is_lottery_petition = TRUE AND EMPLOYER_STATE IS NOT NULL ORDER BY EMPLOYER_STATE").fetchdf()['EMPLOYER_STATE'].tolist()
        years = con.execute(f"SELECT DISTINCT YEAR FROM {TABLE} WHERE VISA_CLASS = 'H-1B' AND is_lottery_petition = TRUE ORDER BY YEAR").fetchdf()['YEAR'].tolist()
        soc_titles = con.execute(f"SELECT DISTINCT aggressive_normalized_soc_title FROM {TABLE} WHERE VISA_CLASS = 'H-1B' AND is_lottery_petition = TRUE AND aggressive_normalized_soc_title IS NOT NULL AND aggressive_normalized_soc_title NOT LIKE '%Other%' ORDER BY aggressive_normalized_soc_title").fetchdf()['aggressive_normalized_soc_title'].tolist()
        
        gc.collect()
        return states, years, soc_titles
    except Exception as e:
        st.error(f"Failed to load filter options: {e}")
        return [], [], []

def get_state_filtered_data(state, year, soc_title):
    """Get filtered data for state-level analysis"""
    with st.spinner("Loading state data..."):
        try:
            con = get_db_connection()
            query = f"SELECT * FROM {TABLE} WHERE VISA_CLASS = 'H-1B' AND is_lottery_petition = TRUE"
            params = []
            
            if state and state != 'All':
                query += " AND EMPLOYER_STATE = ?"
                params.append(state)
            if year:
                query += " AND YEAR = ?"
                params.append(year)
            if soc_title and soc_title != 'All':
                query += " AND aggressive_normalized_soc_title = ?"
                params.append(soc_title)
            
            # Filter out any job categories containing "Other" like in trends analysis
            query += " AND aggressive_normalized_soc_title NOT LIKE '%Other%'"
            
            df = con.execute(query, params).fetchdf()
            gc.collect()
            return df
        except Exception as e:
            st.error(f"Failed to load state data: {e}")
            return pd.DataFrame()

def get_job_titles(state, soc_title, year):
    """Get job titles for state-level analysis"""
    with st.spinner("Loading job titles..."):
        try:
            con = get_db_connection()
            query = f"SELECT DISTINCT NORMALIZED_JOB_TITLE FROM {TABLE} WHERE VISA_CLASS = 'H-1B' AND is_lottery_petition = TRUE AND NORMALIZED_JOB_TITLE IS NOT NULL"
            params = []
            
            if state and state != 'All':
                query += " AND EMPLOYER_STATE = ?"
                params.append(state)
            if soc_title and soc_title != 'All':
                query += " AND aggressive_normalized_soc_title = ?"
                params.append(soc_title)
            if year:
                query += " AND YEAR = ?"
                params.append(year)
            
            # Filter out any job categories containing "Other" like in trends analysis
            query += " AND aggressive_normalized_soc_title NOT LIKE '%Other%'"
            query += " ORDER BY NORMALIZED_JOB_TITLE"
            job_titles = con.execute(query, params).fetchdf()['NORMALIZED_JOB_TITLE'].tolist()
            gc.collect()
            return job_titles
        except Exception as e:
            st.error(f"Failed to load job titles: {e}")
            return []

# ============================================================================
# MAIN PAGE CONTENT
# ============================================================================

# Main page content
st.title("🗺️ H-1B State-Level Explorer")
st.markdown("**Lightweight state-specific analysis tool for H-1B lottery petition data - quick insights on petition volume, wage distribution, and top occupations**")

# Main page tooltip
st.info("💡 **H-1B State-Level Explorer**: This lightweight page provides essential state-level insights for H-1B data analysis. Use the sidebar filters to focus on specific states, years, or job categories.")

# Sidebar filters
st.sidebar.header("Filters")

# Load filter options
states, years, soc_titles = get_state_filter_options()

# Priority states for analysis (high H-1B volumes)
priority_states = [
    # Tech Hubs
    "CA", "WA", "NY", "TX", "MA", "IL", "VA", "GA", "NC", "PA",
    # Growing Tech Markets
    "CO", "OR", "UT", "AZ", "FL", "NJ", "MD", "MI", "OH", "TN"
]

# Filter out states that are already in priority list
available_states = [state for state in states if state not in priority_states]

# Create the state options with priority list at top
state_options = priority_states + ["--- Other States ---"] + available_states

# Find default index for California (most popular)
try:
    california_index = state_options.index("CA") if "CA" in state_options else 0
except ValueError:
    california_index = 0

# Set default selections
state_default = california_index
def_year = 0
try:
    if years and 2024 in years:
        def_year = [str(y) for y in years].index('2024')
except (ValueError, IndexError):
    def_year = 0

# State filter (no "All" option - state-level analysis only)
state = st.sidebar.selectbox("🗺️ State", state_options, index=state_default, help="Select a specific state for detailed analysis")

# Year filter
year = st.sidebar.selectbox("📅 Year", [str(y) for y in years], index=def_year, help="Select a specific year or 'All' for all years")

# SOC Title filter
soc_title = st.sidebar.selectbox("💼 Job Category", ["All"] + soc_titles, help="Select a specific job category or 'All' for all categories")

# Job Title filter (depends on SOC Title)
with st.spinner("Loading job titles..."):
    job_titles = get_job_titles(state, soc_title, year)
job_title = st.sidebar.selectbox("👨‍💻 Job Title", ["All"] + job_titles, help="Select a specific job title or 'All' for all titles")

# Get filtered data
with st.spinner("Loading state data..."):
    df = get_state_filtered_data(state, year, soc_title)
    if job_title and job_title != 'All':
        df = df[df['NORMALIZED_JOB_TITLE'] == job_title]

# Stats
st.header("Summary Stats")
if not df.empty:
    total_petitions = len(df)
    avg_salary = df['PREVAILING_WAGE'].mean()
    min_salary = df['PREVAILING_WAGE'].min()
    max_salary = df['PREVAILING_WAGE'].max()
    
    st.metric("Total Lottery Petitions", f"{total_petitions:,.0f}")
    st.metric("Avg Wage", f"${avg_salary:,.0f}")
    st.metric("Min Wage", f"${min_salary:,.0f}")
    st.metric("Max Wage", f"${max_salary:,.0f}")
else:
    st.metric("Total Lottery Petitions", "0")
    st.metric("Avg Wage", "$0")
    st.metric("Min Wage", "$0")
    st.metric("Max Wage", "$0")

# Handle empty data gracefully
if df.empty or len(df) == 0:
    st.warning("⚠️ No data found for the selected filters. Please try different filter combinations.")
    st.info("💡 Tip: Try selecting 'All' for some filters to see more data.")
else:
    # Lightweight state-level analysis - no tabs, just essential insights
    st.info("💡 **State-Level H-1B Analysis**: Quick overview of petition volume, wage distribution, and top occupations for the selected state.")
    
    # Simple two-column layout for core insights
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📊 Wage Distribution by Level**")
        st.markdown("💰 **What this shows**: How salaries are distributed across different wage levels in this state.")
        
        # Simple wage level breakdown
        wage_level_counts = df['PW_WAGE_LEVEL'].value_counts().reset_index()
        wage_level_counts.columns = ['Wage Level', 'Petitions']
        
        fig_wage = px.bar(wage_level_counts, x='Wage Level', y='Petitions',
                         title="Petitions by Wage Level",
                         color='Petitions', color_continuous_scale='viridis')
        fig_wage.update_layout(height=400)
        st.plotly_chart(fig_wage, use_container_width=True)
        
        # Wage level summary
        st.markdown("**📋 Wage Level Summary**")
        wage_summary = df.groupby('PW_WAGE_LEVEL')['PREVAILING_WAGE'].agg(['count', 'mean', 'min', 'max']).reset_index()
        wage_summary.columns = ['Level', 'Petitions', 'Avg Salary', 'Min Salary', 'Max Salary']
        wage_summary['Avg Salary'] = wage_summary['Avg Salary'].round(0).astype(int)
        wage_summary['Min Salary'] = wage_summary['Min Salary'].round(0).astype(int)
        wage_summary['Max Salary'] = wage_summary['Max Salary'].round(0).astype(int)
        st.dataframe(wage_summary, use_container_width=True)
    
    with col2:
        st.markdown("**🏆 Top Job Categories**")
        st.markdown("💼 **What this shows**: Most common job categories in this state.")
        
        # Top job categories
        top_jobs = df['aggressive_normalized_soc_title'].value_counts().head(10).reset_index()
        top_jobs.columns = ['Job Category', 'Petitions']
        
        fig_jobs = px.bar(top_jobs, x='Petitions', y='Job Category', orientation='h',
                         title="Top 10 Job Categories",
                         color='Petitions', color_continuous_scale='plasma')
        fig_jobs.update_layout(height=400)
        st.plotly_chart(fig_jobs, use_container_width=True)
        
        # Job categories summary
        st.markdown("**📋 Top Job Categories Summary**")
        job_summary = df.groupby('aggressive_normalized_soc_title').agg({
            'PREVAILING_WAGE': ['count', 'mean', 'min', 'max']
        }).reset_index()
        job_summary.columns = ['Job Category', 'Petitions', 'Avg Salary', 'Min Salary', 'Max Salary']
        job_summary = job_summary.sort_values('Petitions', ascending=False).head(10)
        job_summary['Avg Salary'] = job_summary['Avg Salary'].round(0).astype(int)
        job_summary['Min Salary'] = job_summary['Min Salary'].round(0).astype(int)
        job_summary['Max Salary'] = job_summary['Max Salary'].round(0).astype(int)
        st.dataframe(job_summary, use_container_width=True) 