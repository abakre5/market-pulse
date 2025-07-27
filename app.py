import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
import numpy as np
import plotly.graph_objects as go
import time
import gc

# Try to import psutil for memory monitoring
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    st.warning("psutil not available - memory monitoring disabled")

# Memory optimization
def optimize_memory():
    """Optimize memory usage for heavy data processing"""
    try:
        # Force garbage collection
        gc.collect()
        
        # Get memory info if psutil is available
        if PSUTIL_AVAILABLE:
            memory = psutil.virtual_memory()
            st.session_state['memory_available'] = memory.available / (1024**3)  # GB
        else:
            st.session_state['memory_available'] = None
        
        # Set pandas memory optimization
        pd.options.mode.chained_assignment = None
        
        # Set numpy to use less memory
        np.set_printoptions(precision=3, suppress=True)
        
        return True
    except Exception as e:
        st.warning(f"Memory optimization failed: {e}")
        return False

# Set page config at the very beginning
st.set_page_config(page_title="H-1B Company-Level Explorer", layout="wide")

# Initialize memory optimization
if 'memory_optimized' not in st.session_state:
    st.session_state['memory_optimized'] = optimize_memory()

DB_FILE = 'job_market_std_employer.duckdb'  # Users need to create this database
TABLE = 'job_market_data_aggressive_normalized'

from database_connection import get_db_connection

def get_filter_options():
    try:
        con = get_db_connection()
        if con is None:
            return [], [], [], []
        
        # Load only necessary data - no limits
        companies = con.execute(f"SELECT DISTINCT STD_EMPLOYER_NAME_PARENT FROM {TABLE} WHERE VISA_CLASS = 'H-1B' AND is_lottery_petition = TRUE AND STD_EMPLOYER_NAME_PARENT != '' ORDER BY STD_EMPLOYER_NAME_PARENT").fetchdf()['STD_EMPLOYER_NAME_PARENT'].tolist()
        years = con.execute(f"SELECT DISTINCT YEAR FROM {TABLE} WHERE VISA_CLASS = 'H-1B' AND is_lottery_petition = TRUE ORDER BY YEAR").fetchdf()['YEAR'].tolist()
        states = con.execute(f"SELECT DISTINCT EMPLOYER_STATE FROM {TABLE} WHERE VISA_CLASS = 'H-1B' AND is_lottery_petition = TRUE AND EMPLOYER_STATE IS NOT NULL ORDER BY EMPLOYER_STATE").fetchdf()['EMPLOYER_STATE'].tolist()
        soc_titles = con.execute(f"SELECT DISTINCT aggressive_normalized_soc_title FROM {TABLE} WHERE VISA_CLASS = 'H-1B' AND is_lottery_petition = TRUE AND aggressive_normalized_soc_title IS NOT NULL ORDER BY aggressive_normalized_soc_title").fetchdf()['aggressive_normalized_soc_title'].tolist()
        # Force cleanup after loading filter options
        gc.collect()
        
        return companies, years, states, soc_titles
    except Exception as e:
        st.error(f"Failed to load filter options: {e}")
        return [], [], [], []

def get_cities(state, company, year, soc_title):
    with st.spinner("Loading cities..."):
        try:
            con = get_db_connection()
            query = f"SELECT DISTINCT EMPLOYER_CITY FROM {TABLE} WHERE VISA_CLASS = 'H-1B' AND is_lottery_petition = TRUE AND EMPLOYER_CITY IS NOT NULL"
            params = []
            if state and state != 'All':
                query += " AND EMPLOYER_STATE = ?"
                params.append(state)
            if company and company != 'All':
                query += " AND STD_EMPLOYER_NAME_PARENT = ?"
                params.append(company)
            if year:
                query += " AND YEAR = ?"
                params.append(year)
            if soc_title and soc_title != 'All':
                query += " AND aggressive_normalized_soc_title = ?"
                params.append(soc_title)
            query += " ORDER BY EMPLOYER_CITY"
            cities = con.execute(query, params).fetchdf()['EMPLOYER_CITY'].tolist()
            
            # Cleanup after loading cities
            gc.collect()
            
            return cities
        except Exception as e:
            st.error(f"Failed to load cities: {e}")
            return []

def get_all_cities():
    """Get all cities independently"""
    with st.spinner("Loading all cities..."):
        try:
            con = get_db_connection()
            query = f"SELECT DISTINCT EMPLOYER_CITY FROM {TABLE} WHERE VISA_CLASS = 'H-1B' AND is_lottery_petition = TRUE AND EMPLOYER_CITY IS NOT NULL ORDER BY EMPLOYER_CITY"
            cities = con.execute(query).fetchdf()['EMPLOYER_CITY'].tolist()
            
            # Cleanup after loading all cities
            gc.collect()
            
            return cities
        except Exception as e:
            st.error(f"Failed to load all cities: {e}")
            return []

def get_all_companies():
    """Get all companies independently"""
    with st.spinner("Loading all companies..."):
        try:
            con = get_db_connection()
            query = f"SELECT DISTINCT STD_EMPLOYER_NAME_PARENT FROM {TABLE} WHERE VISA_CLASS = 'H-1B' AND is_lottery_petition = TRUE AND STD_EMPLOYER_NAME_PARENT IS NOT NULL ORDER BY STD_EMPLOYER_NAME_PARENT"
            companies = con.execute(query).fetchdf()['STD_EMPLOYER_NAME_PARENT'].tolist()
            
            # Cleanup after loading all companies
            gc.collect()
            
            return companies
        except Exception as e:
            st.error(f"Failed to load all companies: {e}")
            return []

