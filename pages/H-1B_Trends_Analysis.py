import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import duckdb
import numpy as np
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Trends Analysis",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional color scheme for journalists and data analysts
COLORS = {
    'primary': '#1f77b4',      # Professional blue
    'secondary': '#ff7f0e',    # Orange accent
    'success': '#2ca02c',      # Green for positive trends
    'warning': '#d62728',      # Red for warnings/negative trends
    'info': '#9467bd',         # Purple for info
    'light': '#f8f9fa',        # Light background
    'dark': '#343a40',         # Dark background
    'text_primary': '#212529', # Dark text
    'text_secondary': '#6c757d', # Secondary text
    'border': '#dee2e6',       # Border color
    'highlight': '#e3f2fd'     # Highlight color
}

# Apply professional styling
st.markdown(f"""
<style>
    /* Main styling */
    .main {{
        background: linear-gradient(135deg, {COLORS['light']} 0%, #ffffff 100%);
        color: {COLORS['text_primary']};
    }}
    
    /* Headers */
    .main .block-container h1 {{
        color: {COLORS['primary']};
        font-weight: 700;
        border-bottom: 3px solid {COLORS['secondary']};
        padding-bottom: 10px;
        margin-bottom: 30px;
    }}
    
    .main .block-container h2 {{
        color: {COLORS['primary']};
        font-weight: 600;
        border-left: 4px solid {COLORS['secondary']};
        padding-left: 15px;
        margin-top: 30px;
    }}
    
    .main .block-container h3 {{
        color: {COLORS['text_primary']};
        font-weight: 600;
        margin-top: 25px;
    }}
    
    /* Sidebar */
    .css-1d391kg {{
        background: linear-gradient(180deg, {COLORS['dark']} 0%, #495057 100%);
        color: white;
    }}
    
    /* Components */
    .stDataFrame, .stMetric {{
        border: 1px solid {COLORS['border']};
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }}
    
    /* Interactive elements */
    .stSelectbox > div > div {{
        border: 2px solid {COLORS['border']};
        border-radius: 6px;
        transition: border-color 0.3s ease;
    }}
    
    .stSelectbox > div > div:hover {{
        border-color: {COLORS['primary']};
    }}
    
    /* Buttons */
    .stButton > button {{
        background: linear-gradient(45deg, {COLORS['primary']}, {COLORS['info']});
        color: white;
        border: none;
        border-radius: 6px;
        padding: 8px 16px;
        font-weight: 600;
        transition: all 0.3s ease;
    }}
    
    .stButton > button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }}
    
    /* Responsive design */
    @media (max-width: 768px) {{
        .main .block-container h1 {{
            font-size: 1.8rem;
        }}
        
        .main .block-container h2 {{
            font-size: 1.4rem;
        }}
    }}
    
    /* Custom classes for trends page */
    .main-header {{
        font-size: 2.5rem;
        font-weight: bold;
        color: {COLORS['primary']};
        text-align: center;
        margin-bottom: 2rem;
    }}
    
    .section-header {{
        font-size: 1.8rem;
        font-weight: bold;
        color: {COLORS['text_primary']};
        margin-top: 2rem;
        margin-bottom: 1rem;
    }}
    
    .info-box {{
        background-color: {COLORS['highlight']};
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid {COLORS['primary']};
        margin: 1rem 0;
    }}
    
    .metric-card {{
        background-color: {COLORS['light']};
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid {COLORS['border']};
        text-align: center;
    }}
</style>
""", unsafe_allow_html=True)

from database_connection import get_db_connection

# Database configuration
DB_FILE = 'job_market_std_employer.duckdb'
TABLE = 'job_market_data_aggressive_normalized'

# ============================================================================
# FILTER FUNCTIONS (Independent from main app)
# ============================================================================

def get_trends_filter_options():
    """Get filter options for trends analysis - lightweight version"""
    with st.spinner("Loading filter options..."):
        try:
            con = get_db_connection()
            if con is None:
                return [], [], []
            
            # Load only top companies and categories for lightweight operation
            companies = con.execute(f"SELECT DISTINCT STD_EMPLOYER_NAME_PARENT FROM {TABLE} WHERE VISA_CLASS = 'H-1B' AND is_lottery_petition = TRUE AND STD_EMPLOYER_NAME_PARENT != '' ORDER BY STD_EMPLOYER_NAME_PARENT LIMIT 50").fetchdf()['STD_EMPLOYER_NAME_PARENT'].tolist()
            states = con.execute(f"SELECT DISTINCT EMPLOYER_STATE FROM {TABLE} WHERE VISA_CLASS = 'H-1B' AND is_lottery_petition = TRUE AND EMPLOYER_STATE IS NOT NULL ORDER BY EMPLOYER_STATE").fetchdf()['EMPLOYER_STATE'].tolist()
            soc_titles = con.execute(f"SELECT DISTINCT aggressive_normalized_soc_title FROM {TABLE} WHERE VISA_CLASS = 'H-1B' AND is_lottery_petition = TRUE AND aggressive_normalized_soc_title IS NOT NULL ORDER BY aggressive_normalized_soc_title LIMIT 30").fetchdf()['aggressive_normalized_soc_title'].tolist()
            
            # Force cleanup
            import gc
            gc.collect()
            
            return companies, states, soc_titles
        except Exception as e:
            st.error(f"Failed to load filter options: {e}")
            return [], [], []

def get_trends_cities(state, company, soc_title):
    """Get cities for trends analysis filters"""
    with st.spinner("Loading cities..."):
        try:
            con = get_db_connection()
            if con is None:
                return []
            
            query = f"SELECT DISTINCT EMPLOYER_CITY FROM {TABLE} WHERE VISA_CLASS = 'H-1B' AND is_lottery_petition = TRUE AND EMPLOYER_CITY IS NOT NULL"
            params = []
            if state and state != 'All':
                query += " AND EMPLOYER_STATE = ?"
                params.append(state)
            if company and company != 'All':
                query += " AND STD_EMPLOYER_NAME_PARENT = ?"
                params.append(company)
            if soc_title and soc_title != 'All':
                query += " AND aggressive_normalized_soc_title = ?"
                params.append(soc_title)
            query += " ORDER BY EMPLOYER_CITY"
            cities = con.execute(query, params).fetchdf()['EMPLOYER_CITY'].tolist()
            return cities
        except Exception as e:
            st.error(f"Failed to load cities: {e}")
            return []

def get_trends_filtered_data(company, state, soc_title, year_range, international_students_only=True):
    """Get aggregated data for trends analysis - SQL does the heavy lifting"""
    with st.spinner("Loading aggregated trends data..."):
        try:
            con = get_db_connection()
            if con is None:
                return pd.DataFrame()
            
            # Build aggregated query - SQL does all the work
            query = f"""
            SELECT 
                YEAR,
                aggressive_normalized_soc_title,
                COUNT(*) as petition_count,
                AVG(PREVAILING_WAGE) as avg_salary,
                MIN(PREVAILING_WAGE) as min_salary,
                MAX(PREVAILING_WAGE) as max_salary,
                COUNT(CASE WHEN PW_WAGE_LEVEL = 'I' THEN 1 END) as level1_count,
                COUNT(CASE WHEN PW_WAGE_LEVEL = 'II' THEN 1 END) as level2_count,
                COUNT(CASE WHEN PW_WAGE_LEVEL = 'III' THEN 1 END) as level3_count,
                COUNT(CASE WHEN PW_WAGE_LEVEL = 'IV' THEN 1 END) as level4_count
            FROM {TABLE} 
            WHERE VISA_CLASS = 'H-1B' AND is_lottery_petition = TRUE 
            AND YEAR BETWEEN ? AND ? AND LOWER(aggressive_normalized_soc_title) NOT LIKE '%other%'
            """
            params = [year_range[0], year_range[1]]
            
            if company and company != 'All':
                query += " AND STD_EMPLOYER_NAME_PARENT = ?"
                params.append(company)
            if state and state != 'All':
                query += " AND EMPLOYER_STATE = ?"
                params.append(state)
            if soc_title and soc_title != 'All':
                query += " AND aggressive_normalized_soc_title = ?"
                params.append(soc_title)
            
            # Add wage level filter for international students
            if international_students_only:
                query += " AND PW_WAGE_LEVEL IN ('I', 'II')"
            
            # Group by year and category - SQL does the aggregation
            query += " GROUP BY YEAR, aggressive_normalized_soc_title ORDER BY YEAR, petition_count DESC"
            
            df = con.execute(query, params).fetchdf()
            
            # Force cleanup
            import gc
            gc.collect()
            
            return df
        except Exception as e:
            st.error(f"Error fetching aggregated trends data: {e}")
            return pd.DataFrame()

