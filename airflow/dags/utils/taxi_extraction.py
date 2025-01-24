import logging
import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NYCTaxiExtractor:
    def __init__(self, snowflake_credentials: Dict):
        self.snowflake_credentials = snowflake_credentials
        self.base_url = "https://data.cityofnewyork.us/resource/t29m-gskq.json"

    def _connect_snowflake(self):
        return snowflake.connector.connect(
            account=self.snowflake_credentials['account'],
            user=self.snowflake_credentials['user'],
            password=self.snowflake_credentials['password'],
            warehouse=self.snowflake_credentials['warehouse'],
            database=self.snowflake_credentials['database'],
            schema=self.snowflake_credentials['schema']
        )

    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        date_columns = ['pickup_datetime', 'dropoff_datetime']
        for col in date_columns:
            df[col] = pd.to_datetime(df[col])

        numeric_cols = ['passenger_count', 'trip_distance', 'fare_amount', 
                       'extra', 'tip_amount', 'total_amount']
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        return df
    
    def extract_data(self, date: datetime) -> pd.DataFrame:
        try:
            params = {
                "$where": f"pickup_datetime between '{date.strftime('%Y-%m-%d')}T00:00:00' and '{date.strftime('%Y-%m-%d')}T23:59:59'",
                "$limit": 50000
            }
            
            logger.info(f"Extracting data for date: {date.strftime('%Y-%m-%d')}")
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            
            df = pd.DataFrame(response.json())
            return self._clean_data(df)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            raise

    def load_to_snowflake(self, df: pd.DataFrame, table_name: str):
        try:
            conn = self._connect_snowflake()
            write_pandas(conn, df, table_name.upper())
            logger.info(f"Successfully loaded {len(df)} rows to {table_name}")
            
        except Exception as e:
            logger.error(f"Snowflake load failed: {str(e)}")
            raise
            
        finally:
            conn.close()