def get_all_years():
    """Get all years independently"""
    with st.spinner("Loading all years..."):
        try:
            con = get_db_connection()
            query = f"SELECT DISTINCT YEAR FROM {TABLE} WHERE VISA_CLASS = 'H-1B' AND is_lottery_petition = TRUE ORDER BY YEAR"
            years = con.execute(query).fetchdf()['YEAR'].tolist()
            
            # Cleanup after loading all years
            gc.collect()
            
            return years
        except Exception as e:
            st.error(f"Failed to load all years: {e}")
            return []

def get_all_states():
    """Get all states independently"""
    with st.spinner("Loading all states..."):
        try:
            con = get_db_connection()
            query = f"SELECT DISTINCT EMPLOYER_STATE FROM {TABLE} WHERE VISA_CLASS = 'H-1B' AND is_lottery_petition = TRUE AND EMPLOYER_STATE IS NOT NULL ORDER BY EMPLOYER_STATE"
            states = con.execute(query).fetchdf()['EMPLOYER_STATE'].tolist()
            
            # Cleanup after loading all states
            gc.collect()
            
            return states
        except Exception as e:
            st.error(f"Failed to load all states: {e}")
            return []

def get_all_soc_titles():
    """Get all SOC titles independently"""
    with st.spinner("Loading all SOC titles..."):
        try:
            con = get_db_connection()
            query = f"SELECT DISTINCT aggressive_normalized_soc_title FROM {TABLE} WHERE VISA_CLASS = 'H-1B' AND is_lottery_petition = TRUE AND aggressive_normalized_soc_title IS NOT NULL ORDER BY aggressive_normalized_soc_title"
            soc_titles = con.execute(query).fetchdf()['aggressive_normalized_soc_title'].tolist()
            
            # Cleanup after loading all SOC titles
            gc.collect()
            
            return soc_titles
        except Exception as e:
            st.error(f"Failed to load all SOC titles: {e}")
            return []

def get_filtered_data(company, year, state, city, soc_title):
    with st.spinner("Loading filtered data..."):
        try:
            con = get_db_connection()
            query = f"SELECT * FROM {TABLE} WHERE VISA_CLASS = 'H-1B' AND is_lottery_petition = TRUE"
            params = []
            if company and company != 'All':
                query += " AND STD_EMPLOYER_NAME_PARENT = ?"
                params.append(company)
            if year:
                query += " AND YEAR = ?"
                params.append(year)
            if state and state != 'All':
                query += " AND EMPLOYER_STATE = ?"
                params.append(state)
            if city and city != 'All':
                query += " AND EMPLOYER_CITY = ?"
                params.append(city)
            if soc_title and soc_title != 'All':
                query += " AND aggressive_normalized_soc_title = ?"
                params.append(soc_title)
            df = con.execute(query, params).fetchdf()
            
            # Cleanup resources after data loading
            gc.collect()
            
            return df
        except Exception as e:
            st.error(f"Failed to load filtered data: {e}")
            return pd.DataFrame()

def get_company_state_data(company, year, soc_title, job_title):
    """Get company data by state for map visualization - respects Company, Year, SOC Title, and Job Title filters only"""
    with st.spinner("Loading company state data..."):
        try:
            con = get_db_connection()
            
            # Build query based on filters - Company, Year, SOC Title, Job Title (not State/City)
            query = f"""
            SELECT 
                EMPLOYER_STATE as state,
                COUNT(*) as petition_count,
                AVG(PREVAILING_WAGE) as avg_salary,
                COUNT(CASE WHEN PW_WAGE_LEVEL = 'I' THEN 1 END) as level1_count,
                COUNT(CASE WHEN PW_WAGE_LEVEL = 'II' THEN 1 END) as level2_count,
                COUNT(CASE WHEN PW_WAGE_LEVEL = 'III' THEN 1 END) as level3_count,
                COUNT(CASE WHEN PW_WAGE_LEVEL = 'IV' THEN 1 END) as level4_count
            FROM {TABLE} 
            WHERE VISA_CLASS = 'H-1B' AND is_lottery_petition = TRUE 
            AND EMPLOYER_STATE IS NOT NULL
            """
            params = []
            
            # Filter by Company, Year, SOC Title, and Job Title (ignore State and City filters)
            if company and company != 'All':
                query += " AND STD_EMPLOYER_NAME_PARENT = ?"
                params.append(company)
            
            if year:
                query += " AND YEAR = ?"
                params.append(int(year))  # Convert to int
            
            if soc_title and soc_title != 'All':
                query += " AND aggressive_normalized_soc_title = ?"
                params.append(soc_title)
            
            if job_title and job_title != 'All':
                query += " AND NORMALIZED_JOB_TITLE = ?"
                params.append(job_title)
            
            query += " GROUP BY EMPLOYER_STATE ORDER BY petition_count DESC"
            
            df = con.execute(query, params).fetchdf()
            
            # Calculate percentages
            if not df.empty:
                total_petitions = df['petition_count'].sum()
                df['percentage'] = (df['petition_count'] / total_petitions * 100).round(1)
                df['avg_salary'] = df['avg_salary'].round(0)
            
            return df
        except Exception as e:
            st.error(f"Failed to load company state data: {e}")
            return pd.DataFrame()

def get_job_titles(company, soc_title, state, city, year):
    with st.spinner("Loading job titles..."):
        try:
            con = get_db_connection()
            query = f"SELECT DISTINCT NORMALIZED_JOB_TITLE FROM {TABLE} WHERE VISA_CLASS = 'H-1B' AND is_lottery_petition = TRUE AND NORMALIZED_JOB_TITLE IS NOT NULL"
            params = []
            if company and company != 'All':
                query += " AND STD_EMPLOYER_NAME_PARENT = ?"
                params.append(company)
            if soc_title and soc_title != 'All':
                query += " AND aggressive_normalized_soc_title = ?"
                params.append(soc_title)
            if state and state != 'All':
                query += " AND EMPLOYER_STATE = ?"
                params.append(state)
            if city and city != 'All':
                query += " AND EMPLOYER_CITY = ?"
                params.append(city)
            if year:
                query += " AND YEAR = ?"
                params.append(year)
            query += " ORDER BY NORMALIZED_JOB_TITLE"
            job_titles = con.execute(query, params).fetchdf()['NORMALIZED_JOB_TITLE'].drop_duplicates().tolist()
            return job_titles
        except Exception as e:
            st.error(f"Failed to load job titles: {e}")
            return []