def get_trends_yearly_data(company, state, soc_title, year_range, international_students_only=True):
    """Get aggregated yearly data for trends analysis - SQL does the heavy lifting"""
    with st.spinner("Loading aggregated yearly trends data..."):
        try:
            con = get_db_connection()
            if con is None:
                return pd.DataFrame()
            
            # Build aggregated query - SQL does all the work
            query = f"""
            SELECT 
                YEAR,
                aggressive_normalized_soc_title,
                COUNT(*) as petition_count,
                AVG(PREVAILING_WAGE) as avg_salary,
                MIN(PREVAILING_WAGE) as min_salary,
                MAX(PREVAILING_WAGE) as max_salary,
                COUNT(CASE WHEN PW_WAGE_LEVEL = 'I' THEN 1 END) as level1_count,
                COUNT(CASE WHEN PW_WAGE_LEVEL = 'II' THEN 1 END) as level2_count,
                COUNT(CASE WHEN PW_WAGE_LEVEL = 'III' THEN 1 END) as level3_count,
                COUNT(CASE WHEN PW_WAGE_LEVEL = 'IV' THEN 1 END) as level4_count
            FROM {TABLE} 
            WHERE VISA_CLASS = 'H-1B' AND is_lottery_petition = TRUE 
            AND YEAR BETWEEN ? AND ? AND LOWER(aggressive_normalized_soc_title) NOT LIKE '%other%'
            """
            params = [year_range[0], year_range[1]]
            
            if company and company != 'All':
                query += " AND STD_EMPLOYER_NAME_PARENT = ?"
                params.append(company)
            if state and state != 'All':
                query += " AND EMPLOYER_STATE = ?"
                params.append(state)
            if soc_title and soc_title != 'All':
                query += " AND aggressive_normalized_soc_title = ?"
                params.append(soc_title)
            
            # Add wage level filter for international students
            if international_students_only:
                query += " AND PW_WAGE_LEVEL IN ('I', 'II')"
            
            # Group by year and category - SQL does the aggregation
            query += " GROUP BY YEAR, aggressive_normalized_soc_title ORDER BY YEAR, petition_count DESC"
            
            df = con.execute(query, params).fetchdf()
            
            # Force cleanup
            import gc
            gc.collect()
            
            return df
        except Exception as e:
            st.error(f"Error fetching aggregated yearly trends data: {e}")
            return pd.DataFrame()

def get_ai_career_data(company, state, year_range, international_students_only=True):
    """Get aggregated AI career data - SQL does the heavy lifting"""
    with st.spinner("Loading aggregated AI career data..."):
        try:
            con = get_db_connection()
            if con is None:
                return pd.DataFrame()
            
            # Build aggregated query for AI categories - SQL does all the work
            query = f"""
            SELECT 
                YEAR,
                CASE 
                    WHEN aggressive_normalized_soc_title IN ('Data Scientists', 'Computer and Information Research Scientists') 
                    OR (aggressive_normalized_soc_title = 'Software Developers' 
                    AND (JOB_TITLE LIKE '%Machine Learning%' OR JOB_TITLE LIKE '%AI%' OR JOB_TITLE LIKE '%ML%' OR JOB_TITLE LIKE '%Data Science%'))
                    THEN 'AI Developers'
                    ELSE aggressive_normalized_soc_title
                END as career_category,
                COUNT(*) as petition_count,
                AVG(PREVAILING_WAGE) as avg_salary,
                MIN(PREVAILING_WAGE) as min_salary,
                MAX(PREVAILING_WAGE) as max_salary
            FROM {TABLE} 
            WHERE VISA_CLASS = 'H-1B' AND is_lottery_petition = TRUE 
            AND YEAR BETWEEN ? AND ? AND LOWER(aggressive_normalized_soc_title) NOT LIKE '%other%'
            """
            params = [year_range[0], year_range[1]]
            
            if company and company != 'All':
                query += " AND STD_EMPLOYER_NAME_PARENT = ?"
                params.append(company)
            if state and state != 'All':
                query += " AND EMPLOYER_STATE = ?"
                params.append(state)
            
            # Add wage level filter for international students
            if international_students_only:
                query += " AND PW_WAGE_LEVEL IN ('I', 'II')"
            
            # Group by year and career category - SQL does the aggregation
            query += " GROUP BY YEAR, career_category ORDER BY YEAR, petition_count DESC"
            
            df = con.execute(query, params).fetchdf()
            
            # Force cleanup
            import gc
            gc.collect()
            
            return df
        except Exception as e:
            st.error(f"Error fetching aggregated AI career data: {e}")
            return pd.DataFrame()

def get_career_growth_decline_data(company, state, year_range, international_students_only=True):
    """Get detailed career growth and decline data for proper trend analysis"""
    with st.spinner("Loading career growth/decline data..."):
        try:
            con = get_db_connection()
            if con is None:
                return pd.DataFrame()
            
            # Get detailed data for growth analysis - need year-by-year data
            query = f"""
            SELECT 
                YEAR,
                CASE 
                    WHEN aggressive_normalized_soc_title IN ('Data Scientists', 'Computer and Information Research Scientists') 
                    OR (aggressive_normalized_soc_title = 'Software Developers' 
                    AND (JOB_TITLE LIKE '%Machine Learning%' OR JOB_TITLE LIKE '%AI%' OR JOB_TITLE LIKE '%ML%' OR JOB_TITLE LIKE '%Data Science%'))
                    THEN 'AI Developers'
                    ELSE aggressive_normalized_soc_title
                END as career_category,
                COUNT(*) as petition_count
            FROM {TABLE} 
            WHERE VISA_CLASS = 'H-1B' AND is_lottery_petition = TRUE 
            AND YEAR BETWEEN ? AND ? AND LOWER(aggressive_normalized_soc_title) NOT LIKE '%other%'
            """
            params = [year_range[0], year_range[1]]
            
            if company and company != 'All':
                query += " AND STD_EMPLOYER_NAME_PARENT = ?"
                params.append(company)
            if state and state != 'All':
                query += " AND EMPLOYER_STATE = ?"
                params.append(state)
            
            # Add wage level filter for international students
            if international_students_only:
                query += " AND PW_WAGE_LEVEL IN ('I', 'II')"
            
            # Group by year and career category for growth analysis
            query += " GROUP BY YEAR, career_category ORDER BY YEAR, petition_count DESC"
            
            df = con.execute(query, params).fetchdf()
            
            # Force cleanup
            import gc
            gc.collect()
            
            return df
        except Exception as e:
            st.error(f"Error fetching career growth/decline data: {e}")
            return pd.DataFrame()

