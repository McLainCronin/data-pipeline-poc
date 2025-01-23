# NYC Taxi Data Pipeline

## Overview
End-to-end data pipeline processing NYC Taxi data using Airflow, Snowflake, and dbt. Extracts from NYC Taxi API, transforms via dbt, and loads to Snowflake for analysis.

## Status
🚧 **Work in Progress** 🚧
This project is under active development. Core features are being implemented and the structure may change. Feel free to suggest improvements :)

Current Status:
- Setting up infrastructure
- Implementing data ingestion
- Building transformation logic

## Architecture
- Data Source: NYC Taxi & Limousine Commission API
- Orchestration: Apache Airflow 2.7.1
- Data Warehouse: Snowflake
- Transformation: dbt
- Infrastructure: Docker
- CI/CD: GitHub Actions

## Prerequisites
- Python 3.8+
- Docker Desktop 4.0+
- Git
- VS Code (recommended)
- Snowflake Account
- dbt Cloud Account (or dbt Core)
- GitHub Account

## Quick Start
```bash
git clone <repository-url>
cd nyc-taxi-pipeline
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
docker-compose up -d
```

## Setup Instructions

### 1. Environment Setup
```bash
# Clone and setup repository
git clone <repository-url>
cd nyc-taxi-pipeline

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
```

### 2. Snowflake Configuration
```sql
-- Execute in Snowflake console
CREATE WAREHOUSE TAXI_WH WITH 
    WAREHOUSE_SIZE = 'XSMALL'
    AUTO_SUSPEND = 300
    AUTO_RESUME = TRUE;

CREATE DATABASE TAXI_DB;

CREATE SCHEMA TAXI_DB.RAW;
CREATE SCHEMA TAXI_DB.STAGING;
CREATE SCHEMA TAXI_DB.ANALYTICS;

-- Create service account
CREATE USER AIRFLOW_SERVICE
    PASSWORD = '<password>'
    DEFAULT_ROLE = AIRFLOW_ROLE
    DEFAULT_WAREHOUSE = TAXI_WH;

-- Grant privileges
GRANT USAGE ON WAREHOUSE TAXI_WH TO ROLE AIRFLOW_ROLE;
GRANT USAGE ON DATABASE TAXI_DB TO ROLE AIRFLOW_ROLE;
GRANT USAGE ON SCHEMA TAXI_DB.RAW TO ROLE AIRFLOW_ROLE;
GRANT ALL ON SCHEMA TAXI_DB.RAW TO ROLE AIRFLOW_ROLE;
```

### 3. Airflow Configuration
Edit `.env` file:
```env
AIRFLOW_UID=50000
AIRFLOW__CORE__EXECUTOR=LocalExecutor
AIRFLOW__CORE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@postgres/airflow
AIRFLOW__CORE__FERNET_KEY=${FERNET_KEY}
AIRFLOW__CORE__LOAD_EXAMPLES=False
AIRFLOW__CORE__ENABLE_XCOM_PICKLING=True

# Snowflake Connection
SNOWFLAKE_ACCOUNT=<account>
SNOWFLAKE_USER=<user>
SNOWFLAKE_PASSWORD=<password>
SNOWFLAKE_WAREHOUSE=TAXI_WH
SNOWFLAKE_DATABASE=TAXI_DB
```

### 4. dbt Setup
```yaml
# ~/.dbt/profiles.yml
taxi_pipeline:
  target: dev
  outputs:
    dev:
      type: snowflake
      account: <account>
      user: <user>
      password: <password>
      role: TRANSFORMER
      database: TAXI_DB
      warehouse: TAXI_WH
      schema: ANALYTICS
      threads: 4
```

## Project Structure
```
nyc-taxi-pipeline/
├── .github/
│   └── workflows/                # CI/CD pipeline configurations
├── airflow/
│   ├── dags/                    # Airflow DAG definitions
│   │   ├── taxi_ingestion.py    # Main ingestion DAG
│   │   └── utils/               # Helper functions
│   └── plugins/                 # Custom Airflow plugins
├── dbt/
│   ├── models/                  # dbt transformation models
│   │   ├── staging/            # Initial cleaning/typing
│   │   └── analytics/          # Business logic transforms
│   ├── tests/                  # Data quality tests
│   ├── macros/                 # Reusable SQL functions
│   └── dbt_project.yml         # dbt configuration
├── tests/                      # Python unit tests
├── scripts/                    # Utility scripts
├── .env.example               # Environment template
├── docker-compose.yaml        # Docker services config
├── requirements.txt           # Python dependencies
└── README.md                 # This file
```

## Data Pipeline
1. Daily API data extraction (Yellow taxi, Green taxi, FHV)
2. Raw data staging in Snowflake
3. dbt transformations
4. Analytics table generation
5. Data quality validation

## Development Workflow

### Feature Development
```bash
# Create feature branch
git checkout -b feature/new-feature

# Develop and test locally
pytest tests/
dbt test

# Commit changes
git add .
git commit -m "feat: add new feature"
git push origin feature/new-feature
```

### Testing
```bash
# Run Python tests
pytest tests/

# Run dbt tests
cd dbt
dbt test

# Run specific test
pytest tests/test_specific.py
```

### Deployment
Deployments are automated via GitHub Actions on merge to main:
1. Runs all tests
2. Builds Docker images
3. Updates Airflow DAGs
4. Executes dbt transformations

## Monitoring
- Airflow UI: http://localhost:8080
- dbt docs: Generated documentation
- Snowflake History: Query history and performance
- Logs: Available in Airflow UI and Docker logs

## Troubleshooting

### Common Issues
1. Airflow Connection Issues:
```bash
docker-compose down -v
docker-compose up -d
```

2. dbt Connection Errors:
- Verify profiles.yml configuration
- Check Snowflake credentials
- Ensure proper role permissions

3. API Rate Limiting:
- Adjust extraction schedule in DAG
- Implement backoff strategy

## Contributing
1. Fork the repository
2. Create feature branch
3. Commit changes
4. Create pull request

## License
MIT License - see LICENSE.md

## Contact
McLain Cronin
cronin97@gmail.com
GitHub: McLainCronin