def get_soc_titles(company, state, city, year):
    with st.spinner("Loading SOC titles..."):
        try:
            con = get_db_connection()
            query = f"SELECT DISTINCT aggressive_normalized_soc_title FROM {TABLE} WHERE VISA_CLASS = 'H-1B' AND is_lottery_petition = TRUE AND aggressive_normalized_soc_title IS NOT NULL"
            params = []
            if company and company != 'All':
                query += " AND STD_EMPLOYER_NAME_PARENT = ?"
                params.append(company)
            if state and state != 'All':
                query += " AND EMPLOYER_STATE = ?"
                params.append(state)
            if city and city != 'All':
                query += " AND EMPLOYER_CITY = ?"
                params.append(city)
            if year:
                query += " AND YEAR = ?"
                params.append(year)
            query += " ORDER BY aggressive_normalized_soc_title"
            soc_titles = con.execute(query, params).fetchdf()['aggressive_normalized_soc_title'].tolist()
            return soc_titles
        except Exception as e:
            st.error(f"Failed to load SOC titles: {e}")
            return []

def get_yearly_data(company, state, city, soc_title):
    """Get data for yearly analysis - shows all years 2020-2024 regardless of filters"""
    with st.spinner("Loading yearly analysis data..."):
        try:
            con = get_db_connection()
            
            # Get all years first
            all_years_query = f"SELECT DISTINCT YEAR FROM {TABLE} WHERE VISA_CLASS = 'H-1B' AND is_lottery_petition = TRUE ORDER BY YEAR"
            all_years = con.execute(all_years_query).fetchdf()['YEAR'].tolist()
            
            # Get filtered data for each year
            all_data = []
            for year in all_years:
                query = f"SELECT * FROM {TABLE} WHERE VISA_CLASS = 'H-1B' AND is_lottery_petition = TRUE AND YEAR = ?"
                params = [year]
                
                if company and company != 'All':
                    query += " AND STD_EMPLOYER_NAME_PARENT = ?"
                    params.append(company)
                if state and state != 'All':
                    query += " AND EMPLOYER_STATE = ?"
                    params.append(state)
                if city and city != 'All':
                    query += " AND EMPLOYER_CITY = ?"
                    params.append(city)
                if soc_title and soc_title != 'All':
                    query += " AND aggressive_normalized_soc_title = ?"
                    params.append(soc_title)
                
                year_data = con.execute(query, params).fetchdf()
                all_data.append(year_data)
            
            # Combine all years
            if all_data:
                df = pd.concat(all_data, ignore_index=True)
            else:
                df = pd.DataFrame()
            
            # Cleanup resources after data loading
            gc.collect()
            
            return df
        except Exception as e:
            st.error(f"Failed to load yearly data: {e}")
            return pd.DataFrame()

# Background rendering functions for each tab
def render_wage_distribution_tab(df, fig, config):
    """Render wage distribution tab content"""
    # Ensure config is not None
    if config is None:
        config = {}
    
    # Petitions by Wage Level table - FIRST
    st.subheader("Petitions by Wage Level")
    if not df.empty and len(df) > 0:
        try:
            wage_level_counts = df['PW_WAGE_LEVEL'].value_counts().reset_index()
            wage_level_counts.columns = ['Wage Level', 'Number of Petitions']
            wage_level_counts = wage_level_counts.sort_values('Wage Level')
            wage_level_counts['Percentage'] = (wage_level_counts['Number of Petitions'] / len(df) * 100).round(2)
            
            # Add total row
            total_row = pd.DataFrame({
                'Wage Level': ['Total'],
                'Number of Petitions': [len(df)],
                'Percentage': [100.0]
            })
            wage_level_counts = pd.concat([wage_level_counts, total_row], ignore_index=True)
            
            st.dataframe(wage_level_counts, use_container_width=True, hide_index=True)
        except Exception as e:
            st.warning(f"Could not display wage level table: {e}")
    else:
        st.warning("No data available for analysis.")
    
    # Wage Distribution graph - SECOND
    st.subheader("Wage Distribution by Wage Level (Each Point = Lottery LCA)")
    if fig is not None:
        st.plotly_chart(fig, use_container_width=True, config=config)
    else:
        st.warning("No data available for visualization.")

def render_top_occupations_tab(df):
    """Render top occupations tab content"""
    st.subheader("💰 Highest Paid Occupations by Wage Level")
    
    if not df.empty and len(df) > 0:
        try:
            # Get top 3 highest paid occupations for each wage level
            top_paid_occupations = {}
            for level in sorted(df['PW_WAGE_LEVEL'].unique()):
                level_data = df[df['PW_WAGE_LEVEL'] == level]
                # Group by occupation and calculate average salary
                occ_salary = level_data.groupby('aggressive_normalized_soc_title')['PREVAILING_WAGE'].agg(['mean', 'count']).reset_index()
                occ_salary = occ_salary[occ_salary['count'] >= 5]  # Only occupations with at least 5 petitions
                if not occ_salary.empty:
                    top_paid = occ_salary.nlargest(3, 'mean')
                    top_paid_occupations[f'Level {level}'] = top_paid
            
            # Create a comprehensive table
            if top_paid_occupations:
                occupation_df = pd.DataFrame()
                for level, occupations in top_paid_occupations.items():
                    temp_df = pd.DataFrame({
                        'Wage Level': level,
                        'Occupation': occupations['aggressive_normalized_soc_title'],
                        'Average Salary': occupations['mean'].round(0).astype(int),
                        'Number of Petitions': occupations['count']
                    })
                    occupation_df = pd.concat([occupation_df, temp_df], ignore_index=True)
                
                st.dataframe(occupation_df, use_container_width=True)
            else:
                st.warning("No occupations found with sufficient data (minimum 5 petitions per occupation).")
        except Exception as e:
            st.warning(f"Could not display top occupations: {e}")
    else:
        st.warning("No data available for analysis.")