# Specific functions for each visualization - SQL does the heavy lifting
def get_top_companies_data(company, state, soc_title, year_range, international_students_only=True):
    """Get top companies data for visualization - SQL does the heavy lifting"""
    with st.spinner("Loading top companies data..."):
        try:
            con = get_db_connection()
            if con is None:
                return pd.DataFrame()
            
            # Build aggregated query for top companies - SQL does all the work
            query = f"""
            SELECT 
                STD_EMPLOYER_NAME_PARENT as company,
                COUNT(*) as petition_count,
                AVG(PREVAILING_WAGE) as avg_salary,
                MIN(PREVAILING_WAGE) as min_salary,
                MAX(PREVAILING_WAGE) as max_salary,
                COUNT(CASE WHEN PW_WAGE_LEVEL = 'I' THEN 1 END) as level1_count,
                COUNT(CASE WHEN PW_WAGE_LEVEL = 'II' THEN 1 END) as level2_count
            FROM {TABLE} 
            WHERE VISA_CLASS = 'H-1B' AND is_lottery_petition = TRUE 
            AND YEAR BETWEEN ? AND ? AND LOWER(aggressive_normalized_soc_title) NOT LIKE '%other%'
            """
            params = [year_range[0], year_range[1]]
            
            if company and company != 'All':
                query += " AND STD_EMPLOYER_NAME_PARENT = ?"
                params.append(company)
            if state and state != 'All':
                query += " AND EMPLOYER_STATE = ?"
                params.append(state)
            if soc_title and soc_title != 'All':
                query += " AND aggressive_normalized_soc_title = ?"
                params.append(soc_title)
            
            # Add wage level filter for international students
            if international_students_only:
                query += " AND PW_WAGE_LEVEL IN ('I', 'II')"
            
            # Group by company - SQL does the aggregation
            query += " GROUP BY STD_EMPLOYER_NAME_PARENT ORDER BY petition_count DESC"
            
            df = con.execute(query, params).fetchdf()
            
            # Force cleanup
            import gc
            gc.collect()
            
            return df
        except Exception as e:
            st.error(f"Error fetching top companies data: {e}")
            return pd.DataFrame()

def get_top_states_data(company, soc_title, year_range, international_students_only=True):
    """Get top states data for visualization - SQL does the heavy lifting"""
    with st.spinner("Loading top states data..."):
        try:
            con = get_db_connection()
            if con is None:
                return pd.DataFrame()
            
            # Build aggregated query for top states - SQL does all the work
            query = f"""
            SELECT 
                EMPLOYER_STATE as state,
                COUNT(*) as petition_count,
                AVG(PREVAILING_WAGE) as avg_salary,
                MIN(PREVAILING_WAGE) as min_salary,
                MAX(PREVAILING_WAGE) as max_salary,
                COUNT(CASE WHEN PW_WAGE_LEVEL = 'I' THEN 1 END) as level1_count,
                COUNT(CASE WHEN PW_WAGE_LEVEL = 'II' THEN 1 END) as level2_count
            FROM {TABLE} 
            WHERE VISA_CLASS = 'H-1B' AND is_lottery_petition = TRUE 
            AND YEAR BETWEEN ? AND ? AND LOWER(aggressive_normalized_soc_title) NOT LIKE '%other%'
            """
            params = [year_range[0], year_range[1]]
            
            if company and company != 'All':
                query += " AND STD_EMPLOYER_NAME_PARENT = ?"
                params.append(company)
            if soc_title and soc_title != 'All':
                query += " AND aggressive_normalized_soc_title = ?"
                params.append(soc_title)
            
            # Add wage level filter for international students
            if international_students_only:
                query += " AND PW_WAGE_LEVEL IN ('I', 'II')"
            
            # Group by state - SQL does the aggregation
            query += " GROUP BY EMPLOYER_STATE ORDER BY petition_count DESC"
            
            df = con.execute(query, params).fetchdf()
            
            # Force cleanup
            import gc
            gc.collect()
            
            return df
        except Exception as e:
            st.error(f"Error fetching top states data: {e}")
            return pd.DataFrame()

def get_salary_insights_data(company, state, soc_title, year_range, international_students_only=True):
    """Get salary insights data for visualization - SQL does the heavy lifting"""
    with st.spinner("Loading salary insights data..."):
        try:
            con = get_db_connection()
            if con is None:
                return pd.DataFrame()
            
            # Build aggregated query for salary insights - SQL does all the work
            query = f"""
            SELECT 
                aggressive_normalized_soc_title,
                COUNT(*) as petition_count,
                AVG(PREVAILING_WAGE) as avg_salary,
                MIN(PREVAILING_WAGE) as min_salary,
                MAX(PREVAILING_WAGE) as max_salary,
                PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY PREVAILING_WAGE) as p25_salary,
                PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY PREVAILING_WAGE) as median_salary,
                PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY PREVAILING_WAGE) as p75_salary,
                COUNT(CASE WHEN PW_WAGE_LEVEL = 'I' THEN 1 END) as level1_count,
                COUNT(CASE WHEN PW_WAGE_LEVEL = 'II' THEN 1 END) as level2_count,
                COUNT(CASE WHEN PW_WAGE_LEVEL = 'III' THEN 1 END) as level3_count,
                COUNT(CASE WHEN PW_WAGE_LEVEL = 'IV' THEN 1 END) as level4_count
            FROM {TABLE} 
            WHERE VISA_CLASS = 'H-1B' AND is_lottery_petition = TRUE 
            AND YEAR BETWEEN ? AND ? AND LOWER(aggressive_normalized_soc_title) NOT LIKE '%other%'
            """
            params = [year_range[0], year_range[1]]
            
            if company and company != 'All':
                query += " AND STD_EMPLOYER_NAME_PARENT = ?"
                params.append(company)
            if state and state != 'All':
                query += " AND EMPLOYER_STATE = ?"
                params.append(state)
            if soc_title and soc_title != 'All':
                query += " AND aggressive_normalized_soc_title = ?"
                params.append(soc_title)
            
            # Add wage level filter for international students
            if international_students_only:
                query += " AND PW_WAGE_LEVEL IN ('I', 'II')"
            
            # Group by category - SQL does the aggregation
            query += " GROUP BY aggressive_normalized_soc_title ORDER BY avg_salary DESC"
            
            df = con.execute(query, params).fetchdf()
            
            # Force cleanup
            import gc
            gc.collect()
            
            return df
        except Exception as e:
            st.error(f"Error fetching salary insights data: {e}")
            return pd.DataFrame()

# ============================================================================
# MAIN PAGE CONTENT
# ============================================================================

# Main page content
st.markdown('<h1 class="main-header">📈 H-1B Trends Analysis</h1>', unsafe_allow_html=True)
st.markdown("**Comprehensive analysis for H-1B visa holders - understand job market trends, salary expectations, and career development factors**")

# ============================================================================
# SIDEBAR FILTERS (Independent from main app)
# ============================================================================

st.sidebar.markdown("## 🔍 Trends Analysis Filters")
st.sidebar.markdown("**Filter data for trends analysis**")

# Load filter options
companies, states, soc_titles = get_trends_filter_options()

# Year range slider
year_range = st.sidebar.slider(
    "📅 Year Range",
    min_value=2020,
    max_value=2024,
    value=(2020, 2024),
    help="Select a range of years to analyze"
)

# International Students Only toggle
international_students_only = st.sidebar.toggle(
    "🎓 International Students Only (Wage Level I & II)",
    value=True,
    help="When enabled, shows only entry-level positions (Wage Level I & II) suitable for international students. When disabled, includes all wage levels."
)

# Update main description based on toggle
if international_students_only:
    st.markdown("**Comprehensive analysis for international students and H-1B visa holders - understand job market trends, salary expectations, and visa success factors**")
else:
    st.markdown("**Comprehensive analysis for H-1B visa holders and professionals - understand job market trends, salary expectations, and career development factors**")

# Priority companies for trends analysis (same as main app)
priority_companies = [
    # Big Tech (High H-1B volumes, frequently in news)
    "AMAZON", "MICROSOFT", "GOOGLE", "META", "APPLE", "NETFLIX", "UBER", "LYFT",
    
    # Indian IT Giants (Major employers of Indian H-1B workers)
    "TATA CONSULTANCY SERVICES", "INFOSYS", "WIPRO", "HCL", "TECH MAHINDRA", "LARSEN & TOUBRO",
    
    # Global IT Services (High H-1B volumes)
    "COGNIZANT", "ACCENTURE", "DELOITTE", "IBM", "CAPGEMINI", "DXC TECHNOLOGY", "MINDTREE",
    
    # Finance & Consulting (Major H-1B employers)
    "JPMORGAN CHASE", "GOLDMAN SACHS", "ERNST & YOUNG", "PRICEWATERHOUSECOOPERS", "KPMG",
    
    # Retail & Consumer (Large employers)
    "WALMART", "TARGET", "HOME DEPOT", "LOWES",
    
    # Healthcare & Pharma (Growing H-1B sector)
    "JOHNSON & JOHNSON", "PFIZER", "MERCK", "AMGEN", "GILEAD SCIENCES",
    
    # Automotive & Manufacturing
    "TESLA", "FORD", "GENERAL MOTORS", "TOYOTA", "HONDA"
]

