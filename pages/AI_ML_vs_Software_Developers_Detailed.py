import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import gc

# Set page to wide layout
st.set_page_config(layout="wide")

# Import the shared database connection
from database_connection import get_db_connection

# Database configuration
TABLE = 'job_market_data_aggressive_normalized'

def get_comprehensive_ai_ml_data():
    """Get comprehensive data for AI/ML vs Software Developers analysis - OPTIMIZED VERSION"""
    with st.spinner("Loading comprehensive AI/ML vs Software Developers data..."):
        try:
            con = get_db_connection()
            if con is None:
                return pd.DataFrame()
            
            # Single optimized query that gets all data needed
            query = f"""
            WITH career_categories AS (
                SELECT 
                    YEAR,
                    EMPLOYER_STATE,
                    STD_EMPLOYER_NAME_PARENT,
                    CASE 
                        WHEN (
                            -- Comprehensive AI/ML titles (excluding overly broad %engineer%)
                             LOWER(JOB_TITLE) LIKE '%ai engineer%' OR
                            LOWER(JOB_TITLE) LIKE '%ml engineer%' OR
                            LOWER(JOB_TITLE) LIKE '%machine learning engineer%' OR
                            LOWER(JOB_TITLE) LIKE '%artificial intelligence engineer%' OR
                            LOWER(JOB_TITLE) LIKE '%deep learning engineer%' OR
                            LOWER(JOB_TITLE) LIKE '%ai/ml engineer%' OR
                            LOWER(JOB_TITLE) LIKE '%ai-ml engineer%' OR
                            LOWER(JOB_TITLE) LIKE '%ai ml engineer%' OR
                            LOWER(JOB_TITLE) LIKE '%computer vision engineer%' OR
                            LOWER(JOB_TITLE) LIKE '%nlp engineer%' OR
                            LOWER(JOB_TITLE) LIKE '%natural language engineer%' OR
                            LOWER(JOB_TITLE) LIKE '%robotics engineer%' OR
                            LOWER(JOB_TITLE) LIKE '%autonomous engineer%' OR
                            LOWER(JOB_TITLE) LIKE '%self-driving engineer%' OR
                            LOWER(JOB_TITLE) LIKE '%recommendation engineer%' OR
                            LOWER(JOB_TITLE) LIKE '%search engineer%' OR
                            LOWER(JOB_TITLE) LIKE '%ranking engineer%' OR
                            LOWER(JOB_TITLE) LIKE '%mlops engineer%' OR
                            LOWER(JOB_TITLE) LIKE '%machine learning ops%' OR
                            LOWER(JOB_TITLE) LIKE '%ai infrastructure engineer%' OR
                            LOWER(JOB_TITLE) LIKE '%ml infrastructure engineer%' OR
                            LOWER(JOB_TITLE) LIKE '%ai platform engineer%' OR
                            LOWER(JOB_TITLE) LIKE '%ml platform engineer%' OR
                            LOWER(JOB_TITLE) LIKE '%llm engineer%' OR
                            LOWER(JOB_TITLE) LIKE '%large language model engineer%' OR
                            LOWER(JOB_TITLE) LIKE '%transformer engineer%' OR
                            LOWER(JOB_TITLE) LIKE '%generative ai engineer%' OR
                            LOWER(JOB_TITLE) LIKE '%genai engineer%' OR
                            LOWER(JOB_TITLE) LIKE '%diffusion engineer%' OR
                            LOWER(JOB_TITLE) LIKE '%multimodal engineer%' OR
                            LOWER(JOB_TITLE) LIKE '%vision-language engineer%' OR
                            LOWER(JOB_TITLE) LIKE '%ai algorithm developer%' OR
                            LOWER(JOB_TITLE) LIKE '%perception engineer%' OR
                            LOWER(JOB_TITLE) LIKE '%conversational ai engineer%' OR
                            LOWER(JOB_TITLE) LIKE '%ai researcher%' OR
                            LOWER(JOB_TITLE) LIKE '%ml researcher%' OR
                            LOWER(JOB_TITLE) LIKE '%machine learning researcher%' OR
                            LOWER(JOB_TITLE) LIKE '%ai scientist%' OR
                            LOWER(JOB_TITLE) LIKE '%ml scientist%' OR
                            LOWER(JOB_TITLE) LIKE '%machine learning scientist%' OR
                            LOWER(JOB_TITLE) LIKE '%ai specialist%' OR
                            LOWER(JOB_TITLE) LIKE '%ml specialist%' OR
                            LOWER(JOB_TITLE) LIKE '%machine learning specialist%' OR
                            LOWER(JOB_TITLE) LIKE '%ai developer%' OR
                            LOWER(JOB_TITLE) LIKE '%ml developer%' OR
                            LOWER(JOB_TITLE) LIKE '%machine learning developer%' OR
                            LOWER(JOB_TITLE) LIKE '%artificial intelligence%' OR
                            LOWER(JOB_TITLE) LIKE '%machine learning%' OR
                            LOWER(JOB_TITLE) LIKE '%deep learning%' OR
                            LOWER(JOB_TITLE) LIKE '%computer vision%' OR
                            LOWER(JOB_TITLE) LIKE '%natural language processing%' OR
                            LOWER(JOB_TITLE) LIKE '%robotics%' OR
                            LOWER(JOB_TITLE) LIKE '%autonomous%' OR
                            LOWER(JOB_TITLE) LIKE '%self-driving%' OR
                            LOWER(JOB_TITLE) LIKE '%recommendation%' OR
                            LOWER(JOB_TITLE) LIKE '%nlp%' OR
                            LOWER(JOB_TITLE) LIKE '%search%' OR
                            LOWER(JOB_TITLE) LIKE '%ranking%' OR
                            LOWER(JOB_TITLE) LIKE '%mlops%' OR
                            LOWER(JOB_TITLE) LIKE '%machine learning ops%' OR
                            LOWER(JOB_TITLE) LIKE '%machine%' OR
                            LOWER(JOB_TITLE) LIKE '%ai infrastructure%' OR
                            LOWER(JOB_TITLE) LIKE '%ml infrastructure%' OR
                            LOWER(JOB_TITLE) LIKE '%ai platform%' OR
                            LOWER(JOB_TITLE) LIKE '%ml platform%' OR
                            LOWER(JOB_TITLE) LIKE '%llm%' OR
                            LOWER(JOB_TITLE) LIKE '%large language model%' OR
                            LOWER(JOB_TITLE) LIKE '%transformer%' OR
                            LOWER(JOB_TITLE) LIKE '%generative ai%' OR
                            LOWER(JOB_TITLE) LIKE '%genai%' OR
                            LOWER(JOB_TITLE) LIKE '%diffusion%' OR
                            LOWER(JOB_TITLE) LIKE '%multimodal%' OR
                            LOWER(JOB_TITLE) LIKE '%vision-language%' OR
                            LOWER(JOB_TITLE) LIKE '%ai algorithm%' OR
                            LOWER(JOB_TITLE) LIKE '%ai/ml%' OR
                            LOWER(JOB_TITLE) LIKE '%ai-ml%' OR
                            LOWER(JOB_TITLE) LIKE '%ai ml%' OR
                            LOWER(JOB_TITLE) LIKE '%perception%' OR
                            LOWER(JOB_TITLE) LIKE '%conversational%' OR
                            LOWER(JOB_TITLE) LIKE '%neural network%' OR
                            LOWER(JOB_TITLE) LIKE '%neural networks%' OR
                            LOWER(JOB_TITLE) LIKE '%tensorflow%' OR
                            LOWER(JOB_TITLE) LIKE '%pytorch%' OR
                            LOWER(JOB_TITLE) LIKE '%keras%' OR
                            LOWER(JOB_TITLE) LIKE '%scikit%' OR
                            LOWER(JOB_TITLE) LIKE '%opencv%' OR
                            LOWER(JOB_TITLE) LIKE '%bert%' OR
                            LOWER(JOB_TITLE) LIKE '%gpt%' OR
                            LOWER(JOB_TITLE) LIKE '%spark%' OR
                            LOWER(JOB_TITLE) LIKE '%hadoop%' OR
                            LOWER(JOB_TITLE) LIKE '%kafka%' OR
                            LOWER(JOB_TITLE) LIKE '%airflow%' OR
                            LOWER(JOB_TITLE) LIKE '%kubernetes%' OR
                            LOWER(JOB_TITLE) LIKE '%jupyter%' OR
                            LOWER(JOB_TITLE) LIKE '%notebook%' OR
                            LOWER(JOB_TITLE) LIKE '%colab%' OR
                            LOWER(JOB_TITLE) LIKE '%databricks%' OR
                            LOWER(JOB_TITLE) LIKE '%mlflow%' OR
                            LOWER(JOB_TITLE) LIKE '%kubeflow%' OR
                            LOWER(JOB_TITLE) LIKE '%sagemaker%' OR
                            LOWER(JOB_TITLE) LIKE '%vertex ai%' OR
                            LOWER(JOB_TITLE) LIKE '%ai platform%' OR
                            LOWER(JOB_TITLE) LIKE '%ml platform%' OR
                            LOWER(JOB_TITLE) LIKE '%ai infrastructure%' OR
                            LOWER(JOB_TITLE) LIKE '%ml infrastructure%' OR
                            LOWER(JOB_TITLE) LIKE '%chatbot%' OR
                            LOWER(JOB_TITLE) LIKE '%conversational ai%' OR
                            LOWER(JOB_TITLE) LIKE '%dialogue%' OR
                            LOWER(JOB_TITLE) LIKE '%fraud detection%' OR
                            LOWER(JOB_TITLE) LIKE '%anomaly detection%' OR
                            LOWER(JOB_TITLE) LIKE '%personalization%' OR
                            LOWER(JOB_TITLE) LIKE '%autonomous driving%' OR
                            LOWER(JOB_TITLE) LIKE '%autopilot%' OR
                            LOWER(JOB_TITLE) LIKE '%robotic process automation%' OR
                            LOWER(JOB_TITLE) LIKE '%rpa%' OR
                            LOWER(JOB_TITLE) LIKE '%big data%' OR
                            LOWER(JOB_TITLE) LIKE '%perception%' OR
                            LOWER(JOB_TITLE) LIKE '%vision%' OR
                            LOWER(JOB_TITLE) LIKE '%speech%' OR
                            LOWER(JOB_TITLE) LIKE '%language%' OR
                            LOWER(JOB_TITLE) LIKE '%conversation%' OR
                            LOWER(JOB_TITLE) LIKE '%dialogue%' OR
                            LOWER(JOB_TITLE) LIKE '%cto%' OR
                            LOWER(JOB_TITLE) LIKE '%ceo%' OR
                            LOWER(JOB_TITLE) LIKE '%director%' OR
                            LOWER(JOB_TITLE) LIKE '%chief%' OR
                            LOWER(JOB_TITLE) LIKE '%vp%' OR
                            LOWER(JOB_TITLE) LIKE '%vice president%' OR
                            LOWER(JOB_TITLE) LIKE '%vice%' OR
                            LOWER(JOB_TITLE) LIKE '%chatbot%' OR
                            LOWER(JOB_TITLE) LIKE '%autonomous%' OR
                            LOWER(JOB_TITLE) LIKE '%self-driving%' OR
                            LOWER(JOB_TITLE) LIKE '%autopilot%' OR
                            LOWER(JOB_TITLE) LIKE '%robotics%' OR
                            LOWER(JOB_TITLE) LIKE '%computer vision%' OR
                            LOWER(JOB_TITLE) LIKE '%nlp%' OR
                            LOWER(JOB_TITLE) LIKE '%natural language%' OR
                            LOWER(JOB_TITLE) LIKE '%deep learning%' OR
                            LOWER(JOB_TITLE) LIKE '%neural%' OR
                            LOWER(JOB_TITLE) LIKE '%transformer%' OR
                            LOWER(JOB_TITLE) LIKE '%llm%' OR
                            LOWER(JOB_TITLE) LIKE '%large language%' OR
                            LOWER(JOB_TITLE) LIKE '%generative%' OR
                            LOWER(JOB_TITLE) LIKE '%genai%' OR
                            LOWER(JOB_TITLE) LIKE '%diffusion%' OR
                            LOWER(JOB_TITLE) LIKE '%multimodal%' OR
                            LOWER(JOB_TITLE) LIKE '%vision-language%' OR
                            LOWER(JOB_TITLE) LIKE '%algorithm%' OR
                            LOWER(JOB_TITLE) LIKE '%ai/ml%' OR
                            LOWER(JOB_TITLE) LIKE '%ai-ml%' OR
                            LOWER(JOB_TITLE) LIKE '%ai ml%' OR
                            LOWER(JOB_TITLE) LIKE '%conversational%' OR
                            LOWER(JOB_TITLE) LIKE '%neural network%' OR
                            LOWER(JOB_TITLE) LIKE '%neural networks%' OR
                            LOWER(JOB_TITLE) LIKE '%tensorflow%' OR
                            LOWER(JOB_TITLE) LIKE '%pytorch%' OR
                            LOWER(JOB_TITLE) LIKE '%keras%' OR
                            LOWER(JOB_TITLE) LIKE '%scikit%' OR
                            LOWER(JOB_TITLE) LIKE '%opencv%' OR
                            LOWER(JOB_TITLE) LIKE '%bert%' OR
                            LOWER(JOB_TITLE) LIKE '%gpt%' OR
                            LOWER(JOB_TITLE) LIKE '%spark%' OR
                            LOWER(JOB_TITLE) LIKE '%hadoop%' OR
                            LOWER(JOB_TITLE) LIKE '%kafka%' OR
                            LOWER(JOB_TITLE) LIKE '%airflow%' OR
                            LOWER(JOB_TITLE) LIKE '%kubernetes%' OR
                            LOWER(JOB_TITLE) LIKE '%jupyter%' OR
                            LOWER(JOB_TITLE) LIKE '%notebook%' OR
                            LOWER(JOB_TITLE) LIKE '%colab%' OR
                            LOWER(JOB_TITLE) LIKE '%databricks%' OR
                            LOWER(JOB_TITLE) LIKE '%mlflow%' OR
                            LOWER(JOB_TITLE) LIKE '%kubeflow%' OR
                            LOWER(JOB_TITLE) LIKE '%sagemaker%' OR
                            LOWER(JOB_TITLE) LIKE '%vertex ai%' OR
                            LOWER(JOB_TITLE) LIKE '%ai platform%' OR
                            LOWER(JOB_TITLE) LIKE '%ml platform%' OR
                            LOWER(JOB_TITLE) LIKE '%ai infrastructure%' OR
                            LOWER(JOB_TITLE) LIKE '%ml infrastructure%' OR
                            LOWER(JOB_TITLE) LIKE '%chatbot%' OR
                            LOWER(JOB_TITLE) LIKE '%conversational ai%' OR
                            LOWER(JOB_TITLE) LIKE '%dialogue%' OR
                            LOWER(JOB_TITLE) LIKE '%fraud detection%' OR
                            LOWER(JOB_TITLE) LIKE '%anomaly detection%' OR
                            LOWER(JOB_TITLE) LIKE '%personalization%' OR
                            LOWER(JOB_TITLE) LIKE '%autonomous driving%' OR
                            LOWER(JOB_TITLE) LIKE '%autopilot%' OR
                            LOWER(JOB_TITLE) LIKE '%science%' OR
                            LOWER(JOB_TITLE) LIKE '%robotic process automation%' OR
                            LOWER(JOB_TITLE) LIKE '%rpa%'
                        ) 
                        THEN 'AI/ML Engineers'
                        WHEN aggressive_normalized_soc_title = 'Software Developers'
                        THEN 'Software Developers'
                        ELSE 'Other'
                    END as career_category,
                    PREVAILING_WAGE,
                    PW_WAGE_LEVEL
                FROM {TABLE} 
                WHERE VISA_CLASS = 'H-1B' AND is_lottery_petition = TRUE 
                AND YEAR BETWEEN 2020 AND 2024
            ),
            main_data AS (
                SELECT 
                    YEAR,
                    career_category,
                    COUNT(*) as petition_count,
                    AVG(PREVAILING_WAGE) as avg_salary,
                    MIN(PREVAILING_WAGE) as min_salary,
                    MAX(PREVAILING_WAGE) as max_salary,
                    COUNT(CASE WHEN PW_WAGE_LEVEL = 'I' THEN 1 END) as levelI_count,
                    COUNT(CASE WHEN PW_WAGE_LEVEL = 'II' THEN 1 END) as levelII_count,
                    COUNT(CASE WHEN PW_WAGE_LEVEL = 'III' THEN 1 END) as levelIII_count,
                    COUNT(CASE WHEN PW_WAGE_LEVEL = 'IV' THEN 1 END) as levelIV_count
                FROM career_categories
                WHERE career_category IN ('AI/ML Engineers', 'Software Developers')
                GROUP BY YEAR, career_category
            ),
            employer_data AS (
                SELECT 
                    STD_EMPLOYER_NAME_PARENT,
                    COUNT(*) as petition_count
                FROM career_categories
                WHERE career_category = 'AI/ML Engineers' AND STD_EMPLOYER_NAME_PARENT != ''
                GROUP BY STD_EMPLOYER_NAME_PARENT
                ORDER BY petition_count DESC
                LIMIT 15
            ),
            state_data AS (
                SELECT 
                    EMPLOYER_STATE,
                    COUNT(*) as petition_count
                FROM career_categories
                WHERE career_category = 'AI/ML Engineers' AND EMPLOYER_STATE IS NOT NULL
                GROUP BY EMPLOYER_STATE
                ORDER BY petition_count DESC
                LIMIT 15
            )
            SELECT 
                'main' as data_type,
                YEAR,
                career_category,
                petition_count,
                avg_salary,
                min_salary,
                max_salary,
                levelI_count,
                levelII_count,
                levelIII_count,
                levelIV_count,
                NULL as employer_state,
                NULL as std_employer_name_parent
            FROM main_data
            UNION ALL
            SELECT 
                'employer' as data_type,
                NULL as YEAR,
                'AI/ML Engineers' as career_category,
                petition_count,
                NULL as avg_salary,
                NULL as min_salary,
                NULL as max_salary,
                NULL as levelI_count,
                NULL as levelII_count,
                NULL as levelIII_count,
                NULL as levelIV_count,
                NULL as employer_state,
                STD_EMPLOYER_NAME_PARENT as std_employer_name_parent
            FROM employer_data
            UNION ALL
            SELECT 
                'state' as data_type,
                NULL as YEAR,
                'AI/ML Engineers' as career_category,
                petition_count,
                NULL as avg_salary,
                NULL as min_salary,
                NULL as max_salary,
                NULL as levelI_count,
                NULL as levelII_count,
                NULL as levelIII_count,
                NULL as levelIV_count,
                EMPLOYER_STATE as employer_state,
                NULL as std_employer_name_parent
            FROM state_data
            ORDER BY data_type, YEAR, career_category
            """
            
            df = con.execute(query).fetchdf()
            
            # Force cleanup
            gc.collect()
            
            return df
        except Exception as e:
            st.error(f"Error fetching comprehensive AI/ML data: {e}")
            return pd.DataFrame()