def process_yearly_analysis_data(yearly_df):
    """Process yearly analysis data - cached function for expensive computations"""
    if yearly_df.empty or len(yearly_df) == 0:
        return None, None, None, None, None
    
    # Process wage level trends data
    yearly_wage_data = yearly_df.groupby(['YEAR', 'PW_WAGE_LEVEL']).size().reset_index(name='count')
    yearly_wage_pivot = yearly_wage_data.pivot(index='YEAR', columns='PW_WAGE_LEVEL', values='count').fillna(0)
    yearly_wage_pct = yearly_wage_pivot.div(yearly_wage_pivot.sum(axis=1), axis=0) * 100
    
    # Process salary trends data
    salary_trends = yearly_df.groupby(['YEAR', 'PW_WAGE_LEVEL'])['PREVAILING_WAGE'].agg(['mean', 'median', 'count']).reset_index()
    salary_trends.columns = ['Year', 'Wage Level', 'Average Salary', 'Median Salary', 'Count']
    
    # Process yearly statistics
    yearly_stats = yearly_df.groupby('YEAR').agg({
        'PW_WAGE_LEVEL': 'count',
        'PREVAILING_WAGE': ['mean', 'median', 'min', 'max']
    }).round(0)
    yearly_stats.columns = ['Total Petitions', 'Avg Salary', 'Median Salary', 'Min Salary', 'Max Salary']
    
    # Process policy impact data
    yearly_impact = []
    for year in sorted(yearly_df['YEAR'].unique()):
        year_data = yearly_df[yearly_df['YEAR'] == year]
        total = len(year_data)
        level1 = len(year_data[year_data['PW_WAGE_LEVEL'] == 'I'])
        level2 = len(year_data[year_data['PW_WAGE_LEVEL'] == 'II'])
        level3 = len(year_data[year_data['PW_WAGE_LEVEL'] == 'III'])
        level4 = len(year_data[year_data['PW_WAGE_LEVEL'] == 'IV'])
        
        yearly_impact.append({
            'Year': year,
            'Total Petitions': total,
            'Level I Count': level1,
            'Level I %': round(level1/total*100, 1),
            'Level II Count': level2,
            'Level II %': round(level2/total*100, 1),
            'Level III Count': level3,
            'Level III %': round(level3/total*100, 1),
            'Level IV Count': level4,
            'Level IV %': round(level4/total*100, 1),
            'At Risk (I+II)': level1 + level2,
            'At Risk %': round((level1 + level2)/total*100, 1)
        })
    
    # Process top occupations data
    yearly_occupations = {}
    for year in sorted(yearly_df['YEAR'].unique()):
        year_data = yearly_df[yearly_df['YEAR'] == year]
        for level in sorted(year_data['PW_WAGE_LEVEL'].unique()):
            level_data = year_data[year_data['PW_WAGE_LEVEL'] == level]
            if len(level_data) >= 10:  # Only if we have enough data
                top_occ = level_data['aggressive_normalized_soc_title'].value_counts().head(5)
                yearly_occupations[f'{year}_Level_{level}'] = {
                    'Year': year,
                    'Wage Level': level,
                    'Top Occupations': top_occ.to_dict()
                }
    
    return yearly_wage_pct, salary_trends, yearly_stats, yearly_impact, yearly_occupations