# Filter out companies that are already in priority list
available_companies = [company for company in companies if company not in priority_companies]

# Create the company options with priority list at top
company_options = ["All"] + priority_companies + ["--- Other Companies ---"] + available_companies

# Company filter - default to "All"
company = st.sidebar.selectbox(
    "🏢 Company",
    company_options,
    index=0,  # Default to "All"
    help="Select a specific company or 'All' for all companies"
)

# State filter
state = st.sidebar.selectbox(
    "🗺️ State",
    ["All"] + states,
    help="Select a specific state or 'All' for all states"
)

# SOC Title filter
soc_title = st.sidebar.selectbox(
    "💼 Job Category",
    ["All"] + soc_titles,
    index=0,  # Default to "All"
    help="Select a specific job category or 'All' for all categories"
)

# ============================================================================
# TRENDS ANALYSIS TABS
# ============================================================================

# Get filtered data based on sidebar selections
df = get_trends_filtered_data(company, state, soc_title, year_range, international_students_only)

# Dynamic tab titles based on toggle
if international_students_only:
    tab_titles = [
        "🎓 Entry-Level Opportunities", 
        "🏢 Top Employers", 
        "🗺️ Geographic Hotspots", 
        "💼 Career Paths",
        "💰 Salary Insights"
    ]
else:
    tab_titles = [
        "🎯 Job Opportunities", 
        "🏢 Top Employers", 
        "🗺️ Geographic Hotspots", 
        "💼 Career Paths",
        "💰 Salary Insights"
    ]

# Trends Analysis Tabs
trends_tab1, trends_tab2, trends_tab3, trends_tab4, trends_tab5 = st.tabs(tab_titles)

with trends_tab1:
    if international_students_only:
        st.markdown('<h2 class="section-header">🎓 Entry-Level Opportunities for International Students</h2>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">💡 <strong>Key Insight:</strong> Entry-level positions (Wage Level I & II) are typically where international students start their careers. Understanding these trends helps you plan your job search strategy.</div>', unsafe_allow_html=True)
    else:
        st.markdown('<h2 class="section-header">🎯 Job Opportunities Analysis</h2>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">💡 <strong>Key Insight:</strong> Understanding job market trends across all experience levels helps you plan your career development strategy.</div>', unsafe_allow_html=True)
    
    # Get yearly data for entry-level analysis
    yearly_df = get_trends_yearly_data(company, state, soc_title, year_range, international_students_only)
    
    if not yearly_df.empty:
        # Data is already filtered by wage level based on toggle
        entry_level_df = yearly_df
        
        if not entry_level_df.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                if international_students_only:
                    st.markdown("**Entry-Level Opportunities by Year**")
                    chart_title = "Entry-Level H-1B Opportunities (Level I & II)"
                else:
                    st.markdown("**Job Opportunities by Year**")
                    chart_title = "H-1B Job Opportunities by Year"
                
                # Use aggregated data - SQL already did the work
                entry_counts = entry_level_df.groupby('YEAR')['petition_count'].sum().reset_index()
                
                fig_entry_counts = px.line(entry_counts, x='YEAR', y='petition_count',
                                         title=chart_title,
                                         labels={'petition_count': 'Number of Petitions', 'YEAR': 'Year'})
                fig_entry_counts.update_layout(height=400)
                st.plotly_chart(fig_entry_counts, use_container_width=True)
            
            with col2:
                if international_students_only:
                    st.markdown("**Entry-Level Salary Trends**")
                    chart_title = "Entry-Level Salary Trends by Year"
                else:
                    st.markdown("**Salary Trends by Year**")
                    chart_title = "Salary Trends by Year"
                
                # Use aggregated data - SQL already calculated averages
                entry_salary_trends = entry_level_df.groupby('YEAR')['avg_salary'].mean().reset_index()
                
                fig_entry_salary = px.line(entry_salary_trends, x='YEAR', y='avg_salary',
                                         title=chart_title,
                                         labels={'avg_salary': 'Average Salary ($)', 'YEAR': 'Year'})
                fig_entry_salary.update_layout(height=400)
                st.plotly_chart(fig_entry_salary, use_container_width=True)
            

            
            # Market insights
            if international_students_only:
                st.markdown("**📊 Entry-Level Market Insights**")
                insights_title = "🎯 Key Insights for International Students:"
                insights_text = """
                - **Level I (Entry-Level):** Typically for recent graduates with 0-2 years experience
                - **Level II (Mid-Level):** For candidates with 2-5 years experience  
                - **Salary Range:** Entry-level positions typically pay $60,000-$90,000
                - **Top Fields:** Software Engineering, IT & Systems, AI/ML & Data Science
                - **Strategy:** Focus on companies that hire many Level I & II positions
                """
            else:
                st.markdown("**📊 Job Market Insights**")
                insights_title = "🎯 Key Insights for Career Planning:"
                insights_text = """
                - **Level I (Entry-Level):** Typically for recent graduates with 0-2 years experience
                - **Level II (Mid-Level):** For candidates with 2-5 years experience
                - **Level III (Senior):** For candidates with 5-10 years experience
                - **Level IV (Expert):** For candidates with 10+ years experience
                - **Salary Range:** Varies significantly by experience level and field
                - **Top Fields:** Software Engineering, IT & Systems, AI/ML & Data Science
                - **Strategy:** Focus on companies that align with your experience level
                """
            
            # Use aggregated data - SQL already calculated the statistics
            entry_stats = entry_level_df.agg({
                'petition_count': 'sum',
                'avg_salary': 'mean',
                'min_salary': 'min',
                'max_salary': 'max'
            }).round(0)
            
            # Create a simple stats display
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Petitions", f"{int(entry_stats['petition_count']):,}")
            with col2:
                st.metric("Avg Salary", f"${int(entry_stats['avg_salary']):,}")
            with col3:
                st.metric("Min Salary", f"${int(entry_stats['min_salary']):,}")
            with col4:
                st.metric("Max Salary", f"${int(entry_stats['max_salary']):,}")
            
            # Key insights
            st.markdown(f"**{insights_title}**")
            st.markdown(insights_text)
        else:
            st.warning("No entry-level opportunities found for the selected filters.")
    else:
        st.warning("No data available for the selected filters.")

