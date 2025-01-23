import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas

class NYCTaxiExtractor:
    def __init__(self, snowflake_credentials: Dict):
        self.snowflake_credentials = snowflake_credentials
        self.base_url = "https://data.cityofnewyork.us/api/views/qp3b-zxtp"

    def extract_data(self, date: datetime) -> pd.DataFrame:
         endpoint = f"/views/t7mc-8hvi/rows.json"
         params = {
             "$where": f"pickup_datetime between '{date.strftime('%Y-%m-%d')}' and '{(date + timedelta(days=1)).strftime('%Y-%m-%d')}'",
             "$limit": 50000
         }