def render_yearly_analysis_tab(yearly_df, config):
    """Render yearly analysis tab content"""
    st.subheader("📈 Yearly Trends & Policy Impact Analysis")
    
    # Ensure config is not None
    if config is None:
        config = {}
    
    if not yearly_df.empty and len(yearly_df) > 0:
        # Process data using cached function
        yearly_wage_pct, salary_trends, yearly_stats, yearly_impact, yearly_occupations = process_yearly_analysis_data(yearly_df)
        
        if yearly_wage_pct is not None:
            # Use tabs to organize the yearly analysis and prevent overlapping
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "📊 Wage Level Trends", 
                "📈 Salary Trends", 
                "📋 Yearly Statistics", 
                "⚠️ Policy Impact", 
                "💼 Top Occupations"
            ])
            
            with tab1:
                st.markdown("**Wage Level Distribution Trends (2020-2024)**")
                
                fig_yearly_trend = go.Figure()
                # Professional color mapping for wage levels
                level_colors = {
                    'I': COLORS['warning'],      # Red for Level I (entry level)
                    'II': COLORS['secondary'],   # Orange for Level II
                    'III': COLORS['primary'],    # Blue for Level III
                    'IV': COLORS['success']      # Green for Level IV (senior)
                }
                
                for level in yearly_wage_pct.columns:
                    fig_yearly_trend.add_trace(go.Scatter(
                        x=yearly_wage_pct.index,
                        y=yearly_wage_pct[level],
                        mode='lines+markers',
                        name=f'Level {level}',
                        line=dict(width=3, color=level_colors.get(level, COLORS['info'])),
                        marker=dict(size=8, color=level_colors.get(level, COLORS['info']))
                    ))
                

                
                fig_yearly_trend.update_layout(
                    title="H-1B Lottery Petitions by Wage Level Over Time",
                    xaxis_title="Year",
                    yaxis_title="Percentage of Petitions (%)",
                    legend_title="Wage Level",
                    hovermode='x unified',
                    height=400
                )
                st.plotly_chart(fig_yearly_trend, use_container_width=True, config=config)
        
            with tab2:
                st.markdown("**Salary Trends by Wage Level (2020-2024)**")
                
                # Create salary trend chart
                fig_salary_trend = go.Figure()
                # Professional color mapping for wage levels
                level_colors = {
                    'I': COLORS['warning'],      # Red for Level I (entry level)
                    'II': COLORS['secondary'],   # Orange for Level II
                    'III': COLORS['primary'],    # Blue for Level III
                    'IV': COLORS['success']      # Green for Level IV (senior)
                }
                
                for level in sorted(yearly_df['PW_WAGE_LEVEL'].unique()):
                    level_data = salary_trends[salary_trends['Wage Level'] == level]
                    fig_salary_trend.add_trace(go.Scatter(
                        x=level_data['Year'],
                        y=level_data['Average Salary'],
                        mode='lines+markers',
                        name=f'Level {level} (Avg)',
                        line=dict(width=3, color=level_colors.get(level, COLORS['info'])),
                        marker=dict(size=8, color=level_colors.get(level, COLORS['info']))
                    ))
                

                
                fig_salary_trend.update_layout(
                    title="Average Salary Trends by Wage Level Over Time",
                    xaxis_title="Year",
                    yaxis_title="Average Salary ($)",
                    yaxis=dict(tickformat=",.0f"),
                    legend_title="Wage Level",
                    height=400
                )
                st.plotly_chart(fig_salary_trend, use_container_width=True, config=config)
            
            with tab3:
                st.markdown("**Yearly Summary Statistics**")
                st.dataframe(yearly_stats, use_container_width=True)
            
            with tab4:
                st.markdown("**Wage Level Impact Analysis by Year**")
                impact_df = pd.DataFrame(yearly_impact)
                st.dataframe(impact_df, use_container_width=True)
        
            with tab5:
                st.markdown("**Top Occupations by Year and Wage Level**")
                
                # Display in a more readable format
                for key, data in yearly_occupations.items():
                    st.markdown(f"**{data['Year']} - Level {data['Wage Level']}:**")
                    for occ, count in data['Top Occupations'].items():
                        st.markdown(f"- {occ}: {count:,} petitions")
                    st.markdown("---")
    else:
        st.warning("No data available for yearly analysis.")