with trends_tab2:
    if international_students_only:
        st.markdown('<h2 class="section-header">🏢 Top Employers for International Students</h2>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">💡 <strong>Key Insight:</strong> These companies hire the most international students and recent graduates. Focus your job search on companies with high entry-level hiring rates.</div>', unsafe_allow_html=True)
    else:
        st.markdown('<h2 class="section-header">🏢 Top Employers Analysis</h2>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">💡 <strong>Key Insight:</strong> These companies hire the most H-1B workers across all experience levels. Focus your job search on companies with high hiring rates.</div>', unsafe_allow_html=True)
    
    if not df.empty:
        # Use the specific top companies function for aggregated data
        top_companies_df = get_top_companies_data(company, state, soc_title, year_range, international_students_only)
        
        if not top_companies_df.empty:
            # Filter to top 15 companies for visualization
            top_companies_df = top_companies_df.head(15)
            
            # Enhanced Top Employers Visualization
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**🏆 Top Companies by Hiring Volume**")
                # Use aggregated data - SQL already calculated the counts
                fig_top_companies = px.scatter(top_companies_df, x='petition_count', y='company', 
                                             size='petition_count', color='avg_salary',
                                             title="Top Companies by Hiring Volume",
                                             labels={'petition_count': 'Number of Petitions', 'company': 'Company Name', 'avg_salary': 'Avg Salary'},
                                             color_continuous_scale='viridis')
                fig_top_companies.update_layout(height=500, showlegend=False)
                st.plotly_chart(fig_top_companies, use_container_width=True)
            
            with col2:
                st.markdown("**💰 Best Paying Companies**")
                # Filter to companies with 100+ petitions and use aggregated data
                best_paying_df = top_companies_df[top_companies_df['petition_count'] >= 100].nlargest(15, 'avg_salary')
                
                # Create a more appealing salary visualization
                fig_salary_companies = px.scatter(best_paying_df, x='avg_salary', y='company',
                                                size='petition_count', color='avg_salary',
                                                title="Best Paying Companies (100+ petitions)",
                                                labels={'avg_salary': 'Average Salary ($)', 'company': 'Company Name', 'petition_count': 'Number of Petitions'},
                                                color_continuous_scale='plasma')
                fig_salary_companies.update_layout(height=500, showlegend=False)
                st.plotly_chart(fig_salary_companies, use_container_width=True)
            
            # Enhanced Company Types Analysis
            st.markdown("**🏢 Company Types and Entry-Level Hiring**")
            def categorize_company_for_students(company_name):
                company_lower = company_name.lower()
                
                # Big Tech Companies
                big_tech_keywords = [
                    'amazon', 'google', 'microsoft', 'meta', 'apple', 'netflix', 'uber', 'lyft', 'salesforce', 
                    'oracle', 'adobe', 'intel', 'nvidia', 'amd', 'palantir', 'airbnb', 'doordash', 'zoom', 
                    'slack', 'dropbox', 'spotify', 'twitter', 'linkedin', 'snapchat', 'pinterest', 'square',
                    'stripe', 'shopify', 'databricks', 'snowflake', 'mongodb', 'elastic', 'atlassian', 'okta'
                ]
                if any(tech in company_lower for tech in big_tech_keywords):
                    return 'Big Tech'
                
                # IT Services & Consulting
                it_services_keywords = [
                    'tata', 'infosys', 'wipro', 'hcl', 'cognizant', 'accenture', 'deloitte', 'ibm', 'capgemini', 
                    'dxc', 'mindtree', 'larsen', 'tech mahindra', 'mphasis', 'lti', 'persistent', 'birlasoft',
                    'cybage', 'zensar', 'hexaware', 'quinnox', 'ust', 'globant', 'endava', 'epam', 'perficient'
                ]
                if any(it in company_lower for it in it_services_keywords):
                    return 'IT Services'
                
                # Finance & Banking
                finance_keywords = [
                    'jpmorgan', 'goldman', 'bank', 'financial', 'morgan', 'wells', 'citigroup', 'american express', 
                    'visa', 'mastercard', 'blackrock', 'fidelity', 'vanguard', 'state street', 'pnc', 'us bank',
                    'capital one', 'american express', 'discover', 'paypal', 'stripe', 'square', 'robinhood'
                ]
                if any(finance in company_lower for finance in finance_keywords):
                    return 'Finance'
                
                # Consulting & Professional Services
                consulting_keywords = [
                    'bain', 'mckinsey', 'bcg', 'pwc', 'ey', 'kpmg', 'booz', 'oliver wyman', 'strategy&',
                    'roland berger', 'at kearney', 'le k consulting', 'accenture strategy', 'deloitte consulting'
                ]
                if any(consulting in company_lower for consulting in consulting_keywords):
                    return 'Consulting'
                
                # Healthcare & Pharma
                healthcare_keywords = [
                    'johnson', 'pfizer', 'merck', 'amgen', 'gilead', 'bristol', 'novartis', 'roche', 'sanofi',
                    'astrazeneca', 'eli lilly', 'abbvie', 'biogen', 'regeneron', 'moderna', 'biontech',
                    'johnson & johnson', 'unitedhealth', 'anthem', 'cigna', 'aetna', 'humana', 'kaiser'
                ]
                if any(healthcare in company_lower for healthcare in healthcare_keywords):
                    return 'Healthcare'
                
                # Retail & E-commerce
                retail_keywords = [
                    'walmart', 'target', 'home depot', 'lowes', 'costco', 'best buy', 'amazon retail',
                    'macy', 'nordstrom', 'kohl', 'dollar general', 'dollar tree', 'tj maxx', 'ross'
                ]
                if any(retail in company_lower for retail in retail_keywords):
                    return 'Retail'
                
                # Automotive & Manufacturing
                auto_keywords = [
                    'tesla', 'ford', 'general motors', 'toyota', 'honda', 'bmw', 'mercedes', 'volkswagen',
                    'audi', 'porsche', 'nissan', 'hyundai', 'kia', 'chrysler', 'dodge', 'jeep', 'chevrolet'
                ]
                if any(auto in company_lower for auto in auto_keywords):
                    return 'Automotive'
                
                # Telecommunications
                telecom_keywords = [
                    'verizon', 'at&t', 't-mobile', 'sprint', 'comcast', 'charter', 'cox', 'centurylink',
                    'frontier', 'windstream', 'mediacom', 'optimum', 'spectrum'
                ]
                if any(telecom in company_lower for telecom in telecom_keywords):
                    return 'Telecommunications'
                
                # Aerospace & Defense
                aerospace_keywords = [
                    'boeing', 'lockheed', 'northrop', 'raytheon', 'general electric', 'honeywell',
                    'pratt & whitney', 'rolls royce', 'safran', 'airbus', 'spacex', 'blue origin'
                ]
                if any(aerospace in company_lower for aerospace in aerospace_keywords):
                    return 'Aerospace & Defense'
                
                # Energy & Utilities
                energy_keywords = [
                    'exxon', 'chevron', 'shell', 'bp', 'conocophillips', 'duke energy', 'southern company',
                    'nextera', 'dominion', 'pg&e', 'edison', 'conedison', 'national grid'
                ]
                if any(energy in company_lower for energy in energy_keywords):
                    return 'Energy & Utilities'
                
                # Media & Entertainment
                media_keywords = [
                    'disney', 'warner', 'paramount', 'sony', 'universal', 'netflix', 'hulu', 'discovery',
                    'viacom', 'cbs', 'nbc', 'abc', 'fox', 'cnn', 'espn', 'mtv', 'comedy central'
                ]
                if any(media in company_lower for media in media_keywords):
                    return 'Media & Entertainment'
                
                # Insurance
                insurance_keywords = [
                    'state farm', 'allstate', 'progressive', 'geico', 'liberty mutual', 'farmers',
                    'nationwide', 'travelers', 'hartford', 'metlife', 'prudential', 'aflac'
                ]
                if any(insurance in company_lower for insurance in insurance_keywords):
                    return 'Insurance'
                
                # Real Estate & Construction
                real_estate_keywords = [
                    'keller williams', 're/max', 'century 21', 'coldwell banker', 'berkshire hathaway',
                    'beazer', 'pulte', 'lennar', 'dr horton', 'kb home', 'toll brothers'
                ]
                if any(real_estate in company_lower for real_estate in real_estate_keywords):
                    return 'Real Estate & Construction'
                
                # Food & Beverage
                food_keywords = [
                    'mcdonalds', 'starbucks', 'coca cola', 'pepsi', 'nestle', 'kraft', 'kellogg',
                    'general mills', 'campbell', 'hershey', 'mondelez', 'unilever', 'procter & gamble'
                ]
                if any(food in company_lower for food in food_keywords):
                    return 'Food & Beverage'
                
                # Transportation & Logistics
                transport_keywords = [
                    'fedex', 'ups', 'dhl', 'usps', 'amazon logistics', 'uber freight', 'lyft logistics',
                    'doordash', 'grubhub', 'instacart', 'postmates'
                ]
                if any(transport in company_lower for transport in transport_keywords):
                    return 'Transportation & Logistics'
                
                # Education & Training
                education_keywords = [
                    'kaplan', 'pearson', 'mcgraw hill', 'cengage', 'wiley', 'blackboard', 'canvas',
                    'coursera', 'udemy', 'edx', 'pluralsight', 'linkedin learning'
                ]
                if any(education in company_lower for education in education_keywords):
                    return 'Education & Training'
                
                # Government & Non-Profit
                gov_keywords = [
                    'united states', 'federal', 'state of', 'city of', 'county of', 'department of',
                    'university of', 'college', 'school district', 'red cross', 'united way'
                ]
                if any(gov in company_lower for gov in gov_keywords):
                    return 'Government & Non-Profit'
                
                # Small Companies (based on petition count - will be handled in visualization)
                return 'Other Industries'
            
            # Apply company categorization to aggregated data
            top_companies_df['Company_Type'] = top_companies_df['company'].apply(categorize_company_for_students)
            
            # Enhanced company type analysis with aggregated data
            company_type_summary = top_companies_df.groupby('Company_Type').agg({
                'petition_count': 'sum',
                'avg_salary': 'mean',
                'min_salary': 'min',
                'max_salary': 'max'
            }).round(0)
            company_type_summary.columns = ['Total Petitions', 'Avg Salary', 'Min Salary', 'Max Salary']
            company_type_summary = company_type_summary.sort_values('Total Petitions', ascending=False)
            
            # Filter to show only significant company types (10+ petitions)
            significant_types = company_type_summary[company_type_summary['Total Petitions'] >= 10]
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Bar chart for company types by hiring volume
                fig_company_volume = px.bar(significant_types.reset_index(), x='Total Petitions', y='Company_Type',
                                          title="Entry-Level Hiring by Company Type (10+ petitions)",
                                          labels={'Total Petitions': 'Number of Petitions', 'Company_Type': 'Company Type'},
                                          color='Total Petitions',
                                          color_continuous_scale='viridis')
                fig_company_volume.update_layout(height=500, yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig_company_volume, use_container_width=True)
            
            with col2:
                # Scatter plot showing salary vs hiring volume
                fig_company_salary = px.scatter(significant_types.reset_index(), x='Total Petitions', y='Avg Salary',
                                              size='Total Petitions', color='Avg Salary',
                                              title="Salary vs Hiring Volume by Company Type",
                                              labels={'Total Petitions': 'Number of Petitions', 'Avg Salary': 'Average Salary ($)'},
                                              color_continuous_scale='plasma',
                                              hover_data=['Company_Type', 'Min Salary', 'Max Salary'])
                fig_company_salary.update_layout(height=500)
                st.plotly_chart(fig_company_salary, use_container_width=True)
            
            # Detailed company type statistics
            st.markdown("**📊 Company Type Statistics**")
            st.dataframe(significant_types, use_container_width=True)
            
            # Student-focused company summary using aggregated data
            st.markdown("**🎯 Top Companies for International Students**")
            student_company_summary = top_companies_df[top_companies_df['petition_count'] >= 5].copy()
            student_company_summary['% Level I'] = (student_company_summary['level1_count'] / student_company_summary['petition_count'] * 100).round(2)
            student_company_summary = student_company_summary[['company', 'petition_count', 'avg_salary', 'min_salary', 'max_salary', '% Level I']].sort_values('petition_count', ascending=False)
            student_company_summary.columns = ['Company', 'Entry-Level Petitions', 'Avg Salary', 'Min Salary', 'Max Salary', '% Level I']
            st.dataframe(student_company_summary.head(20), use_container_width=True)
            
            # Key insights for students
            st.markdown("**💡 Key Insights for Job Search:**")
            st.markdown("""
            - **Big Tech Companies:** Highest salaries but competitive
            - **IT Services Companies:** Most entry-level opportunities, good for getting started
            - **Finance Companies:** High salaries, often require specific skills
            - **Consulting Firms:** Good career growth, diverse projects
            - **Strategy:** Apply to IT services companies first, then target Big Tech
            """)
        else:
            st.warning("No entry-level companies found for the selected filters.")
    else:
        st.warning("No data available for the selected filters.")

