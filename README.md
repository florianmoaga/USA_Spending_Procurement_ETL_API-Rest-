# USA_Spending_Procurement_ETL_API-Rest-


US Federal Spending ETL & Analytics Pipeline
📊 Project Overview
This project demonstrates a complete, end-to-end Data Engineering pipeline that extracts federal contract data from the USASpending.gov API, processes it using Python, stores it in a SQL Server data warehouse, and visualizes key business insights through an interactive Power BI dashboard.

The goal of this project is to analyze US government spending patterns for the fiscal year 2024, focusing on contract magnitudes, awarding agencies, and top recipients.

🏗️ System Architecture
The pipeline follows the classic ETL (Extract, Transform, Load) pattern:

Extract: Automated data retrieval from a REST API with pagination handling.
Transform: Data cleaning, type casting, and business logic enrichment (e.g., contract size categorization).
Load: Efficient data transfer into a structured SQL Server database using SQLAlchemy.
Visualize: Interactive reporting in Power BI using advanced DAX measures and data modeling.
🛠️ Tech Stack
Language: Python 3.13
Libraries: Pandas, SQLAlchemy, Requests, PyODBC
Database: SQL Server (SSMS)
BI Tool: Power BI (DAX)
🚀 Key Features
1. Robust Python ETL Pipeline
Risk Mitigation: Includes a "Step 0" connectivity check to ensure the database is reachable before starting API calls.
Pagination Logic: Automatically handles multi-page API responses.
Alternative Auth: Supports both Windows Authentication (Local) and SQL Server Authentication (Production/Cloud).
2. Data Enrichment (Business Logic)
Beyond raw data, the script creates new dimensions:

Contract Categorization: Automatically flags contracts as "Big", "Medium", or "Small" based on fiscal thresholds.
Time Intelligence: Deconstructs dates into Years and Months for granular trend analysis.
3. SQL Data Warehousing
Data is stored in a clean Fact_Awards table.
Optimized for BI ingestion with appropriate data types for financial values and dates.
4. Interactive Power BI Dashboard
The report answers four fundamental business questions:

How much? (KPI Cards: Total Spent, Avg Award, Total Count)
Who gives? (Analysis of Awarding Agencies)
Who receives? (Top 10 Recipients by value/count)
When? (Timeline trend analysis)
📈 Dashboard Preview
(Add a high-quality screenshot of your Power BI dashboard here)

🔢 DAX Measures Used
To provide deeper insights, the following DAX measures were implemented:

Total Awarded = SUM(Fact_Awards[award_amount])
Number of Contracts = COUNTROWS(Fact_Awards)
Avg Contract Value = [Total Awarded] / [Number of Contracts]
% of Total = DIVIDE([Total Awarded], CALCULATE([Total Awarded], ALL(Fact_Awards)))
💡 Key Insights Captured
Concentration Analysis: Identifying if a few "Big Contracts" dominate the total budget relative to their volume.
Agency Dominance: Visualizing which departments (e.g., Defense vs. Energy) are the primary drivers of spending.
Recipient Trends: Identifying the top private corporations benefiting from federal awards.
🔧 How to Run
Database: Create a SQL Server database named USA_Spending.
Python: Run etl_pipeline.py to fetch data and populate the SQL table.
Power BI: Open the .pbix file and hit Refresh to sync with your local SQL data.
Author: [Numele Tău]
Role: Data Engineer / Analyst Portfolio Project
