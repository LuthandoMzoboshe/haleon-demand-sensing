"""
Airflow DAG: Haleon Demand Sensing Pipeline
Runs daily to collect data, transform, and validate quality
"""
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

# Import pipeline modules
from data_ingestion.mock_sales_generator import HaleonSalesGenerator
from data_ingestion.google_trends_collector import GoogleTrendsCollector
from data_ingestion.weather_collector import WeatherCollector
from data_ingestion.flu_data_simulator import FluDataSimulator
from transformation.data_transformer import DataTransformer
from data_quality.quality_tests import DataQualityValidator

# Default arguments
default_args = {
    'owner': 'haleon_data_team',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

# Define DAG
dag = DAG(
    'haleon_demand_sensing_pipeline',
    default_args=default_args,
    description='Daily demand risk calculation pipeline',
    schedule_interval='0 2 * * *',  # Run at 2 AM daily
    start_date=datetime(2025, 3, 1),
    catchup=False,
    tags=['haleon', 'demand-sensing', 'production'],
)

# Task functions
def collect_sales_data(**kwargs):
    """Generate sales data"""
    print("Collecting sales data...")
    generator = HaleonSalesGenerator(start_date='2025-03-28', num_days=365)
    generator.save_to_csv()
    print("✅ Sales data collected")

def collect_trends_data(**kwargs):
    """Collect Google Trends"""
    print("Collecting Google Trends...")
    collector = GoogleTrendsCollector()
    collector.collect_all_trends()
    print("✅ Trends data collected")

def collect_weather_data(**kwargs):
    """Collect weather data"""
    print("Collecting weather data...")
    collector = WeatherCollector()
    collector.collect_all_weather()
    print("✅ Weather data collected")

def collect_flu_data(**kwargs):
    """Generate flu surveillance data"""
    print("Collecting flu data...")
    simulator = FluDataSimulator()
    simulator.generate_flu_data()
    print("✅ Flu data collected")

def transform_data(**kwargs):
    """Run transformation pipeline"""
    print("Running transformations...")
    transformer = DataTransformer()
    transformer.run_pipeline()
    print("✅ Transformations complete")

def validate_quality(**kwargs):
    """Run data quality checks"""
    print("Running quality validation...")
    validator = DataQualityValidator()
    result = validator.validate_gold_layer()
    
    if not result:
        raise Exception("Data quality validation failed!")
    
    print("✅ Quality validation passed")

def send_alerts(**kwargs):
    """Send alerts for high-risk products"""
    import pandas as pd
    
    print("Checking for high-risk products...")
    df = pd.read_parquet('data/gold/demand_risk_analytics.parquet')
    
    high_risk = df[df['risk_category'].isin(['CRITICAL', 'WARNING'])]
    
    if len(high_risk) > 0:
        print(f"\n⚠️  ALERT: {len(high_risk)} high-risk products detected")
        print(high_risk[['date', 'region', 'product_name', 'demand_risk_score', 'risk_category']].head(10))
    else:
        print("✅ No high-risk products detected")

# Define tasks
task_sales = PythonOperator(
    task_id='collect_sales_data',
    python_callable=collect_sales_data,
    dag=dag,
)

task_trends = PythonOperator(
    task_id='collect_trends_data',
    python_callable=collect_trends_data,
    dag=dag,
)

task_weather = PythonOperator(
    task_id='collect_weather_data',
    python_callable=collect_weather_data,
    dag=dag,
)

task_flu = PythonOperator(
    task_id='collect_flu_data',
    python_callable=collect_flu_data,
    dag=dag,
)

task_transform = PythonOperator(
    task_id='transform_data',
    python_callable=transform_data,
    dag=dag,
)

task_quality = PythonOperator(
    task_id='validate_quality',
    python_callable=validate_quality,
    dag=dag,
)

task_alerts = PythonOperator(
    task_id='send_alerts',
    python_callable=send_alerts,
    dag=dag,
)

# Define task dependencies
[task_sales, task_trends, task_weather, task_flu] >> task_transform >> task_quality >> task_alerts
