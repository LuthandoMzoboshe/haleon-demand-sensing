"""Mock Haleon Sales Data Generator"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from faker import Faker
import random

fake = Faker()

class HaleonSalesGenerator:
    def __init__(self, start_date='2025-03-28', num_days=365):
        self.start_date = pd.to_datetime(start_date)
        self.num_days = num_days
        self.products = {
            'Theraflu': {'category': 'Cold & Flu', 'base_sales': 1200, 'seasonality': 'winter'},
            'Panadol': {'category': 'Pain Relief', 'base_sales': 2500, 'seasonality': 'stable'},
            'Otrivin': {'category': 'Nasal Care', 'base_sales': 800, 'seasonality': 'winter'},
            'Sensodyne': {'category': 'Oral Health', 'base_sales': 3000, 'seasonality': 'stable'},
            'Advil': {'category': 'Pain Relief', 'base_sales': 2800, 'seasonality': 'stable'},
            'Centrum': {'category': 'Vitamins', 'base_sales': 1500, 'seasonality': 'winter_mild'},
        }
        self.regions = {
            'UK_London': {'timezone': 'Europe/London', 'winter_months': [11, 12, 1, 2, 3]},
            'US_NewYork': {'timezone': 'America/New_York', 'winter_months': [11, 12, 1, 2, 3]},
            'Germany_Berlin': {'timezone': 'Europe/Berlin', 'winter_months': [11, 12, 1, 2, 3]},
            'Australia_Sydney': {'timezone': 'Australia/Sydney', 'winter_months': [6, 7, 8, 9]},
            'Canada_Toronto': {'timezone': 'America/Toronto', 'winter_months': [11, 12, 1, 2, 3, 4]},
            'SouthAfrica_CapeTown': {'timezone': 'Africa/Johannesburg', 'winter_months': [5, 6, 7, 8, 9]},
        }
    
    def generate_seasonal_multiplier(self, date, product_name):
        month = date.month
        product_info = self.products[product_name]
        seasonality_type = product_info['seasonality']
        if seasonality_type == 'winter':
            if month in [11, 12, 1, 2, 3]:
                return random.uniform(2.5, 4.0)
            elif month in [4, 10]:
                return random.uniform(1.3, 1.7)
            else:
                return random.uniform(0.4, 0.7)
        elif seasonality_type == 'winter_mild':
            if month in [11, 12, 1, 2]:
                return random.uniform(1.5, 2.0)
            else:
                return random.uniform(0.9, 1.1)
        else:
            return random.uniform(0.95, 1.05)
    
    def add_weekly_pattern(self, date, base_amount):
        day_of_week = date.dayofweek
        if day_of_week in [5, 6]:
            multiplier = random.uniform(1.2, 1.4)
        elif day_of_week == 4:
            multiplier = random.uniform(1.1, 1.2)
        else:
            multiplier = random.uniform(0.9, 1.0)
        return base_amount * multiplier
    
    def add_random_events(self, date, base_amount):
        if random.random() < 0.05:
            spike_multiplier = random.uniform(1.5, 3.0)
            return base_amount * spike_multiplier
        return base_amount
    
    def generate_sales_data(self):
        records = []
        for day_offset in range(self.num_days):
            current_date = self.start_date + timedelta(days=day_offset)
            for product_name, product_info in self.products.items():
                for region_name, region_info in self.regions.items():
                    base_sales = product_info['base_sales']
                    seasonal_mult = self.generate_seasonal_multiplier(current_date, product_name)
                    sales = base_sales * seasonal_mult
                    sales = self.add_weekly_pattern(current_date, sales)
                    sales = self.add_random_events(current_date, sales)
                    noise = random.uniform(0.85, 1.15)
                    sales = sales * noise
                    regional_multipliers = {
                        'UK_London': 1.0, 'US_NewYork': 1.3, 'Germany_Berlin': 0.9,
                        'Australia_Sydney': 0.7, 'Canada_Toronto': 0.8, 'SouthAfrica_CapeTown': 0.6,
                    }
                    sales = sales * regional_multipliers[region_name]
                    unit_price = {
                        'Theraflu': 8.99, 'Panadol': 6.49, 'Otrivin': 9.99,
                        'Sensodyne': 5.99, 'Advil': 7.49, 'Centrum': 12.99,
                    }[product_name]
                    revenue = sales * unit_price
                    stock_on_hand = random.randint(5000, 15000)
                    records.append({
                        'sale_date': current_date, 'region': region_name,
                        'product_name': product_name, 'product_category': product_info['category'],
                        'units_sold': int(sales), 'unit_price': unit_price,
                        'revenue': round(revenue, 2), 'stock_on_hand': stock_on_hand,
                        'stockout_risk': 'HIGH' if stock_on_hand < 7000 else 'NORMAL',
                    })
        df = pd.DataFrame(records)
        return df
    
    def save_to_csv(self, output_path='data/raw/haleon_sales_data.csv'):
        df = self.generate_sales_data()
        df.to_csv(output_path, index=False)
        print(f"✅ Generated {len(df):,} sales records")
        print(f"📅 Date range: {df['sale_date'].min()} to {df['sale_date'].max()}")
        print(f"💰 Total revenue: ${df['revenue'].sum():,.2f}")
        print(f"📦 Saved to: {output_path}")
        return df

if __name__ == "__main__":
    generator = HaleonSalesGenerator(start_date='2025-03-28', num_days=365)
    df = generator.save_to_csv()
    print("\n📊 Sample data:")
    print(df.head(10))
    print("\n📈 Summary by product:")
    print(df.groupby('product_name')['units_sold'].agg(['sum', 'mean', 'std']))
