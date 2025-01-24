from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.hooks.base import BaseHook
from datetime import datetime, timedelta
import snowflake.connector
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG(
    'test_snowflake_connection',
    default_args=default_args,
    description='Test Snowflake Connection',
    schedule_interval=None,  # Manual trigger only
    catchup=False
)

def test_snowflake_connection(**context):
    try:
        # Get Snowflake connection details
        conn = BaseHook.get_connection('snowflake_default')
        snowflake_creds = {
            'account': conn.extra_dejson.get('account'),
            'user': conn.login,
            'password': conn.password,
            'warehouse': conn.extra_dejson.get('warehouse'),
            'database': conn.extra_dejson.get('database'),
            'schema': conn.extra_dejson.get('schema')
        }
        
        logger.info("Attempting to connect to Snowflake...")
        
        # Try to establish connection
        sf_conn = snowflake.connector.connect(
            user=snowflake_creds['user'],
            password=snowflake_creds['password'],
            account=snowflake_creds['account'],
            warehouse=snowflake_creds['warehouse'],
            database=snowflake_creds['database'],
            schema=snowflake_creds['schema']
        )
        
        # Execute a simple query
        cursor = sf_conn.cursor()
        cursor.execute('SELECT CURRENT_TIMESTAMP()')
        result = cursor.fetchone()
        
        logger.info(f"Successfully connected to Snowflake! Current timestamp: {result[0]}")
        
        # Clean up
        cursor.close()
        sf_conn.close()
        
    except Exception as e:
        logger.error(f"Failed to connect to Snowflake: {str(e)}")
        raise

test_connection = PythonOperator(
    task_id='test_snowflake_connection',
    python_callable=test_snowflake_connection,
    dag=dag
)