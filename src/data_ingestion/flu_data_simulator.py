"""
Flu Surveillance Data Simulator
Simulates CDC/WHO-style flu activity levels based on realistic patterns
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

class FluDataSimulator:
    def __init__(self):
        self.regions = [
            'UK_London', 'US_NewYork', 'Germany_Berlin', 
            'Australia_Sydney', 'Canada_Toronto', 'SouthAfrica_CapeTown'
        ]
        
        self.activity_levels = ['Minimal', 'Low', 'Moderate', 'High', 'Very High']
        
        # Northern hemisphere winter: Nov-Mar
        # Southern hemisphere winter: May-Sep
        self.hemisphere_patterns = {
            'northern': {'peak_months': [12, 1, 2], 'active_months': [11, 12, 1, 2, 3]},
            'southern': {'peak_months': [6, 7, 8], 'active_months': [5, 6, 7, 8, 9]}
        }
        
        self.region_hemisphere = {
            'UK_London': 'northern',
            'US_NewYork': 'northern',
            'Germany_Berlin': 'northern',
            'Australia_Sydney': 'southern',
            'Canada_Toronto': 'northern',
            'SouthAfrica_CapeTown': 'southern'
        }
    
    def get_activity_level(self, date, region):
        """
        Determine flu activity level based on date and region
        """
        month = date.month
        hemisphere = self.region_hemisphere[region]
        pattern = self.hemisphere_patterns[hemisphere]
        
        if month in pattern['peak_months']:
            # Peak season - higher chance of high activity
            return random.choices(
                self.activity_levels,
                weights=[5, 10, 20, 35, 30],  # Favor High/Very High
                k=1
            )[0]
        elif month in pattern['active_months']:
            # Active season
            return random.choices(
                self.activity_levels,
                weights=[10, 20, 35, 25, 10],  # Favor Moderate/High
                k=1
            )[0]
        else:
            # Off season
            return random.choices(
                self.activity_levels,
                weights=[40, 35, 20, 5, 0],  # Favor Minimal/Low
                k=1
            )[0]
    
    def generate_flu_data(self, start_date='2025-03-28', num_days=365, 
                         output_path='data/raw/flu_surveillance_data.csv'):
        """
        Generate flu surveillance data
        """
        start = datetime.strptime(start_date, '%Y-%m-%d') - timedelta(days=num_days)
        
        records = []
        
        for day_offset in range(num_days):
            current_date = start + timedelta(days=day_offset)
            
            # Weekly reporting (every Sunday)
            if current_date.weekday() == 6:
                for region in self.regions:
                    activity_level = self.get_activity_level(current_date, region)
                    
                    # Convert activity level to numeric score
                    level_scores = {
                        'Minimal': 1,
                        'Low': 2,
                        'Moderate': 3,
                        'High': 4,
                        'Very High': 5
                    }
                    
                    # Simulated metrics
                    base_cases = level_scores[activity_level] * 1000
                    cases = int(base_cases * random.uniform(0.8, 1.2))
                    
                    records.append({
                        'week_ending': current_date,
                        'region': region,
                        'flu_activity_level': activity_level,
                        'activity_score': level_scores[activity_level],
                        'estimated_cases': cases,
                        'data_source': 'Simulated_Surveillance'
                    })
        
        df = pd.DataFrame(records)
        df.to_csv(output_path, index=False)
        
        print(f"✅ Generated {len(df):,} flu surveillance records")
        print(f"📅 Date range: {df['week_ending'].min()} to {df['week_ending'].max()}")
        print(f"📦 Saved to: {output_path}")
        
        return df

if __name__ == "__main__":
    simulator = FluDataSimulator()
    df = simulator.generate_flu_data()
    
    print("\n📊 Sample data:")
    print(df.head(10))
    
    print("\n🦠 Activity level distribution:")
    print(df['flu_activity_level'].value_counts())
    
    print("\n📈 By region:")
    print(df.groupby('region')['activity_score'].mean().sort_values(ascending=False))
