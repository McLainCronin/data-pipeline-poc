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