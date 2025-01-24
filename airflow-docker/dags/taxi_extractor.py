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
        
        response = requests.get(f"{self.base_url}{endpoint}", params=params)
        response.raise_for_status()
    
        df = pd.DataFrame(response.json())
        return self._clean_data(df)

    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        df['pickup_datetime'] = pd.to_datetime(df['pickup_datetime'])
        df['dropoff_datetime'] = pd.to_datetime(df['dropoff_datetime'])

        numeric_cols = ['passenger_count', 'trip_distance', 'fare_amount', 'tip_amount', 'total_amount']
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        df = df[
            (df['trip_distance'] > 0) &
            (df['fare_amount'] > 0) &
            (df['passenger_count'] > 0)
        ]

        df['trip_duration_minutes'] = (
            df['dropoff_datetime'] - df['pickup_datetime']
        ).dt.total_seconds() / 60

        df = df[
            (df['trip_duration_minutes'] < 24 * 60) &
            (df['trip_distance'] < 100) &
            (df['fare_amount'] < 1000)
        ]

        return df