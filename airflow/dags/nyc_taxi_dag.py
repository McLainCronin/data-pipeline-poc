from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from taxi_extraction import NYCTaxiExtractor

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
    'nyc_taxi_pipeline',
    default_args=default_args,
    description='NYC Taxi Data Pipeline',
    schedule_interval='@daily',
    catchup=False
)

def extract_load_taxi_data(**context):
    execution_date = context['execution_date']
    
    snowflake_creds = {
        'account': '{{ conn.snowflake_default.account }}',
        'user': '{{ conn.snowflake_default.login }}',
        'password': '{{ conn.snowflake_default.password }}',
        'warehouse': 'TAXI_WH',
        'database': 'TAXI_DB',
        'schema': 'RAW'
    }
    
    extractor = NYCTaxiExtractor(snowflake_creds)
    df = extractor.extract_data(execution_date)
    extractor.load_to_snowflake(df, 'RAW_TAXI_TRIPS')

extract_load_task = PythonOperator(
    task_id='extract_load_taxi_data',
    python_callable=extract_load_taxi_data,
    dag=dag
)

extract_load_task