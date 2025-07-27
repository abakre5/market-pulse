# H-1B Lottery Explorer

A Streamlit application for exploring H-1B lottery petition data from 2020-2024.

## Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the app**:
   ```bash
   streamlit run app.py
   ```

The app will open in your browser at `http://localhost:8501`

## Data Files

- `job_market_std_employer.duckdb` - DuckDB database (3.8GB)
- `Combined_LCA_Disclosure_Data_FY2020_to_FY2024.csv` - Raw CSV data (2.6GB)

## Features

- Interactive data filtering by company, year, state, city, and job title
- Wage distribution analysis with visualizations
- Geographic mapping of petition data
- Yearly trends and policy impact analysis
- Dark/light mode toggle

## Requirements

- Python 3.8+
- 4GB+ RAM recommended
- Modern web browser 