def render_us_map_tab(company, year, soc_title, job_title):
    """Render US map visualization tab - respects Company, Year, SOC Title, and Job Title filters only"""
    st.subheader("🗺️ US Geographic Distribution")
    st.info("💡 **Note:** This map shows data across ALL states, respecting Company, Year, SOC Title, and Job Title filters (State and City filters are ignored for geographic visualization).")
    
    # Show active filters
    st.markdown("**Active Filters:**")
    filter_info = []
    if company and company != 'All':
        filter_info.append(f"Company: {company}")
    if year:
        filter_info.append(f"Year: {year}")
    if soc_title and soc_title != 'All':
        filter_info.append(f"SOC Title: {soc_title}")
    if job_title and job_title != 'All':
        filter_info.append(f"Job Title: {job_title}")
    
    if filter_info:
        st.write(" | ".join(filter_info))
    else:
        st.write("No filters applied - showing all data")
    
    # Get company state data
    state_data = get_company_state_data(company, year, soc_title, job_title)
    
    if state_data.empty:
        st.warning("No geographic data available for the selected filters.")
        return
    
    # Create tabs for different map views
    map_tab1, map_tab2, map_tab3 = st.tabs([
        "📊 Petition Count by State", 
        "💰 Average Salary by State", 
        "📈 Wage Level Distribution"
    ])
    
    with map_tab1:
        st.markdown("**H-1B Lottery Petitions by State**")
        
        # Create choropleth map for petition count
        fig_map = px.choropleth(
            state_data,
            locations='state',
            locationmode='USA-states',
            color='petition_count',
            hover_name='state',
            hover_data={
                'state': False,
                'petition_count': True,
                'percentage': True,
                'avg_salary': True
            },
            color_continuous_scale='Blues',
            title=f"H-1B Lottery Petitions by State{f' - {company}' if company != 'All' else ''}{f' ({year})' if year else ''}",
            labels={'petition_count': 'Petitions', 'percentage': '% of Total', 'avg_salary': 'Avg Salary'}
        )
        
        # Apply styling
        fig_map.update_layout(
            geo=dict(
                bgcolor='white',
                landcolor='#f8f9fa',
                coastlinecolor=COLORS['border'],
                showland=True,
                showcoastlines=True,
                projection_type='albers usa'
            )
        )
        
        fig_map.update_layout(height=500)
        st.plotly_chart(fig_map, use_container_width=True)
        
        # Show top states table
        st.markdown("**Top 10 States by Petition Count**")
        top_states = state_data.head(10)[['state', 'petition_count', 'percentage', 'avg_salary']]
        top_states.columns = ['State', 'Petitions', '% of Total', 'Avg Salary']
        st.dataframe(top_states, use_container_width=True)
    
    with map_tab2:
        st.markdown("**Average Salary by State**")
        
        # Create choropleth map for average salary
        fig_salary_map = px.choropleth(
            state_data,
            locations='state',
            locationmode='USA-states',
            color='avg_salary',
            hover_name='state',
            hover_data={
                'state': False,
                'avg_salary': True,
                'petition_count': True,
                'percentage': True
            },
            color_continuous_scale='Greens',
            title=f"Average Salary by State{f' - {company}' if company != 'All' else ''}{f' ({year})' if year else ''}",
            labels={'avg_salary': 'Avg Salary ($)', 'petition_count': 'Petitions', 'percentage': '% of Total'}
        )
        
        # Apply styling
        fig_salary_map.update_layout(
            geo=dict(
                bgcolor='white',
                landcolor='#f8f9fa',
                coastlinecolor=COLORS['border'],
                showland=True,
                showcoastlines=True,
                projection_type='albers usa'
            )
        )
        
        fig_salary_map.update_layout(height=500)
        st.plotly_chart(fig_salary_map, use_container_width=True)
        
        # Show salary statistics
        st.markdown("**Salary Statistics by State**")
        salary_stats = state_data[['state', 'avg_salary', 'petition_count']].sort_values('avg_salary', ascending=False)
        salary_stats.columns = ['State', 'Avg Salary ($)', 'Petitions']
        st.dataframe(salary_stats, use_container_width=True)
    
    with map_tab3:
        st.markdown("**Wage Level Distribution by State**")
        
        # Create stacked bar chart for wage levels by state
        wage_level_data = []
        for _, row in state_data.iterrows():
            wage_level_data.extend([
                {'state': row['state'], 'wage_level': 'Level I', 'count': row['level1_count']},
                {'state': row['state'], 'wage_level': 'Level II', 'count': row['level2_count']},
                {'state': row['state'], 'wage_level': 'Level III', 'count': row['level3_count']},
                {'state': row['state'], 'wage_level': 'Level IV', 'count': row['level4_count']}
            ])
        
        wage_df = pd.DataFrame(wage_level_data)
        wage_df = wage_df[wage_df['count'] > 0]  # Remove zero counts
        
        if not wage_df.empty:
            # Professional color mapping for wage levels
            level_colors = {
                'Level I': COLORS['warning'],      # Red for Level I
                'Level II': COLORS['secondary'],   # Orange for Level II
                'Level III': COLORS['primary'],    # Blue for Level III
                'Level IV': COLORS['success']      # Green for Level IV
            }
            
            fig_wage_dist = px.bar(
                wage_df,
                x='state',
                y='count',
                color='wage_level',
                color_discrete_map=level_colors,
                title=f"Wage Level Distribution by State{f' - {company}' if company != 'All' else ''}{f' ({year})' if year else ''}",
                labels={'count': 'Number of Petitions', 'state': 'State', 'wage_level': 'Wage Level'}
            )
            

            
            fig_wage_dist.update_layout(height=500, xaxis_tickangle=-45)
            st.plotly_chart(fig_wage_dist, use_container_width=True)
            
            # Show wage level summary
            st.markdown("**Wage Level Summary by State**")
            wage_summary = state_data[['state', 'level1_count', 'level2_count', 'level3_count', 'level4_count', 'petition_count']].copy()
            wage_summary['Level I %'] = (wage_summary['level1_count'] / wage_summary['petition_count'] * 100).round(1)
            wage_summary['Level II %'] = (wage_summary['level2_count'] / wage_summary['petition_count'] * 100).round(1)
            wage_summary['Level III %'] = (wage_summary['level3_count'] / wage_summary['petition_count'] * 100).round(1)
            wage_summary['Level IV %'] = (wage_summary['level4_count'] / wage_summary['petition_count'] * 100).round(1)
            
            wage_summary = wage_summary[['state', 'petition_count', 'Level I %', 'Level II %', 'Level III %', 'Level IV %']]
            wage_summary.columns = ['State', 'Total Petitions', 'Level I %', 'Level II %', 'Level III %', 'Level IV %']
            st.dataframe(wage_summary, use_container_width=True)
        else:
            st.warning("No wage level data available for the selected filters.")