with trends_tab3:
    if international_students_only:
        st.markdown('<h2 class="section-header">🗺️ Geographic Hotspots for International Students</h2>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">💡 <strong>Key Insight:</strong> Some states and cities have more opportunities for international students. Understanding geographic trends helps you decide where to focus your job search and potentially relocate.</div>', unsafe_allow_html=True)
    else:
        st.markdown('<h2 class="section-header">🗺️ Geographic Hotspots Analysis</h2>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">💡 <strong>Key Insight:</strong> Some states and cities have more opportunities for H-1B workers. Understanding geographic trends helps you decide where to focus your job search and potentially relocate.</div>', unsafe_allow_html=True)
    
    if not df.empty:
        # Use the specific top states function for aggregated data
        top_states_df = get_top_states_data(company, soc_title, year_range, international_students_only)
        
        if not top_states_df.empty:
            # Enhanced Geographic Visualizations
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**🗺️ Top States by Opportunity Volume**")
                # Use aggregated data - SQL already calculated the counts
                top_states_viz = top_states_df.head(15)
                fig_top_states = px.scatter(top_states_viz, x='petition_count', y='state', 
                                          size='petition_count', color='avg_salary',
                                          title="Top States by Hiring Volume",
                                          labels={'petition_count': 'Number of Petitions', 'state': 'State', 'avg_salary': 'Avg Salary'},
                                          color_continuous_scale='blues')
                fig_top_states.update_layout(height=500, showlegend=False)
                st.plotly_chart(fig_top_states, use_container_width=True)
            
            with col2:
                st.markdown("**💰 Best Paying States**")
                # Filter to states with 100+ petitions and use aggregated data
                best_paying_states = top_states_df[top_states_df['petition_count'] >= 100].nlargest(15, 'avg_salary')
                
                # Create a more appealing salary visualization
                fig_salary_states = px.scatter(best_paying_states, x='avg_salary', y='state',
                                             size='petition_count', color='avg_salary',
                                             title="Best Paying States (100+ petitions)",
                                             labels={'avg_salary': 'Average Salary ($)', 'state': 'State', 'petition_count': 'Number of Petitions'},
                                             color_continuous_scale='plasma')
                fig_salary_states.update_layout(height=500, showlegend=False)
                st.plotly_chart(fig_salary_states, use_container_width=True)
            
            # Enhanced Cities Visualization - Note: Cities data not available in aggregated format
            st.markdown("**🏙️ Top Cities by Opportunity Volume**")
            st.info("City-level analysis requires detailed data. For aggregated analysis, focus on state-level trends above.")
            
            # Show top states instead
            st.markdown("**📊 Top States Summary**")
            top_states_summary = top_states_df.head(10)[['state', 'petition_count', 'avg_salary']]
            top_states_summary.columns = ['State', 'Petitions', 'Avg Salary']
            st.dataframe(top_states_summary, use_container_width=True)
            
            # Geographic insights for students using aggregated data
            st.markdown("**🌍 Geographic Insights for International Students**")
            geographic_summary = top_states_df[top_states_df['petition_count'] >= 100].copy()
            geographic_summary['% Level I'] = (geographic_summary['level1_count'] / geographic_summary['petition_count'] * 100).round(2)
            geographic_summary = geographic_summary[['state', 'petition_count', 'avg_salary', 'min_salary', 'max_salary', '% Level I']].sort_values('petition_count', ascending=False)
            geographic_summary.columns = ['State', 'Entry-Level Petitions', 'Avg Salary', 'Min Salary', 'Max Salary', '% Level I']
            st.dataframe(geographic_summary.head(15), use_container_width=True)
            
            # Key insights for students
            st.markdown("**🎯 Key Insights for Location Strategy:**")
            st.markdown("""
            - **California (CA):** Most opportunities, highest salaries, but high cost of living
            - **Texas (TX):** Growing tech hub, good salaries, lower cost of living
            - **New York (NY):** Finance and tech opportunities, high salaries
            - **Washington (WA):** Tech hub (Seattle), good work-life balance
            - **Strategy:** Consider cost of living vs. salary when choosing location
            """)
        else:
            st.warning("No entry-level geographic data found for the selected filters.")
    else:
        st.warning("No data available for the selected filters.")

