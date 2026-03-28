"""
Weather Data Collector
Collects REAL historical weather data via Open-Meteo API (free, no key needed)
"""
import pandas as pd
import requests
from datetime import datetime, timedelta

class WeatherCollector:
    def __init__(self):
        self.base_url = "https://archive-api.open-meteo.com/v1/archive"
        
        # Major cities for each Haleon region
        self.locations = {
            'UK_London': {'lat': 51.5074, 'lon': -0.1278},
            'US_NewYork': {'lat': 40.7128, 'lon': -74.0060},
            'Germany_Berlin': {'lat': 52.5200, 'lon': 13.4050},
            'Australia_Sydney': {'lat': -33.8688, 'lon': 151.2093},
            'Canada_Toronto': {'lat': 43.6532, 'lon': -79.3832},
            'SouthAfrica_CapeTown': {'lat': -33.9249, 'lon': 18.4241}
        }
    
    def collect_weather_data(self, location_name, lat, lon, start_date, end_date):
        """
        Collect historical weather data from Open-Meteo API
        """
        params = {
            'latitude': lat,
            'longitude': lon,
            'start_date': start_date,
            'end_date': end_date,
            'daily': 'temperature_2m_max,temperature_2m_min,temperature_2m_mean,precipitation_sum',
            'timezone': 'auto'
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if 'daily' in data:
                df = pd.DataFrame({
                    'date': pd.to_datetime(data['daily']['time']),
                    'temp_max': data['daily']['temperature_2m_max'],
                    'temp_min': data['daily']['temperature_2m_min'],
                    'temp_mean': data['daily']['temperature_2m_mean'],
                    'precipitation': data['daily']['precipitation_sum'],
                    'region': location_name
                })
                return df
            
            return pd.DataFrame()
            
        except Exception as e:
            print(f"⚠️  Error collecting weather for {location_name}: {e}")
            return pd.DataFrame()
    
    def collect_all_weather(self, start_date='2025-03-28', days_back=365, 
                           output_path='data/raw/weather_data.csv'):
        """
        Collect weather data for all regions
        """
        start = datetime.strptime(start_date, '%Y-%m-%d') - timedelta(days=days_back)
        end = datetime.strptime(start_date, '%Y-%m-%d')
        
        start_str = start.strftime('%Y-%m-%d')
        end_str = end.strftime('%Y-%m-%d')
        
        print(f"🌡️  Collecting weather data from {start_str} to {end_str}")
        
        all_data = []
        
        for location_name, coords in self.locations.items():
            print(f"Fetching {location_name}...", end=' ')
            
            df = self.collect_weather_data(
                location_name, 
                coords['lat'], 
                coords['lon'],
                start_str,
                end_str
            )
            
            if not df.empty:
                all_data.append(df)
                print(f"✅ {len(df)} days")
            else:
                print("⚠️  No data")
        
        if all_data:
            final_df = pd.concat(all_data, ignore_index=True)
            
            # Calculate temperature delta from monthly average
            final_df['month'] = pd.to_datetime(final_df['date']).dt.month
            monthly_avg = final_df.groupby(['region', 'month'])['temp_mean'].transform('mean')
            final_df['temp_delta_from_monthly_avg'] = final_df['temp_mean'] - monthly_avg
            
            final_df.to_csv(output_path, index=False)
            print(f"\n✅ Saved {len(final_df):,} weather records to {output_path}")
            return final_df
        else:
            print("\n❌ No weather data collected")
            return pd.DataFrame()

if __name__ == "__main__":
    collector = WeatherCollector()
    df = collector.collect_all_weather()
    
    if not df.empty:
        print("\n📊 Sample data:")
        print(df.head(10))
        print("\n🌡️  Temperature summary by region:")
        print(df.groupby('region')['temp_mean'].agg(['mean', 'min', 'max']))