def render_policy_summary_tab(df):
    """Render policy summary tab content"""
    st.subheader("📋 Policy Impact Summary")
    
    # Check if we have data
    if df.empty:
        st.warning("No data available for policy analysis.")
        return
    
    # Calculate what the new policy would mean
    total_petitions = len(df)
    level1_petitions = len(df[df['PW_WAGE_LEVEL'] == 'I'])
    level2_petitions = len(df[df['PW_WAGE_LEVEL'] == 'II'])
    level3_petitions = len(df[df['PW_WAGE_LEVEL'] == 'III'])
    level4_petitions = len(df[df['PW_WAGE_LEVEL'] == 'IV'])
    
    # Calculate percentages safely
    level1_pct = (level1_petitions/total_petitions*100) if total_petitions > 0 else 0
    level2_pct = (level2_petitions/total_petitions*100) if total_petitions > 0 else 0
    level3_pct = (level3_petitions/total_petitions*100) if total_petitions > 0 else 0
    level4_pct = (level4_petitions/total_petitions*100) if total_petitions > 0 else 0
    
    st.markdown(f"""
    **Current H-1B Lottery System (Random Selection):**
    - Total Lottery Petitions: {total_petitions:,}
    - Level I (Entry-level): {level1_petitions:,} ({level1_pct:.1f}%)
    - Level II (Mid-level): {level2_petitions:,} ({level2_pct:.1f}%)
    - Level III (Senior): {level3_petitions:,} ({level3_pct:.1f}%)
    - Level IV (Expert): {level4_petitions:,} ({level4_pct:.1f}%)
    
    **Potential Impact of Wage-Based Selection:**
    - Level I petitions would likely be **eliminated** or severely reduced
    - Level II petitions would face **significant reduction**
    - Level III and IV petitions would become **dominant**
    - **International students** (typically Level I/II) would be **disproportionately affected**
    """)
    
    # Only show min wage table if we have data
    if total_petitions > 0:
        st.subheader("Min Wage by Wage Level (with Example LCA)")
        try:
            min_lca = df.loc[df.groupby("PW_WAGE_LEVEL")['PREVAILING_WAGE'].idxmin()]
            st.dataframe(min_lca[["PW_WAGE_LEVEL", "PREVAILING_WAGE", "CASE_NUMBER", "EMPLOYER_NAME", "JOB_TITLE", "EMPLOYER_CITY", "EMPLOYER_STATE"]], use_container_width=True)
        except Exception as e:
            st.warning(f"Could not display min wage table: {e}")
    else:
        st.warning("No data available for min wage analysis.")

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
</style>
""", unsafe_allow_html=True)

st.title("🏢 H-1B Company-Level Explorer")
st.markdown("**Company-specific analysis tool for H-1B lottery petition data - dive deep into individual company hiring patterns, wage distributions, and policy impacts**")

# Sidebar filters
st.sidebar.header("Filters")


# Independent filters (not cascading)
# Company filter with priority list for Indian journalists
with st.spinner("Loading companies..."):
    companies = get_all_companies()
    years = get_all_years()
    states = get_all_states()

# Priority companies for Indian journalists (high H-1B volumes, frequently in news)
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

# Create the company options with priority list at top (company-level analysis only)
company_options = priority_companies + ["--- Other Companies ---"] + available_companies

# Find default index for Amazon (most popular)
try:
    amazon_index = company_options.index("AMAZON") if "AMAZON" in company_options else 0
except ValueError:
    amazon_index = 0

# Set default selections with safe indexing
state_default = 0  # "All" is at index 0

def_year = 0
try:
    if years and 2024 in years:
        def_year = [str(y) for y in years].index('2024')  # Default to 2024
except (ValueError, IndexError):
    def_year = 0

company = st.sidebar.selectbox("🏢 Company", company_options, index=amazon_index, help="Select a specific company for detailed analysis")

year = st.sidebar.selectbox("📅 Year", [str(y) for y in years], index=def_year, help="Select a specific year or 'All' for all years")
state = st.sidebar.selectbox("🗺️ State", ["All"] + states, index=state_default, help="Select a specific state or 'All' for all states")

# Cascading filters: City depends on State, SOC Title and Job Title are independent
with st.spinner("Loading cities..."):
    cities = get_cities(state, company, year, None)
city = st.sidebar.selectbox("🏙️ City", ["All"] + cities, help="Select a specific city or 'All' for all cities")

# Independent SOC Title filter
with st.spinner("Loading SOC titles..."):
    soc_titles = get_all_soc_titles()
soc_title_default = 0
try:
    if soc_titles:
        for i, t in enumerate(soc_titles):
            if t and t.lower().startswith('software developers'):
                soc_title_default = i + 1  # +1 because "All" is at index 0
                break
except (ValueError, IndexError):
    soc_title_default = 0

soc_title = st.sidebar.selectbox("💼 Job Category", ["All"] + soc_titles, index=soc_title_default, help="Select a specific job category or 'All' for all categories")

# Cascading Job Title filter (depends on SOC Title)
with st.spinner("Loading job titles..."):
    job_titles = get_job_titles(company, soc_title, state, city, year)
job_title = st.sidebar.selectbox("👨‍💻 Job Title", ["All"] + job_titles, help="Select a specific job title or 'All' for all titles")

# Store the job_title value to ensure it's not affected by caching
current_job_title = job_title

# Main panel: filtered data
with st.spinner("Loading data..."):
    start_time = time.time()
    df = get_filtered_data(company, year, state, city, soc_title)
    if job_title and job_title != 'All':
        df = df[df['NORMALIZED_JOB_TITLE'] == job_title]
    load_time = time.time() - start_time

# Stats
st.header("Summary Stats")
st.metric("Total Lottery Petitions", f"{len(df):,}")

# Initialize fig and config variables
fig = None
config = {}

# Handle empty data gracefully
if df.empty or len(df) == 0:
    st.warning("⚠️ No data found for the selected filters. Please try different filter combinations.")
    st.info("💡 Tip: Try selecting 'All' for some filters to see more data.")
else:
    try:
        # Safe calculations with null checks
        avg_wage = df['PREVAILING_WAGE'].mean() if not df['PREVAILING_WAGE'].isna().all() else 0
        min_wage = df['PREVAILING_WAGE'].min() if not df['PREVAILING_WAGE'].isna().all() else 0
        max_wage = df['PREVAILING_WAGE'].max() if not df['PREVAILING_WAGE'].isna().all() else 0
        
        st.metric("Avg Wage", f"${avg_wage:,.0f}")
        st.metric("Min Wage", f"${min_wage:,.0f}")
        st.metric("Max Wage", f"${max_wage:,.0f}")
    except Exception as e:
        st.error(f"Error calculating wage statistics: {e}")
        st.metric("Avg Wage", "$0")
        st.metric("Min Wage", "$0")
        st.metric("Max Wage", "$0")
    
    # Wage distribution graph - moved to tabs to prevent overlapping
    import plotly.graph_objects as go
    import numpy as np
    
    # Use all data - no sampling
    df_plot = df.copy()
    
    # Safe data processing with error handling
    try:
        # Ensure required columns exist
        if 'PW_WAGE_LEVEL' not in df_plot.columns or 'PREVAILING_WAGE' not in df_plot.columns:
            st.error("Required columns 'PW_WAGE_LEVEL' or 'PREVAILING_WAGE' not found in data")
            fig = None
            config = {}
        else:
            # Remove rows with null values
            df_plot = df_plot.dropna(subset=['PW_WAGE_LEVEL', 'PREVAILING_WAGE'])
            
            if df_plot.empty:
                st.warning("No valid data available for visualization after removing null values")
                fig = None
                config = {}
            else:
                # Optimize data processing for large datasets
                wage_levels = df_plot['PW_WAGE_LEVEL'].astype('category')
                x_jitter = wage_levels.cat.codes + np.random.uniform(-0.2, 0.2, size=len(df_plot))
                df_plot['x_jitter'] = x_jitter
                
                # Create visualization if we have valid data
                if len(df_plot) > 0:
                    # Use professional color scheme
                    color_map = [COLORS['primary'], COLORS['secondary'], COLORS['success'], COLORS['warning'], 
                                COLORS['info'], '#8c564b', '#e377c2', '#bcbd22']
                    
                    # Create color mapping
                    color_discrete_map = {lvl: color_map[i % len(color_map)] for i, lvl in enumerate(wage_levels.cat.categories)}
                    colors = [color_discrete_map.get(lvl, color_map[0]) for lvl in df_plot['PW_WAGE_LEVEL']]
                    
                    # Generate hover text
                    if len(df_plot) > 10000:
                        hover_texts = [f"${wage:,.0f}" for wage in df_plot['PREVAILING_WAGE']]
                    else:
                        hover_texts = []
                        for _, row in df_plot.iterrows():
                            try:
                                wage = row.get('PREVAILING_WAGE', 0)
                                job_title = row.get('NORMALIZED_JOB_TITLE', 'Unknown')
                                hover_texts.append(f"Salary: ${wage:,.0f}<br>Job Title: {job_title}")
                            except Exception:
                                hover_texts.append("Data unavailable")
                    
                    # Create scatter trace
                    marker_size = 4 if len(df_plot) > 10000 else 6
                    marker_opacity = 0.4 if len(df_plot) > 10000 else 0.6
                    
                    scatter = go.Scatter(
                        x=df_plot['x_jitter'],
                        y=df_plot['PREVAILING_WAGE'],
                        mode='markers',
                        marker=dict(size=marker_size, opacity=marker_opacity, color=colors),
                        text=hover_texts,
                        hoverinfo='text',
                        name='LCA Points',
                        showlegend=False
                    )
                    
                    # Create box traces
                    box_traces = []
                    for i, lvl in enumerate(wage_levels.cat.categories):
                        y = df_plot[df_plot['PW_WAGE_LEVEL'] == lvl]['PREVAILING_WAGE']
                        if len(y) > 0:
                            box_traces.append(go.Box(
                                y=y, x=[i]*len(y), name=str(lvl),
                                marker_color=color_map[i % len(color_map)],
                                boxpoints=False, opacity=0.3, showlegend=True
                            ))
                    
                    # Create figure
                    fig = go.Figure(data=box_traces + [scatter])
                    
                    # Layout
                    layout_kwargs = {
                        "title": "Wage Distribution by Wage Level (Each Point = Lottery LCA)",
                        "xaxis": dict(
                            tickvals=list(range(len(wage_levels.cat.categories))),
                            ticktext=list(wage_levels.cat.categories),
                            title="Wage Level"
                        ),
                        "yaxis": dict(title="Wage", tickformat=",.0f"),
                        "legend_title_text": "Wage Level",
                        "uirevision": True,
                        "hovermode": 'closest'
                    }
                    

                    
                    fig.update_layout(**layout_kwargs)
                    
                    # Create config
                    config = {
                        'displayModeBar': True,
                        'displaylogo': False,
                        'modeBarButtonsToRemove': ['pan2d', 'lasso2d', 'select2d', 'autoScale2d'],
                        'scrollZoom': True,
                        'responsive': True,
                        'staticPlot': False
                    }
                else:
                    fig = None
                    config = {}
    except Exception as e:
        st.error(f"Error processing data for visualization: {e}")
        fig = None
        config = {}
    
    # Visualization creation is now handled in the data processing section above

# ============================================================================
# H-1B PETITION LOTTERY EXPLORER
# ============================================================================

st.header("🎯 H-1B Petition Lottery Explorer")
st.markdown("**Comprehensive analysis of H-1B petition data to understand policy impacts, wage distributions, and market trends**")

# Use tabs to organize all policy analysis and prevent overlapping
main_tab1, main_tab2, main_tab3, main_tab4, main_tab5 = st.tabs([
    "📊 Wage Distribution", 
    "💰 Top Occupations", 
    "📈 Yearly Analysis", 
    "🗺️ US Geographic Map",
    "📋 Policy Summary"
])

# Background rendering implementation with immediate loading
with main_tab1:
    # Always load immediately for best UX
    if df.empty or len(df) == 0:
        st.warning("⚠️ No data available for wage distribution analysis.")
        st.info("💡 Tip: Try selecting 'All' for some filters to see data.")
    else:
        render_wage_distribution_tab(df, fig, config)

with main_tab2:
    # Always load immediately for best UX
    if df.empty or len(df) == 0:
        st.warning("⚠️ No data available for top occupations analysis.")
        st.info("💡 Tip: Try selecting 'All' for some filters to see data.")
    else:
        render_top_occupations_tab(df)

with main_tab3:
    # Lazy load yearly analysis data for better performance
    with st.spinner("Loading Yearly Analysis Data..."):
        # Get data for yearly analysis (respects all filters EXCEPT year)
        yearly_df = get_yearly_data(company, state, city, soc_title)
        
        # Handle empty yearly data
        if yearly_df.empty or len(yearly_df) == 0:
            st.warning("⚠️ No yearly data found for the selected filters.")
            st.info("💡 Tip: Try selecting 'All' for some filters to see yearly trends.")
        else:
            render_yearly_analysis_tab(yearly_df, config)

with main_tab4:
    # US Geographic Map - always load immediately for best UX
    render_us_map_tab(company, year, soc_title, current_job_title)

with main_tab5:
    # Always load immediately for best UX
    if df.empty or len(df) == 0:
        st.warning("⚠️ No data available for policy summary analysis.")
        st.info("💡 Tip: Try selecting 'All' for some filters to see data.")
    else:
        render_policy_summary_tab(df)

 