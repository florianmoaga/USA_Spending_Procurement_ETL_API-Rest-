import requests
import pandas as pd
from sqlalchemy import create_engine
import urllib

# API endpoint for US Federal Spending awards
url = "https://api.usaspending.gov/api/v2/search/spending_by_award/"

# ============ SQL SERVER CONFIGURATION ============
# Ensure the SERVER_NAME matches exactly what you see in SSMS (e.g., LAPTOP-NAME\SQLEXPRESS)
SERVER_NAME = r"FLORIAN\SQLEXPRESS" 
DB_NAME = "USA_Spending"

# --- OPTION A: WINDOWS AUTHENTICATION ---
# Use this if you log into SSMS without a password
odbc_str = (
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={SERVER_NAME};"
    f"DATABASE={DB_NAME};"
    f"Trusted_Connection=yes;"
)

# --- OPTION B: SQL SERVER AUTHENTICATION (Username/Password) ---
# Use this if your database requires a specific ID and Password (e.g., in a Cloud/Production environment)
# Uncomment the lines below and provide your credentials:
# DB_USER = "your_username"
# DB_PASS = "your_password"
# odbc_str = (
#     f"DRIVER={{ODBC Driver 17 for SQL Server}};"
#     f"SERVER={SERVER_NAME};"
#     f"DATABASE={DB_NAME};"
#     f"UID={DB_USER};"
#     f"PWD={DB_PASS};"
# )

# NOTE ON DRIVERS: If "ODBC Driver 17" is not installed, check your ODBC Data Sources 
# and update the string to "ODBC Driver 18" or "SQL Server" as applicable.

# Encoding the connection string for SQLAlchemy compatibility
conn_url = f"mssql+pyodbc:///?odbc_connect={urllib.parse.quote_plus(odbc_str)}"
engine = create_engine(conn_url)

# ============ STEP 0: CONNECTION CHECK (Risk Mitigation) ============
# We verify the database availability before starting the expensive API extraction process
print("=== STEP 0: TESTING SQL SERVER CONNECTION ===")
try:
    with engine.connect() as conn:
        print(f"Success! Connected to server: {SERVER_NAME}")
    print("-------------------------------------------\n")
except Exception as e:
    print(f"CRITICAL ERROR: Could not establish a connection to the database.")
    print(f"Details: {e}")
    print("\nAborting script execution to prevent unnecessary API calls.")
    exit()


# ============ STEP 1: DATA EXTRACTION ============
# Fetching data from USASpending API using pagination logic
page = 1
all_results = []

print("=== STEP 1: EXTRACT ===")
while True:
    # DATA FILTERING: You can adjust 'start_date' and 'end_date' to change the timeframe
    # 'award_type_codes' A, B, C, D represent different types of federal contracts
    payload = {
        "filters": {
            "time_period": [{"start_date": "2024-01-01", "end_date": "2024-09-30"}],
            "award_type_codes": ["A", "B", "C", "D"]
        },
        "fields": ["Award ID", "Recipient Name", "Award Amount", "Awarding Agency", "Start Date"],
        "sort": "Award Amount",
        "limit": 100,
        "page": page
    }

    print(f"Fetching page {page}...")
    response = requests.post(url, json=payload)
    data = response.json()

    all_results.extend(data["results"])
    print(f"  -> {len(data['results'])} records received. Total so far: {len(all_results)}")

    # PAGINATION LOGIC: If 'hasNext' is true, the API has more data to provide
    # We use 'page < 5' as a safety limit for testing; remove it to fetch the full dataset
    if data["page_metadata"]["hasNext"]:   
        page += 1
    else:
        break

print(f"Extraction complete: {len(all_results)} total records fetched\n")


# ============ STEP 2: DATA CLEANING ============
def clean_award(record):
    # .strip() removes any accidental leading/trailing whitespaces from strings
    return {
        "award_id": record["Award ID"].strip(),
        "recipient_name": record["Recipient Name"].strip(),
        "award_amount": round(record["Award Amount"], 2), # Ensuring 2 decimal precision for currency
        "awarding_agency": record["Awarding Agency"].strip(),
        "start_date": record["Start Date"]
    }


print("=== STEP 2: CLEAN ===")
print(f"Processing {len(all_results)} records...")
cleaned_awards = [clean_award(record) for record in all_results]
print(f"  -> Data cleaning complete\n")


# ============ STEP 3: DATA ENRICHMENT ============
# Here we add Calculated Columns (Dimensions) that are not present in the raw data
def enrich_award(record):
    # Time-based dimensions for easier filtering in reports
    record["contract_year"] = record["start_date"].split("-")[0]
    record["contract_month"] = record["start_date"].split("-")[1]
    
    # BUSINESS RULES: Defining contract magnitude categories
    # These thresholds (1B, 100M) can be adjusted based on business requirements
    record["amount_category"] = (
        "Big Contract" if record["award_amount"] >= 1_000_000_000
        else "Medium Contract" if record["award_amount"] >= 100_000_000
        else "Small Contract"
    )
    return record


print("=== STEP 3: ENRICH ===")
print(f"Enriching {len(cleaned_awards)} records...")
enriched_records = [enrich_award(record) for record in cleaned_awards]
print(f"  -> Enrichment complete. Finalizing {len(enriched_records)} records\n")


# ============ STEP 4: DATA LOAD ============
# Final stage of the ETL pipeline: Loading the transformed data into the SQL Data Warehouse
print("=== STEP 4: LOAD ===")
print("Pushing data to SQL Server...")

df = pd.DataFrame(enriched_records)

# Target table name in the 'USA_Spending' database
table_name = "Fact_Awards"

# SCHEMA MANAGEMENT: 
# 'if_exists=replace' drops and recreates the table (good for fresh daily snapshots)
# 'if_exists=append' would add new rows to existing data (good for historical tracking)
df.to_sql(
    name=table_name, 
    con=engine, 
    if_exists="replace",  
    index=False           
)

print(f"Success! {len(enriched_records)} rows written to table '{table_name}' in SQL Server.")