with trends_tab4:
    if international_students_only:
        st.markdown('<h2 class="section-header">💼 Career Paths for International Students</h2>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">💡 <strong>Key Insight:</strong> Understanding which career paths have the most opportunities and best salaries helps you make informed decisions about your field of study and career direction. AI jobs are growing exponentially!</div>', unsafe_allow_html=True)
    else:
        st.markdown('<h2 class="section-header">💼 Career Paths Analysis</h2>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">💡 <strong>Key Insight:</strong> Understanding which career paths have the most opportunities and best salaries helps you make informed decisions about your career direction. AI jobs are growing exponentially!</div>', unsafe_allow_html=True)
    
    if not df.empty:
        # Get AI career data
        ai_career_df = get_ai_career_data(company, state, year_range, international_students_only)
        career_growth_df = get_career_growth_decline_data(company, state, year_range, international_students_only)
        
        # Data is already filtered by wage level based on toggle
        entry_level_careers = df
        
        if not entry_level_careers.empty:
            # Use aggregated data - AI career data is already filtered at SQL level
            combined_entry_careers = entry_level_careers.copy()
            
            # Add AI career data if available (already aggregated)
            if not ai_career_df.empty:
                # AI data is already aggregated, just combine the career categories
                ai_career_subset = ai_career_df[['YEAR', 'career_category', 'petition_count', 'avg_salary']].copy()
                ai_career_subset = ai_career_subset.rename(columns={'career_category': 'aggressive_normalized_soc_title'})
                combined_entry_careers = pd.concat([combined_entry_careers, ai_career_subset], ignore_index=True)
            
            # Career Path Growth & Salary Trends (Line Charts)
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**📈 Top Career Paths Growth Trends (2020-2024)**")
                
                # Get top 10 career paths by total count (data already filtered at SQL level)
                top_10_careers = combined_entry_careers['aggressive_normalized_soc_title'].value_counts().head(10).index.tolist()
                
                # Create growth trends data for top career paths using aggregated data
                top_career_trends = combined_entry_careers[combined_entry_careers['aggressive_normalized_soc_title'].isin(top_10_careers)]
                # Use petition_count from aggregated data instead of size()
                top_career_trends = top_career_trends.groupby(['YEAR', 'aggressive_normalized_soc_title'])['petition_count'].sum().reset_index()
                
                # Create line chart for top career paths growth
                fig_top_careers = px.line(top_career_trends, x='YEAR', y='petition_count', color='aggressive_normalized_soc_title',
                                        title="Top 10 Career Paths Growth Trends (2020-2024)",
                                        labels={'petition_count': 'Number of Entry-Level Petitions', 'YEAR': 'Year', 'aggressive_normalized_soc_title': 'Career Path'})
                fig_top_careers.update_layout(height=400)
                st.plotly_chart(fig_top_careers, use_container_width=True)
            
            with col2:
                st.markdown("**💰 Best Paying Career Paths Salary Trends (2020-2024)**")
                
                # Get top 10 paying career paths using aggregated data
                career_salary = combined_entry_careers.groupby('aggressive_normalized_soc_title').agg({
                    'avg_salary': 'mean',
                    'petition_count': 'sum'
                }).reset_index()
                career_salary = career_salary[career_salary['petition_count'] >= 10]  # Only career paths with 10+ entry-level petitions
                top_10_paying_careers = career_salary.nlargest(10, 'avg_salary')['aggressive_normalized_soc_title'].tolist()
                
                # Create salary trends data for top paying careers using aggregated data
                top_paying_trends = combined_entry_careers[combined_entry_careers['aggressive_normalized_soc_title'].isin(top_10_paying_careers)]
                top_paying_trends = top_paying_trends.groupby(['YEAR', 'aggressive_normalized_soc_title'])['avg_salary'].mean().reset_index()
                
                # Create line chart for salary trends
                fig_salary_trends = px.line(top_paying_trends, x='YEAR', y='avg_salary', color='aggressive_normalized_soc_title',
                                          title="Top 10 Paying Career Paths Salary Trends (2020-2024)",
                                          labels={'avg_salary': 'Average Salary ($)', 'YEAR': 'Year', 'aggressive_normalized_soc_title': 'Career Path'})
                fig_salary_trends.update_layout(height=400)
                st.plotly_chart(fig_salary_trends, use_container_width=True)
            

            
            # Career Growth vs Decline Trends
            if not career_growth_df.empty:
                st.markdown("**📈 Career Path Growth Trends (2020-2024) - Top 10 Growing**")
                
                # Calculate growth rates for each career path using year-by-year data
                career_growth_rates = []
                for career in career_growth_df['career_category'].unique():
                    career_data = career_growth_df[career_growth_df['career_category'] == career]
                    if len(career_data) >= 2:  # Need at least 2 years of data
                        # Sort by year to get start and end
                        career_data = career_data.sort_values('YEAR')
                        start_count = career_data.iloc[0]['petition_count']
                        end_count = career_data.iloc[-1]['petition_count']
                        if start_count > 0:
                            growth_rate = ((end_count - start_count) / start_count) * 100
                            career_growth_rates.append({
                                'career': career,
                                'growth_rate': growth_rate,
                                'start_count': start_count,
                                'end_count': end_count,
                                'total_petitions': career_data['petition_count'].sum()
                            })
                
                # Sort by growth rate and filter for meaningful careers (at least 50 total petitions)
                growth_df = pd.DataFrame(career_growth_rates)
                if not growth_df.empty:
                    growth_df = growth_df[growth_df['total_petitions'] >= 50]  # Only careers with meaningful volume
                    top_growing = growth_df.nlargest(10, 'growth_rate')
                    top_declining = growth_df.nsmallest(10, 'growth_rate')
                
                if not growth_df.empty:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**🚀 Top 10 Growing Careers**")
                        if not top_growing.empty:
                            fig_growing = px.bar(top_growing, x='growth_rate', y='career', orientation='h',
                                               title="Top 10 Growing Career Paths (2020-2024)",
                                               labels={'growth_rate': 'Growth Rate (%)', 'career': 'Career Path'})
                            fig_growing.update_layout(height=400)
                            st.plotly_chart(fig_growing, use_container_width=True)
                        else:
                            st.info("No growing careers found with sufficient data.")
                    
                    with col2:
                        st.markdown("**📉 Top 10 Declining Careers**")
                        if not top_declining.empty:
                            fig_declining = px.bar(top_declining, x='growth_rate', y='career', orientation='h',
                                                 title="Top 10 Declining Career Paths (2020-2024)",
                                                 labels={'growth_rate': 'Growth Rate (%)', 'career': 'Career Path'})
                            fig_declining.update_layout(height=400)
                            st.plotly_chart(fig_declining, use_container_width=True)
                        else:
                            st.info("No declining careers found with sufficient data.")
                else:
                    st.warning("No career growth data available for the selected filters.")
                
                # Show detailed growth data
                if not growth_df.empty:
                    st.markdown("**📊 Detailed Growth Analysis**")
                    growth_analysis = pd.concat([
                        top_growing.assign(type='Growing'),
                        top_declining.assign(type='Declining')
                    ])
                    st.dataframe(growth_analysis[['career', 'growth_rate', 'start_count', 'end_count', 'type']].round(2), use_container_width=True)
                else:
                    st.info("No detailed growth data available.")
            
            # Career path insights for students using aggregated data
            st.markdown("**🎯 Career Path Insights for International Students**")
            career_summary = entry_level_careers.groupby('aggressive_normalized_soc_title').agg({
                'petition_count': 'sum',
                'avg_salary': 'mean',
                'min_salary': 'min',
                'max_salary': 'max'
            }).round(2)
            # Calculate % Level I using aggregated data
            level_i_percentage = entry_level_careers.groupby('aggressive_normalized_soc_title').apply(
                lambda x: (x['level1_count'].sum() / x['petition_count'].sum() * 100) if x['petition_count'].sum() > 0 else 0
            ).round(2)
            career_summary['% Level I'] = level_i_percentage
            career_summary.columns = ['Entry-Level Petitions', 'Avg Salary', 'Min Salary', 'Max Salary', '% Level I']
            career_summary = career_summary[career_summary['Entry-Level Petitions'] >= 10].sort_values('Entry-Level Petitions', ascending=False)
            st.dataframe(career_summary.head(20), use_container_width=True)
            
            # Key insights for students
            st.markdown("**💡 Key Insights for Career Planning:**")
            st.markdown("""
            - **🤖 AI/ML & Data Science:** Fastest growing field, high salaries, exponential growth
            - **💻 Software Engineering:** Most opportunities, good salaries, high demand
            - **🔬 Research Scientists:** Highest salaries, competitive, requires advanced degrees
            - **🏥 Healthcare:** Stable demand, good salaries, requires specific education
            - **📊 Data Science:** Growing rapidly, good entry point for AI careers
            - **Strategy:** Focus on AI/ML if you want exponential growth opportunities!
            """)
        else:
            st.warning("No entry-level career paths found for the selected filters.")
    else:
        st.warning("No data available for the selected filters.")

