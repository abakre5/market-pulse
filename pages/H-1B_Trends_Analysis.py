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

@st.cache_data(ttl=3600, show_spinner=False)  # Cache for 1 hour
def get_trends_filter_options():
    """Get filter options for trends analysis"""
    with st.spinner("Loading filter options..."):
        try:
            con = get_db_connection()
            if con is None:
                return [], [], []
            
            companies = con.execute(f"SELECT DISTINCT STD_EMPLOYER_NAME_PARENT FROM {TABLE} WHERE VISA_CLASS = 'H-1B' AND is_lottery_petition = TRUE AND STD_EMPLOYER_NAME_PARENT != '' ORDER BY STD_EMPLOYER_NAME_PARENT").fetchdf()['STD_EMPLOYER_NAME_PARENT'].tolist()
            states = con.execute(f"SELECT DISTINCT EMPLOYER_STATE FROM {TABLE} WHERE VISA_CLASS = 'H-1B' AND is_lottery_petition = TRUE AND EMPLOYER_STATE IS NOT NULL ORDER BY EMPLOYER_STATE").fetchdf()['EMPLOYER_STATE'].tolist()
            soc_titles = con.execute(f"SELECT DISTINCT aggressive_normalized_soc_title FROM {TABLE} WHERE VISA_CLASS = 'H-1B' AND is_lottery_petition = TRUE AND aggressive_normalized_soc_title IS NOT NULL ORDER BY aggressive_normalized_soc_title").fetchdf()['aggressive_normalized_soc_title'].tolist()
            return companies, states, soc_titles
        except Exception as e:
            st.error(f"Failed to load filter options: {e}")
            return [], [], []

@st.cache_data(ttl=1800, show_spinner=False)  # Cache for 30 minutes
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

@st.cache_data(ttl=900, show_spinner=False)  # Cache for 15 minutes
def get_trends_filtered_data(company, state, soc_title, year_range, international_students_only=True):
    """Get filtered data for trends analysis"""
    with st.spinner("Loading trends data..."):
        try:
            con = get_db_connection()
            if con is None:
                return pd.DataFrame()
            
            query = f"SELECT * FROM {TABLE} WHERE VISA_CLASS = 'H-1B' AND is_lottery_petition = TRUE AND YEAR BETWEEN ? AND ? AND LOWER(aggressive_normalized_soc_title) NOT LIKE '%other%'"
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
            
            df = con.execute(query, params).fetchdf()
            return df
        except Exception as e:
            st.error(f"Error fetching trends data: {e}")
            return pd.DataFrame()

@st.cache_data(ttl=900, show_spinner=False)  # Cache for 15 minutes
def get_trends_yearly_data(company, state, soc_title, year_range, international_students_only=True):
    """Get yearly data for trends analysis (respects all filters EXCEPT year)"""
    with st.spinner("Loading yearly trends data..."):
        try:
            con = get_db_connection()
            if con is None:
                return pd.DataFrame()
            
            query = f"SELECT * FROM {TABLE} WHERE VISA_CLASS = 'H-1B' AND is_lottery_petition = TRUE AND YEAR BETWEEN ? AND ? AND LOWER(aggressive_normalized_soc_title) NOT LIKE '%other%'"
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
            
            query += " ORDER BY YEAR"
            df = con.execute(query, params).fetchdf()
            return df
        except Exception as e:
            st.error(f"Error fetching yearly trends data: {e}")
            return pd.DataFrame()

