"""
Master data collection script - runs all collectors
"""
from mock_sales_generator import HaleonSalesGenerator
from google_trends_collector import GoogleTrendsCollector
from weather_collector import WeatherCollector
from flu_data_simulator import FluDataSimulator
import time

def collect_all():
    print("=" * 60)
    print("🚀 HALEON DATA COLLECTION PIPELINE")
    print("=" * 60)
    
    start_time = time.time()
    
    # 1. Sales data
    print("\n1️⃣ Generating sales data...")
    sales_gen = HaleonSalesGenerator(start_date='2025-03-28', num_days=365)
    sales_gen.save_to_csv()
    
    # 2. Google Trends
    print("\n2️⃣ Collecting Google Trends (REAL data)...")
    trends = GoogleTrendsCollector()
    trends.collect_all_trends()
    
    # 3. Weather
    print("\n3️⃣ Collecting weather data (REAL data)...")
    weather = WeatherCollector()
    weather.collect_all_weather()
    
    # 4. Flu surveillance
    print("\n4️⃣ Generating flu surveillance data...")
    flu = FluDataSimulator()
    flu.generate_flu_data()
    
    elapsed = time.time() - start_time
    
    print("\n" + "=" * 60)
    print(f"✅ ALL DATA COLLECTED in {elapsed:.1f} seconds")
    print("=" * 60)

if __name__ == "__main__":
    collect_all()