with trends_tab5:
    if international_students_only:
        st.markdown('<h2 class="section-header">💰 Salary Insights for International Students</h2>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">💡 <strong>Key Insight:</strong> Understanding salary expectations helps you negotiate better offers and plan your financial future. Entry-level salaries vary significantly by field, location, and company type.</div>', unsafe_allow_html=True)
    else:
        st.markdown('<h2 class="section-header">💰 Salary Insights Analysis</h2>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">💡 <strong>Key Insight:</strong> Understanding salary expectations helps you negotiate better offers and plan your financial future. Salaries vary significantly by field, location, experience level, and company type.</div>', unsafe_allow_html=True)
    
    if not df.empty:
        # Use the specific salary insights function for aggregated data
        salary_insights_df = get_salary_insights_data(company, state, soc_title, year_range, international_students_only)
        
        if not salary_insights_df.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Entry-Level Salary Distribution by Field**")
                # Top 10 fields for entry-level using aggregated data
                top_fields = salary_insights_df['aggressive_normalized_soc_title'].value_counts().head(10).index.tolist()
                top_fields_data = salary_insights_df[salary_insights_df['aggressive_normalized_soc_title'].isin(top_fields)]
                
                fig_salary_field = px.bar(top_fields_data, x='aggressive_normalized_soc_title', y='avg_salary',
                                        title="Entry-Level Salary by Field",
                                        labels={'avg_salary': 'Average Salary ($)', 'aggressive_normalized_soc_title': 'Field'})
                fig_salary_field.update_layout(height=400, xaxis_tickangle=-45)
                st.plotly_chart(fig_salary_field, use_container_width=True)
            
            with col2:
                st.markdown("**Entry-Level Salary Trends by Year**")
                # Use aggregated data for salary trends
                salary_trends = salary_insights_df.groupby('aggressive_normalized_soc_title')['avg_salary'].mean().reset_index()
                
                fig_salary_trends = px.bar(salary_trends.head(10), x='avg_salary', y='aggressive_normalized_soc_title',
                                          title="Top 10 Paying Fields",
                                          labels={'avg_salary': 'Average Salary ($)', 'aggressive_normalized_soc_title': 'Field'})
                fig_salary_trends.update_layout(height=400)
                st.plotly_chart(fig_salary_trends, use_container_width=True)
            
            # Enhanced Salary by Location with Better Visualization
            st.markdown("**🗺️ Salary by Location**")
            # Use top states data for location salary analysis
            location_salary = top_states_df[top_states_df['petition_count'] >= 100].nlargest(15, 'avg_salary')
            
            # Create a more appealing location salary visualization with better styling
            fig_location_salary = px.scatter(location_salary, x='avg_salary', y='state',
                                           size='petition_count', color='avg_salary',
                                           title="Best Paying States (100+ petitions)",
                                           labels={'avg_salary': 'Average Salary ($)', 'state': 'State', 'petition_count': 'Number of Petitions'},
                                           color_continuous_scale='viridis',
                                           hover_data=['petition_count'])
            fig_location_salary.update_layout(
                height=500, 
                showlegend=False,
                title_font_size=16,
                xaxis_title_font_size=14,
                yaxis_title_font_size=14
            )
            fig_location_salary.update_traces(
                marker=dict(line=dict(width=1, color='white')),
                selector=dict(mode='markers')
            )
            st.plotly_chart(fig_location_salary, use_container_width=True)
            
            # Enhanced Salary Statistics
            st.markdown("**📊 Comprehensive Salary Statistics**")
            
            # Overall statistics using aggregated data
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Average Salary", f"${salary_insights_df['avg_salary'].mean():,.0f}")
            with col2:
                st.metric("Median Salary", f"${salary_insights_df['avg_salary'].median():,.0f}")
            with col3:
                st.metric("Min Salary", f"${salary_insights_df['min_salary'].min():,.0f}")
            with col4:
                st.metric("Max Salary", f"${salary_insights_df['max_salary'].max():,.0f}")
            
            # Salary distribution by field
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**📈 Top 10 Fields by Average Salary**")
                top_fields_stats = salary_insights_df.nlargest(10, 'avg_salary')[['aggressive_normalized_soc_title', 'avg_salary', 'petition_count']]
                top_fields_stats.columns = ['Field', 'Average Salary', 'Petitions']
                st.dataframe(top_fields_stats, use_container_width=True)
            
            with col2:
                st.markdown("**📊 Salary Range by Field**")
                salary_range_stats = salary_insights_df[['aggressive_normalized_soc_title', 'min_salary', 'max_salary', 'avg_salary']].head(10)
                salary_range_stats.columns = ['Field', 'Min Salary', 'Max Salary', 'Avg Salary']
                st.dataframe(salary_range_stats, use_container_width=True)
            
            # Enhanced Top Paying Fields with Better Visualization
            st.markdown("**💵 Top Paying Fields (100+ petitions)**")
            # Use aggregated data for top paying fields
            top_paying_fields = salary_insights_df[salary_insights_df['petition_count'] >= 100].nlargest(15, 'avg_salary').reset_index()
            top_paying_fields = top_paying_fields[['aggressive_normalized_soc_title', 'avg_salary', 'petition_count', 'min_salary', 'max_salary']]
            top_paying_fields.columns = ['Field', 'Avg Salary', 'Petitions', 'Min Salary', 'Max Salary']
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Bar chart for top paying fields
                fig_top_fields = px.bar(top_paying_fields, x='Avg Salary', y='Field',
                                      title="Top 15 Highest Paying Fields (100+ petitions)",
                                      labels={'Avg Salary': 'Average Salary ($)', 'Field': 'Field'},
                                      color='Avg Salary',
                                      color_continuous_scale='viridis')
                fig_top_fields.update_layout(height=500, yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig_top_fields, use_container_width=True)
            
            with col2:
                # Scatter plot showing salary vs petition count
                fig_salary_vs_volume = px.scatter(top_paying_fields, x='Petitions', y='Avg Salary',
                                                size='Avg Salary', color='Avg Salary',
                                                title="Salary vs Petition Volume (100+ petitions)",
                                                labels={'Petitions': 'Number of Petitions', 'Avg Salary': 'Average Salary ($)'},
                                                color_continuous_scale='plasma',
                                                hover_data=['Field'])
                fig_salary_vs_volume.update_layout(height=500)
                st.plotly_chart(fig_salary_vs_volume, use_container_width=True)
            
            # Detailed table
            st.markdown("**📊 Detailed Salary Statistics by Field**")
            st.dataframe(top_paying_fields, use_container_width=True)
            
            # Key insights for students
            st.markdown("**🎯 Key Insights for Salary Negotiation:**")
            st.markdown("""
            - **Research Your Field:** Know the average salary for your field and experience level
            - **Consider Location:** Salaries vary significantly by state/city
            - **Company Type Matters:** Big Tech pays more than IT services companies
            - **Negotiation Range:** Aim for 10-15% above the median for your field
            - **Benefits Matter:** Consider total compensation, not just salary
            """)
        else:
            st.warning("No entry-level salary data found for the selected filters.")
    else:
        st.warning("No data available for the selected filters.")

 