# ============================================================================
# MAIN PAGE CONTENT
# ============================================================================

st.title("🤖 AI/ML Engineers vs Software Developers")
st.markdown("**Comprehensive comparison of AI/ML Engineers and Traditional Software Developers in H-1B lottery petitions (2020-2024)**")

# Main page tooltip
st.info("💡 **Comprehensive Analysis**: This page provides detailed insights into the growth, salary trends, and distribution of AI/ML Engineers compared to traditional Software Developers in H-1B petitions.")

# Get data
df = get_comprehensive_ai_ml_data()

if df.empty:
    st.warning("⚠️ No data found. Please check the database connection.")
else:
    # Separate data by type
    main_data = df[df['data_type'] == 'main'].copy()
    employer_data = df[df['data_type'] == 'employer'].copy()
    state_data = df[df['data_type'] == 'state'].copy()
    
    # Overall Analysis 2020-2024
    st.header("📊 Overall Analysis (2020-2024)")
    
    # Calculate overall trends
    total_ai_ml = main_data[main_data['career_category'] == 'AI/ML Engineers']['petition_count'].sum()
    total_software = main_data[main_data['career_category'] == 'Software Developers']['petition_count'].sum()
    ai_ml_growth_rate = ((main_data[main_data['career_category'] == 'AI/ML Engineers'].groupby('YEAR')['petition_count'].sum().iloc[-1] - 
                          main_data[main_data['career_category'] == 'AI/ML Engineers'].groupby('YEAR')['petition_count'].sum().iloc[0]) / 
                          main_data[main_data['career_category'] == 'AI/ML Engineers'].groupby('YEAR')['petition_count'].sum().iloc[0] * 100)
    software_growth_rate = ((main_data[main_data['career_category'] == 'Software Developers'].groupby('YEAR')['petition_count'].sum().iloc[-1] - 
                            main_data[main_data['career_category'] == 'Software Developers'].groupby('YEAR')['petition_count'].sum().iloc[0]) / 
                            main_data[main_data['career_category'] == 'Software Developers'].groupby('YEAR')['petition_count'].sum().iloc[0] * 100)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total AI/ML Engineers", f"{total_ai_ml:,.0f}", f"{ai_ml_growth_rate:+.1f}% growth")
    with col2:
        st.metric("Total Software Developers", f"{total_software:,.0f}", f"{software_growth_rate:+.1f}% growth")
    with col3:
        st.metric("AI/ML Market Share", f"{(total_ai_ml/(total_ai_ml+total_software)*100):.1f}%")
    
    st.markdown("**🎯 Key Trends:** AI/ML Engineers show strong growth despite 2023 market correction. Software Developers remain dominant but AI/ML is gaining market share with higher salary premiums.")
    
    # Summary metrics
    st.header("�� Summary Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_ai_ml = main_data[main_data['career_category'] == 'AI/ML Engineers']['petition_count'].sum()
    total_software = main_data[main_data['career_category'] == 'Software Developers']['petition_count'].sum()
    avg_ai_ml_salary = main_data[main_data['career_category'] == 'AI/ML Engineers']['avg_salary'].mean()
    avg_software_salary = main_data[main_data['career_category'] == 'Software Developers']['avg_salary'].mean()
    
    with col1:
        st.metric("Total AI/ML Engineers", f"{total_ai_ml:,.0f}")
    with col2:
        st.metric("Total Software Developers", f"{total_software:,.0f}")
    with col3:
        st.metric("Avg AI/ML Salary", f"${avg_ai_ml_salary:,.0f}")
    with col4:
        st.metric("Avg Software Salary", f"${avg_software_salary:,.0f}")
    
    # Yearly trends
    st.header("📈 Yearly Trends")
    
    yearly_data = main_data.groupby(['YEAR', 'career_category'])['petition_count'].sum().reset_index()
    
    fig_trends = px.line(yearly_data, x='YEAR', y='petition_count', color='career_category',
                         title="Petition Count by Year (2020-2024)",
                         labels={'petition_count': 'Petitions', 'YEAR': 'Year'},
                         color_discrete_map={'AI/ML Engineers': '#FF6B6B', 'Software Developers': '#4ECDC4'})
    fig_trends.update_layout(height=500)
    st.plotly_chart(fig_trends, use_container_width=True)
    
    # Top employers for AI/ML Engineers
    st.header("🏢 Top Employers for AI/ML Engineers")
    
    ai_ml_employers = employer_data.set_index('std_employer_name_parent')['petition_count']
    
    fig_employers = px.bar(x=ai_ml_employers.values, y=ai_ml_employers.index, orientation='h',
                           title="Top 15 Employers Hiring AI/ML Engineers",
                           labels={'x': 'Petitions', 'y': 'Employer'},
                           color=ai_ml_employers.values, color_continuous_scale='viridis')
    fig_employers.update_layout(height=600)
    st.plotly_chart(fig_employers, use_container_width=True)
    
    # Top states for AI/ML Engineers
    st.header("🗺️ Top States for AI/ML Engineers")
    
    ai_ml_states = state_data.set_index('employer_state')['petition_count']
    
    fig_states = px.bar(x=ai_ml_states.values, y=ai_ml_states.index, orientation='h',
                        title="Top 15 States for AI/ML Engineers",
                        labels={'x': 'Petitions', 'y': 'State'},
                        color=ai_ml_states.values, color_continuous_scale='plasma')
    fig_states.update_layout(height=600)
    st.plotly_chart(fig_states, use_container_width=True)
    
    # Salary comparison
    st.header("💰 Salary Comparison")
    
    col1, col2 = st.columns(2)
    
    with col1:
        salary_data = main_data.groupby(['YEAR', 'career_category'])['avg_salary'].mean().reset_index()
        fig_salary = px.line(salary_data, x='YEAR', y='avg_salary', color='career_category',
                            title="Average Salary Growth by Year",
                            labels={'avg_salary': 'Average Salary ($)', 'YEAR': 'Year'},
                            color_discrete_map={'AI/ML Engineers': '#FF6B6B', 'Software Developers': '#4ECDC4'})
        fig_salary.update_layout(height=400)
        st.plotly_chart(fig_salary, use_container_width=True)
    
    with col2:
        # Salary growth rate comparison (better than bubble chart)
        salary_growth_data = []
        for category in ['AI/ML Engineers', 'Software Developers']:
            cat_data = salary_data[salary_data['career_category'] == category].sort_values('YEAR')
            for i in range(1, len(cat_data)):
                current = cat_data.iloc[i]['avg_salary']
                previous = cat_data.iloc[i-1]['avg_salary']
                growth_rate = ((current - previous) / previous * 100) if previous > 0 else 0
                salary_growth_data.append({
                    'YEAR': cat_data.iloc[i]['YEAR'],
                    'career_category': category,
                    'salary_growth_rate': growth_rate
                })
        
        if salary_growth_data:
            salary_growth_df = pd.DataFrame(salary_growth_data)
            fig_salary_growth = px.bar(salary_growth_df, x='YEAR', y='salary_growth_rate', color='career_category',
                                      title="Salary Growth Rate by Year (%)",
                                      labels={'salary_growth_rate': 'Salary Growth Rate (%)', 'YEAR': 'Year'},
                                      color_discrete_map={'AI/ML Engineers': '#FF6B6B', 'Software Developers': '#4ECDC4'})
            fig_salary_growth.update_layout(height=400)
            st.plotly_chart(fig_salary_growth, use_container_width=True)
    
    # Market share analysis
    st.header("📈 Market Share Analysis")
    
    market_share_data = main_data.groupby(['YEAR', 'career_category'])['petition_count'].sum().reset_index()
    market_share_data['total_petitions'] = market_share_data.groupby('YEAR')['petition_count'].transform('sum')
    market_share_data['market_share'] = (market_share_data['petition_count'] / market_share_data['total_petitions'] * 100)
    
    fig_market_share = px.line(market_share_data, x='YEAR', y='market_share', color='career_category',
                              title="Market Share Growth by Year (%)",
                              labels={'market_share': 'Market Share (%)', 'YEAR': 'Year'},
                              color_discrete_map={'AI/ML Engineers': '#FF6B6B', 'Software Developers': '#4ECDC4'})
    fig_market_share.update_layout(height=500)
    st.plotly_chart(fig_market_share, use_container_width=True)
    
    # 2023 Drop Analysis
    st.header("📉 2023 Drop Analysis")
    
    # Calculate the drop
    ai_ml_2022 = main_data[(main_data['career_category'] == 'AI/ML Engineers') & (main_data['YEAR'] == 2022)]['petition_count'].sum()
    ai_ml_2023 = main_data[(main_data['career_category'] == 'AI/ML Engineers') & (main_data['YEAR'] == 2023)]['petition_count'].sum()
    software_2022 = main_data[(main_data['career_category'] == 'Software Developers') & (main_data['YEAR'] == 2022)]['petition_count'].sum()
    software_2023 = main_data[(main_data['career_category'] == 'Software Developers') & (main_data['YEAR'] == 2023)]['petition_count'].sum()
    
    ai_ml_drop_pct = ((ai_ml_2022 - ai_ml_2023) / ai_ml_2022 * 100) if ai_ml_2022 > 0 else 0
    software_drop_pct = ((software_2022 - software_2023) / software_2022 * 100) if software_2022 > 0 else 0
    
    st.markdown(f"**📉 2023 Drop:** AI/ML Engineers dropped {ai_ml_drop_pct:.1f}% while Software Developers dropped {software_drop_pct:.1f}% due to H-1B cap reduction and tech layoffs.")
    
    # Wage level distribution - IMPROVED VISUALIZATION
    st.header("📊 Wage Level Distribution & Growth Trends")
    
    # Prepare wage level data for better visualization
    wage_data = []
    for _, row in main_data.iterrows():
        for level in ['I', 'II', 'III', 'IV']:
            count = row[f'level{level}_count']
            if count > 0:
                wage_data.append({
                    'YEAR': row['YEAR'],
                    'career_category': row['career_category'],
                    'wage_level': f'Level {level}',
                    'count': count,
                    'percentage': (count / row['petition_count'] * 100)
                })
    
    if wage_data:
        wage_df = pd.DataFrame(wage_data)
        
        # Create a more sophisticated wage level visualization with growth focus
        fig_wage = go.Figure()
        
        # Color scheme for wage levels
        level_colors = {
            'Level I': '#FF6B6B',      # Red for entry level
            'Level II': '#4ECDC4',      # Teal for mid level
            'Level III': '#45B7D1',     # Blue for senior
            'Level IV': '#96CEB4'       # Green for expert
        }
        
        for category in ['AI/ML Engineers', 'Software Developers']:
            for level in ['Level I', 'Level II', 'Level III', 'Level IV']:
                data = wage_df[(wage_df['career_category'] == category) & (wage_df['wage_level'] == level)]
                if not data.empty:
                    fig_wage.add_trace(go.Bar(
                        x=data['YEAR'],
                        y=data['percentage'],
                        name=f'{category} - {level}',
                        hovertemplate=f'{category} - {level}<br>%{{y:.1f}}%<br>Year: %{{x}}<extra></extra>',
                        marker_color=level_colors[level],
                        opacity=0.8 if category == 'AI/ML Engineers' else 0.6
                    ))
        
        fig_wage.update_layout(
            title="Wage Level Distribution Growth by Year (%)",
            xaxis_title="Year",
            yaxis_title="Percentage of Petitions (%)",
            barmode='group',  # Changed to group for better comparison
            height=600,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        st.plotly_chart(fig_wage, use_container_width=True)
        
        # Add wage level growth insights
        st.markdown("**📈 Wage Level Growth Insights:**")
        
        # Calculate growth trends for each wage level
        for level in ['Level I', 'Level II', 'Level III', 'Level IV']:
            ai_ml_level_data = wage_df[(wage_df['career_category'] == 'AI/ML Engineers') & (wage_df['wage_level'] == level)]
            software_level_data = wage_df[(wage_df['career_category'] == 'Software Developers') & (wage_df['wage_level'] == level)]
            
            if not ai_ml_level_data.empty and not software_level_data.empty:
                ai_ml_trend = ai_ml_level_data['percentage'].iloc[-1] - ai_ml_level_data['percentage'].iloc[0]
                software_trend = software_level_data['percentage'].iloc[-1] - software_level_data['percentage'].iloc[0]
                
                st.markdown(f"- **{level}**: AI/ML trend {ai_ml_trend:+.1f}%, Software trend {software_trend:+.1f}%")
    
    # Growth rate analysis - IMPROVED VISUALIZATION
    st.header("🚀 Growth Rate Analysis & Trends")
    
    # Calculate year-over-year growth with better metrics
    growth_data = []
    for category in ['AI/ML Engineers', 'Software Developers']:
        cat_data = yearly_data[yearly_data['career_category'] == category].sort_values('YEAR')
        for i in range(1, len(cat_data)):
            current = cat_data.iloc[i]['petition_count']
            previous = cat_data.iloc[i-1]['petition_count']
            growth_rate = ((current - previous) / previous * 100) if previous > 0 else 0
            growth_data.append({
                'YEAR': cat_data.iloc[i]['YEAR'],
                'career_category': category,
                'growth_rate': growth_rate,
                'current_count': current,
                'previous_count': previous
            })
    
    if growth_data:
        growth_df = pd.DataFrame(growth_data)
        
        # Create a more sophisticated growth visualization
        fig_growth = go.Figure()
        
        for category in ['AI/ML Engineers', 'Software Developers']:
            data = growth_df[growth_df['career_category'] == category]
            if not data.empty:
                # Add bars for growth rate
                fig_growth.add_trace(go.Bar(
                    x=data['YEAR'],
                    y=data['growth_rate'],
                    name=f'{category} Growth Rate',
                    hovertemplate=f'{category}<br>Growth: %{{y:.1f}}%<br>Year: %{{x}}<extra></extra>',
                    marker_color='#FF6B6B' if category == 'AI/ML Engineers' else '#4ECDC4'
                ))
        
        # Add a horizontal line at 0% for reference
        fig_growth.add_hline(y=0, line_dash="dash", line_color="gray", annotation_text="No Growth")
        
        fig_growth.update_layout(
            title="Year-over-Year Growth Rate Trends (%)",
            xaxis_title="Year",
            yaxis_title="Growth Rate (%)",
            height=500,
            showlegend=True,
            hovermode='x unified'
        )
        st.plotly_chart(fig_growth, use_container_width=True)
        
        # Add comprehensive growth insights
        st.markdown("**📈 Growth Trend Analysis:**")
        for category in ['AI/ML Engineers', 'Software Developers']:
            cat_growth = growth_df[growth_df['career_category'] == category]
            if not cat_growth.empty:
                avg_growth = cat_growth['growth_rate'].mean()
                max_growth = cat_growth['growth_rate'].max()
                min_growth = cat_growth['growth_rate'].min()
                positive_years = len(cat_growth[cat_growth['growth_rate'] > 0])
                total_years = len(cat_growth)
                
                st.markdown(f"""
                **{category}:**
                - Average growth: {avg_growth:.1f}%
                - Growth range: {min_growth:.1f}% to {max_growth:.1f}%
                - Positive growth years: {positive_years}/{total_years}
                - 2023 impact: {cat_growth[cat_growth['YEAR'] == 2023]['growth_rate'].iloc[0] if not cat_growth[cat_growth['YEAR'] == 2023].empty else 'N/A'}%
                """)
    
    # Detailed yearly comparison table
    st.header("📋 Detailed Yearly Comparison")
    
    comparison_data = []
    for _, row in main_data.groupby(['YEAR', 'career_category']).agg({
        'petition_count': 'sum',
        'avg_salary': 'mean',
        'min_salary': 'min',
        'max_salary': 'max',
        'levelI_count': 'sum',
        'levelII_count': 'sum',
        'levelIII_count': 'sum',
        'levelIV_count': 'sum'
    }).reset_index().iterrows():
        comparison_data.append({
            'Year': row['YEAR'],
            'Category': row['career_category'],
            'Petitions': f"{row['petition_count']:,}",
            'Avg Salary': f"${row['avg_salary']:,.0f}",
            'Min Salary': f"${row['min_salary']:,.0f}",
            'Max Salary': f"${row['max_salary']:,.0f}",
            'Level I': row['levelI_count'],
            'Level II': row['levelII_count'],
            'Level III': row['levelIII_count'],
            'Level IV': row['levelIV_count']
        })
    
    comparison_df = pd.DataFrame(comparison_data)
    st.dataframe(comparison_df, use_container_width=True)
    
    # Key insights
    st.header("🔍 Key Insights")
    
    # Calculate insights
    ai_ml_growth = main_data[main_data['career_category'] == 'AI/ML Engineers']['petition_count'].sum()
    software_growth = main_data[main_data['career_category'] == 'Software Developers']['petition_count'].sum()
    
    ai_ml_avg_salary = main_data[main_data['career_category'] == 'AI/ML Engineers']['avg_salary'].mean()
    software_avg_salary = main_data[main_data['career_category'] == 'Software Developers']['avg_salary'].mean()
    
    salary_diff = ai_ml_avg_salary - software_avg_salary
    salary_diff_pct = (salary_diff / software_avg_salary * 100) if software_avg_salary > 0 else 0
    
    # Calculate growth rates
    ai_ml_yearly = main_data[main_data['career_category'] == 'AI/ML Engineers'].groupby('YEAR')['petition_count'].sum()
    software_yearly = main_data[main_data['career_category'] == 'Software Developers'].groupby('YEAR')['petition_count'].sum()
    
    ai_ml_growth_rate = ((ai_ml_yearly.iloc[-1] - ai_ml_yearly.iloc[0]) / ai_ml_yearly.iloc[0] * 100) if len(ai_ml_yearly) > 1 else 0
    software_growth_rate = ((software_yearly.iloc[-1] - software_yearly.iloc[0]) / software_yearly.iloc[0] * 100) if len(software_yearly) > 1 else 0
    
    st.markdown(f"""
    **📈 Growth Insights:**
    - **AI/ML Engineers**: {ai_ml_growth:,} total petitions ({ai_ml_growth_rate:+.1f}% growth)
    - **Software Developers**: {software_growth:,} total petitions ({software_growth_rate:+.1f}% growth)
    - **Ratio**: {ai_ml_growth/software_growth:.1f} AI/ML Engineers per Software Developer
    
    **💰 Salary Insights:**
    - **AI/ML Engineers Average**: ${ai_ml_avg_salary:,.0f}
    - **Software Developers Average**: ${software_avg_salary:,.0f}
    - **Salary Difference**: ${salary_diff:,.0f} ({salary_diff_pct:+.1f}%)
    
    **🏢 Top Employers for AI/ML:**
    - {ai_ml_employers.index[0]}: {ai_ml_employers.iloc[0]:,} petitions
    - {ai_ml_employers.index[1]}: {ai_ml_employers.iloc[1]:,} petitions
    - {ai_ml_employers.index[2]}: {ai_ml_employers.iloc[2]:,} petitions
    
    **🗺️ Top States for AI/ML:**
    - {ai_ml_states.index[0]}: {ai_ml_states.iloc[0]:,} petitions
    - {ai_ml_states.index[1]}: {ai_ml_states.iloc[1]:,} petitions
    - {ai_ml_states.index[2]}: {ai_ml_states.iloc[2]:,} petitions
    
    **🎯 Key Findings:**
    - AI/ML Engineers represent a growing segment in H-1B petitions
    - Salary premiums for AI/ML roles reflect specialized skills
    - Both categories show strong demand in the tech industry
    - AI/ML Engineers are concentrated in major tech hubs
    - Market share analysis shows the relative growth of AI/ML vs traditional software development
    """) 