@st.cache_data(ttl=900, show_spinner=False)  # Cache for 15 minutes
def get_ai_career_data(company, state, year_range, international_students_only=True):
    """Get AI career data including Data Scientists, Research Scientists, and AI Software Developers"""
    with st.spinner("Loading AI career data..."):
        try:
            con = get_db_connection()
            if con is None:
                return pd.DataFrame()
            
            # Query for AI categories and AI Software Developers
            query = f"""
            SELECT *, 
                   CASE 
                       WHEN aggressive_normalized_soc_title IN ('Data Scientists', 'Computer and Information Research Scientists') 
                       OR (aggressive_normalized_soc_title = 'Software Developers' 
                       AND (JOB_TITLE LIKE '%Machine Learning%' OR JOB_TITLE LIKE '%AI%' OR JOB_TITLE LIKE '%ML%' OR JOB_TITLE LIKE '%Data Science%'))
                       THEN 'AI Developers'
                       ELSE aggressive_normalized_soc_title
                   END as career_category
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
            
            query += " ORDER BY YEAR"
            df = con.execute(query, params).fetchdf()
            return df
        except Exception as e:
            st.error(f"Error fetching AI career data: {e}")
            return pd.DataFrame()

@st.cache_data(ttl=900, show_spinner=False)  # Cache for 15 minutes
def get_career_growth_decline_data(company, state, year_range, international_students_only=True):
    """Get career growth and decline data for top categories"""
    with st.spinner("Loading career growth/decline data..."):
        try:
            con = get_db_connection()
            if con is None:
                return pd.DataFrame()
            
            # Get all career categories with yearly counts
            query = f"""
            SELECT aggressive_normalized_soc_title, YEAR, COUNT(*) as count
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
            
            query += " GROUP BY aggressive_normalized_soc_title, YEAR ORDER BY aggressive_normalized_soc_title, YEAR"
            df = con.execute(query, params).fetchdf()
            return df
        except Exception as e:
            st.error(f"Error fetching career growth/decline data: {e}")
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
                    chart_title = "H-1B Job Opportunities by Wage Level"
                
                entry_counts = entry_level_df.groupby(['YEAR', 'PW_WAGE_LEVEL']).size().reset_index(name='count')
                
                fig_entry_counts = px.line(entry_counts, x='YEAR', y='count', color='PW_WAGE_LEVEL',
                                         title=chart_title,
                                         labels={'count': 'Number of Petitions', 'YEAR': 'Year', 'PW_WAGE_LEVEL': 'Wage Level'})
                fig_entry_counts.update_layout(height=400)
                st.plotly_chart(fig_entry_counts, use_container_width=True)
            
            with col2:
                if international_students_only:
                    st.markdown("**Entry-Level Salary Trends**")
                    chart_title = "Entry-Level Salary Trends by Wage Level"
                else:
                    st.markdown("**Salary Trends by Experience Level**")
                    chart_title = "Salary Trends by Wage Level"
                
                entry_salary_trends = entry_level_df.groupby(['YEAR', 'PW_WAGE_LEVEL'])['PREVAILING_WAGE'].mean().reset_index()
                
                fig_entry_salary = px.line(entry_salary_trends, x='YEAR', y='PREVAILING_WAGE', color='PW_WAGE_LEVEL',
                                         title=chart_title,
                                         labels={'PREVAILING_WAGE': 'Average Salary ($)', 'YEAR': 'Year', 'PW_WAGE_LEVEL': 'Wage Level'})
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
            
            entry_stats = entry_level_df.groupby('PW_WAGE_LEVEL').agg({
                'PW_WAGE_LEVEL': 'count',
                'PREVAILING_WAGE': ['mean', 'median', 'min', 'max']
            }).round(0)
            entry_stats.columns = ['Total Petitions', 'Avg Salary', 'Median Salary', 'Min Salary', 'Max Salary']
            st.dataframe(entry_stats, use_container_width=True)
            
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
        # Focus on companies that hire entry-level positions
        entry_level_companies = df[df['PW_WAGE_LEVEL'].isin(['I', 'II'])]
        
        if not entry_level_companies.empty:
            top_entry_companies = entry_level_companies['STD_EMPLOYER_NAME_PARENT'].value_counts().head(20)
            
            # Enhanced Top Employers Visualization
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**🏆 Top Companies by Hiring Volume**")
                # Create a more appealing visualization with bubbles
                top_companies_df = pd.DataFrame({
                    'Company': top_entry_companies.index,
                    'Petitions': top_entry_companies.values
                })
                fig_top_companies = px.scatter(top_companies_df, x='Petitions', y='Company', 
                                             size='Petitions', color='Petitions',
                                             title="Top Companies by Entry-Level Hiring Volume",
                                             labels={'Petitions': 'Number of Petitions', 'Company': 'Company'},
                                             color_continuous_scale='viridis')
                fig_top_companies.update_layout(height=500, showlegend=False)
                st.plotly_chart(fig_top_companies, use_container_width=True)
            
            with col2:
                st.markdown("**💰 Best Paying Companies**")
                entry_salary = entry_level_companies.groupby('STD_EMPLOYER_NAME_PARENT')['PREVAILING_WAGE'].agg(['mean', 'count']).reset_index()
                entry_salary = entry_salary[entry_salary['count'] >= 100]  # Only companies with 100+ entry-level petitions
                top_salary_companies = entry_salary.nlargest(20, 'mean')
                
                # Create a more appealing salary visualization
                fig_salary_companies = px.scatter(top_salary_companies, x='mean', y='STD_EMPLOYER_NAME_PARENT',
                                                size='count', color='mean',
                                                title="Best Paying Companies (100+ petitions)",
                                                labels={'mean': 'Average Salary ($)', 'STD_EMPLOYER_NAME_PARENT': 'Company', 'count': 'Number of Petitions'},
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
            
            entry_level_companies['Company_Type'] = entry_level_companies['STD_EMPLOYER_NAME_PARENT'].apply(categorize_company_for_students)
            
            # Enhanced company type analysis with better visualization
            company_type_summary = entry_level_companies.groupby('Company_Type').agg({
                'PW_WAGE_LEVEL': 'count',
                'PREVAILING_WAGE': ['mean', 'median']
            }).round(0)
            company_type_summary.columns = ['Total Petitions', 'Avg Salary', 'Median Salary']
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
                                              hover_data=['Company_Type', 'Median Salary'])
                fig_company_salary.update_layout(height=500)
                st.plotly_chart(fig_company_salary, use_container_width=True)
            
            # Detailed company type statistics
            st.markdown("**📊 Company Type Statistics**")
            st.dataframe(significant_types, use_container_width=True)
            
            # Student-focused company summary
            st.markdown("**🎯 Top Companies for International Students**")
            student_company_summary = entry_level_companies.groupby('STD_EMPLOYER_NAME_PARENT').agg({
                'PW_WAGE_LEVEL': 'count',
                'PREVAILING_WAGE': ['mean', 'median']
            }).round(2)
            # Calculate % Level I separately
            level_i_percentage = entry_level_companies.groupby('STD_EMPLOYER_NAME_PARENT')['PW_WAGE_LEVEL'].apply(lambda x: (x == 'I').sum() / len(x) * 100).round(2)
            student_company_summary['% Level I'] = level_i_percentage
            student_company_summary.columns = ['Entry-Level Petitions', 'Avg Salary', 'Median Salary', '% Level I']
            student_company_summary = student_company_summary[student_company_summary['Entry-Level Petitions'] >= 5].sort_values('Entry-Level Petitions', ascending=False)
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
        # Focus on entry-level opportunities by location
        entry_level_states = df[df['PW_WAGE_LEVEL'].isin(['I', 'II'])]
        
        if not entry_level_states.empty:
            # Enhanced Geographic Visualizations
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**🗺️ Top States by Opportunity Volume**")
                top_entry_states = entry_level_states['EMPLOYER_STATE'].value_counts().head(15)
                # Create a more appealing state visualization
                states_df = pd.DataFrame({
                    'State': top_entry_states.index,
                    'Petitions': top_entry_states.values
                })
                fig_top_states = px.scatter(states_df, x='Petitions', y='State', 
                                          size='Petitions', color='Petitions',
                                          title="Top States by Entry-Level Hiring Volume",
                                          labels={'Petitions': 'Number of Petitions', 'State': 'State'},
                                          color_continuous_scale='blues')
                fig_top_states.update_layout(height=500, showlegend=False)
                st.plotly_chart(fig_top_states, use_container_width=True)
            
            with col2:
                st.markdown("**💰 Best Paying States**")
                entry_state_salary = entry_level_states.groupby('EMPLOYER_STATE')['PREVAILING_WAGE'].agg(['mean', 'count']).reset_index()
                entry_state_salary = entry_state_salary[entry_state_salary['count'] >= 20]  # Only states with 20+ entry-level petitions
                top_salary_states = entry_state_salary.nlargest(15, 'mean')
                
                # Create a more appealing salary visualization
                fig_salary_states = px.scatter(top_salary_states, x='mean', y='EMPLOYER_STATE',
                                             size='count', color='mean',
                                             title="Best Paying States (20+ petitions)",
                                             labels={'mean': 'Average Salary ($)', 'EMPLOYER_STATE': 'State', 'count': 'Number of Petitions'},
                                             color_continuous_scale='plasma')
                fig_salary_states.update_layout(height=500, showlegend=False)
                st.plotly_chart(fig_salary_states, use_container_width=True)
            
            # Enhanced Cities Visualization
            st.markdown("**🏙️ Top Cities by Opportunity Volume**")
            top_entry_cities = entry_level_states['EMPLOYER_CITY'].value_counts().head(20)
            
            # Create a more appealing city visualization
            cities_df = pd.DataFrame({
                'City': top_entry_cities.index,
                'Petitions': top_entry_cities.values
            })
            fig_top_cities = px.scatter(cities_df, x='Petitions', y='City', 
                                      size='Petitions', color='Petitions',
                                      title="Top Cities by Entry-Level Hiring Volume",
                                      labels={'Petitions': 'Number of Petitions', 'City': 'City'},
                                      color_continuous_scale='greens')
            fig_top_cities.update_layout(height=500, showlegend=False)
            st.plotly_chart(fig_top_cities, use_container_width=True)
            
            # Geographic insights for students
            st.markdown("**🌍 Geographic Insights for International Students**")
            geographic_summary = entry_level_states.groupby('EMPLOYER_STATE').agg({
                'PW_WAGE_LEVEL': 'count',
                'PREVAILING_WAGE': ['mean', 'median']
            }).round(2)
            # Calculate % Level I separately
            level_i_percentage = entry_level_states.groupby('EMPLOYER_STATE')['PW_WAGE_LEVEL'].apply(lambda x: (x == 'I').sum() / len(x) * 100).round(2)
            geographic_summary['% Level I'] = level_i_percentage
            geographic_summary.columns = ['Entry-Level Petitions', 'Avg Salary', 'Median Salary', '% Level I']
            geographic_summary = geographic_summary[geographic_summary['Entry-Level Petitions'] >= 20].sort_values('Entry-Level Petitions', ascending=False)
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
            # Combine regular career data with AI career data for entry-level analysis
            entry_level_ai = ai_career_df[ai_career_df['PW_WAGE_LEVEL'].isin(['I', 'II'])]
            
            # Create combined entry-level career data
            combined_entry_careers = entry_level_careers.copy()
            if not entry_level_ai.empty:
                # Add AI career data to entry-level analysis
                # Select only the columns that exist in both DataFrames
                common_columns = list(set(entry_level_careers.columns) & set(entry_level_ai.columns))
                entry_level_ai_subset = entry_level_ai[common_columns].copy()
                entry_level_ai_subset['aggressive_normalized_soc_title'] = entry_level_ai['career_category']
                combined_entry_careers = pd.concat([combined_entry_careers, entry_level_ai_subset], ignore_index=True)
            
            # Career Path Growth & Salary Trends (Line Charts)
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**📈 Top Career Paths Growth Trends (2020-2024)**")
                
                # Get top 10 career paths by total count (data already filtered at SQL level)
                top_10_careers = combined_entry_careers['aggressive_normalized_soc_title'].value_counts().head(10).index.tolist()
                
                # Create growth trends data for top career paths
                top_career_trends = combined_entry_careers[combined_entry_careers['aggressive_normalized_soc_title'].isin(top_10_careers)]
                top_career_trends = top_career_trends.groupby(['YEAR', 'aggressive_normalized_soc_title']).size().reset_index(name='count')
                
                # Create line chart for top career paths growth
                fig_top_careers = px.line(top_career_trends, x='YEAR', y='count', color='aggressive_normalized_soc_title',
                                        title="Top 10 Career Paths Growth Trends (2020-2024)",
                                        labels={'count': 'Number of Entry-Level Petitions', 'YEAR': 'Year', 'aggressive_normalized_soc_title': 'Career Path'})
                fig_top_careers.update_layout(height=400)
                st.plotly_chart(fig_top_careers, use_container_width=True)
            
            with col2:
                st.markdown("**💰 Best Paying Career Paths Salary Trends (2020-2024)**")
                
                # Get top 10 paying career paths (data already filtered at SQL level)
                career_salary = combined_entry_careers.groupby('aggressive_normalized_soc_title')['PREVAILING_WAGE'].agg(['mean', 'count']).reset_index()
                career_salary = career_salary[career_salary['count'] >= 10]  # Only career paths with 10+ entry-level petitions
                top_10_paying_careers = career_salary.nlargest(10, 'mean')['aggressive_normalized_soc_title'].tolist()
                
                # Create salary trends data for top paying careers
                top_paying_trends = combined_entry_careers[combined_entry_careers['aggressive_normalized_soc_title'].isin(top_10_paying_careers)]
                top_paying_trends = top_paying_trends.groupby(['YEAR', 'aggressive_normalized_soc_title'])['PREVAILING_WAGE'].mean().reset_index()
                
                # Create line chart for salary trends
                fig_salary_trends = px.line(top_paying_trends, x='YEAR', y='PREVAILING_WAGE', color='aggressive_normalized_soc_title',
                                          title="Top 10 Paying Career Paths Salary Trends (2020-2024)",
                                          labels={'PREVAILING_WAGE': 'Average Salary ($)', 'YEAR': 'Year', 'aggressive_normalized_soc_title': 'Career Path'})
                fig_salary_trends.update_layout(height=400)
                st.plotly_chart(fig_salary_trends, use_container_width=True)
            

            
            # Career Growth vs Decline Trends
            if not career_growth_df.empty:
                st.markdown("**📈 Career Path Growth Trends (2020-2024) - Top 10 Growing**")
                
                # Data already filtered at SQL level, no need for manual filtering
                combined_career_data = career_growth_df.copy()
                
                # Add AI career data to the growth analysis
                if not ai_career_df.empty:
                    ai_career_trends = ai_career_df.groupby(['YEAR', 'career_category']).size().reset_index(name='count')
                    ai_career_trends = ai_career_trends.rename(columns={'career_category': 'aggressive_normalized_soc_title'})
                    combined_career_data = pd.concat([combined_career_data, ai_career_trends], ignore_index=True)
                
                # Calculate growth rates for each career path
                career_growth_rates = []
                for career in combined_career_data['aggressive_normalized_soc_title'].unique():
                    career_data = combined_career_data[combined_career_data['aggressive_normalized_soc_title'] == career]
                    if len(career_data) >= 2:  # Need at least 2 years of data
                        start_count = career_data.iloc[0]['count']
                        end_count = career_data.iloc[-1]['count']
                        if start_count > 0:
                            growth_rate = ((end_count - start_count) / start_count) * 100
                            career_growth_rates.append({
                                'career': career,
                                'growth_rate': growth_rate,
                                'start_count': start_count,
                                'end_count': end_count
                            })
                
                # Sort by growth rate
                growth_df = pd.DataFrame(career_growth_rates)
                top_growing = growth_df.nlargest(10, 'growth_rate')
                top_declining = growth_df.nsmallest(10, 'growth_rate')
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**🚀 Top 10 Growing Careers**")
                    fig_growing = px.bar(top_growing, x='growth_rate', y='career', orientation='h',
                                       title="Top 10 Growing Career Paths (2020-2024)",
                                       labels={'growth_rate': 'Growth Rate (%)', 'career': 'Career Path'})
                    fig_growing.update_layout(height=400)
                    st.plotly_chart(fig_growing, use_container_width=True)
                
                with col2:
                    st.markdown("**📉 Top 10 Declining Careers**")
                    fig_declining = px.bar(top_declining, x='growth_rate', y='career', orientation='h',
                                         title="Top 10 Declining Career Paths (2020-2024)",
                                         labels={'growth_rate': 'Growth Rate (%)', 'career': 'Career Path'})
                    fig_declining.update_layout(height=400)
                    st.plotly_chart(fig_declining, use_container_width=True)
                
                # Show detailed growth data
                st.markdown("**📊 Detailed Growth Analysis**")
                growth_analysis = pd.concat([
                    top_growing.assign(type='Growing'),
                    top_declining.assign(type='Declining')
                ])
                st.dataframe(growth_analysis[['career', 'growth_rate', 'start_count', 'end_count', 'type']].round(2), use_container_width=True)
            
            # Career path insights for students
            st.markdown("**🎯 Career Path Insights for International Students**")
            career_summary = entry_level_careers.groupby('aggressive_normalized_soc_title').agg({
                'PW_WAGE_LEVEL': 'count',
                'PREVAILING_WAGE': ['mean', 'median']
            }).round(2)
            # Calculate % Level I separately
            level_i_percentage = entry_level_careers.groupby('aggressive_normalized_soc_title')['PW_WAGE_LEVEL'].apply(lambda x: (x == 'I').sum() / len(x) * 100).round(2)
            career_summary['% Level I'] = level_i_percentage
            career_summary.columns = ['Entry-Level Petitions', 'Avg Salary', 'Median Salary', '% Level I']
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
        # Focus on entry-level salaries
        entry_level_salary = df[df['PW_WAGE_LEVEL'].isin(['I', 'II'])]
        
        if not entry_level_salary.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Entry-Level Salary Distribution by Field**")
                # Top 10 fields for entry-level
                top_fields = entry_level_salary['aggressive_normalized_soc_title'].value_counts().head(10).index.tolist()
                top_fields_data = entry_level_salary[entry_level_salary['aggressive_normalized_soc_title'].isin(top_fields)]
                
                fig_salary_field = px.box(top_fields_data, x='aggressive_normalized_soc_title', y='PREVAILING_WAGE',
                                        title="Entry-Level Salary Distribution by Field",
                                        labels={'PREVAILING_WAGE': 'Salary ($)', 'aggressive_normalized_soc_title': 'Field'})
                fig_salary_field.update_layout(height=400, xaxis_tickangle=-45)
                st.plotly_chart(fig_salary_field, use_container_width=True)
            
            with col2:
                st.markdown("**Entry-Level Salary Trends by Year**")
                entry_salary_trends = entry_level_salary.groupby(['YEAR', 'PW_WAGE_LEVEL'])['PREVAILING_WAGE'].mean().reset_index()
                
                fig_salary_trends = px.line(entry_salary_trends, x='YEAR', y='PREVAILING_WAGE', color='PW_WAGE_LEVEL',
                                          title="Entry-Level Salary Trends (2020-2024)",
                                          labels={'PREVAILING_WAGE': 'Average Salary ($)', 'YEAR': 'Year', 'PW_WAGE_LEVEL': 'Wage Level'})
                fig_salary_trends.update_layout(height=400)
                st.plotly_chart(fig_salary_trends, use_container_width=True)
            
            # Enhanced Salary by Location with Better Visualization
            st.markdown("**🗺️ Salary by Location**")
            entry_location_salary = entry_level_salary.groupby('EMPLOYER_STATE')['PREVAILING_WAGE'].agg(['mean', 'count']).reset_index()
            entry_location_salary = entry_location_salary[entry_location_salary['count'] >= 100]  # Only states with 100+ entry-level petitions
            top_salary_states = entry_location_salary.nlargest(15, 'mean')
            
            # Create a more appealing location salary visualization with better styling
            fig_location_salary = px.scatter(top_salary_states, x='mean', y='EMPLOYER_STATE',
                                           size='count', color='mean',
                                           title="Best Paying States (100+ petitions)",
                                           labels={'mean': 'Average Salary ($)', 'EMPLOYER_STATE': 'State', 'count': 'Number of Petitions'},
                                           color_continuous_scale='viridis',
                                           hover_data=['count'])
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
            
            # Overall statistics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Average Salary", f"${entry_level_salary['PREVAILING_WAGE'].mean():,.0f}")
            with col2:
                st.metric("Median Salary", f"${entry_level_salary['PREVAILING_WAGE'].median():,.0f}")
            with col3:
                st.metric("25th Percentile", f"${entry_level_salary['PREVAILING_WAGE'].quantile(0.25):,.0f}")
            with col4:
                st.metric("75th Percentile", f"${entry_level_salary['PREVAILING_WAGE'].quantile(0.75):,.0f}")
            
            # Salary distribution by wage level
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**📈 Salary Distribution by Experience Level**")
                wage_level_stats = entry_level_salary.groupby('PW_WAGE_LEVEL')['PREVAILING_WAGE'].agg(['mean', 'median', 'count']).round(0)
                wage_level_stats.columns = ['Average Salary', 'Median Salary', 'Number of Petitions']
                st.dataframe(wage_level_stats, use_container_width=True)
            
            with col2:
                st.markdown("**📊 Salary Percentiles by Experience Level**")
                percentiles = entry_level_salary.groupby('PW_WAGE_LEVEL')['PREVAILING_WAGE'].quantile([0.25, 0.5, 0.75, 0.9]).round(0)
                percentiles_df = percentiles.unstack()
                percentiles_df.columns = ['25th Percentile', 'Median', '75th Percentile', '90th Percentile']
                st.dataframe(percentiles_df, use_container_width=True)
            
            # Enhanced Top Paying Fields with Better Visualization
            st.markdown("**💵 Top Paying Fields (100+ petitions)**")
            salary_insights = entry_level_salary.groupby('aggressive_normalized_soc_title').agg({
                'PW_WAGE_LEVEL': 'count',
                'PREVAILING_WAGE': ['mean', 'median', 'std', 'min', 'max']
            }).round(0)
            salary_insights.columns = ['Petitions', 'Avg Salary', 'Median Salary', 'Std Dev', 'Min Salary', 'Max Salary']
            salary_insights = salary_insights[salary_insights['Petitions'] >= 100].sort_values('Avg Salary', ascending=False)
            
            # Create a better visualization for top paying fields
            top_paying_fields = salary_insights.head(15).reset_index()
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Bar chart for top paying fields
                fig_top_fields = px.bar(top_paying_fields, x='Avg Salary', y='aggressive_normalized_soc_title',
                                      title="Top 15 Highest Paying Fields (100+ petitions)",
                                      labels={'Avg Salary': 'Average Salary ($)', 'aggressive_normalized_soc_title': 'Field'},
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
                                                hover_data=['aggressive_normalized_soc_title'])
                fig_salary_vs_volume.update_layout(height=500)
                st.plotly_chart(fig_salary_vs_volume, use_container_width=True)
            
            # Detailed table
            st.markdown("**📊 Detailed Salary Statistics by Field**")
            st.dataframe(salary_insights.head(15), use_container_width=True)
            
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

 