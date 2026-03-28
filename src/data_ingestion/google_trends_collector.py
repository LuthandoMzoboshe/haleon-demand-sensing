"""
Google Trends Data Collector
Collects REAL search interest data for health-related symptoms
"""
import pandas as pd
from pytrends.request import TrendReq
from datetime import datetime, timedelta
import time

class GoogleTrendsCollector:
    def __init__(self):
        self.pytrends = TrendReq(hl='en-US', tz=360)
        
        # Health symptom keywords that drive Haleon product demand
        self.keyword_groups = {
            'cold_flu': ['flu symptoms', 'cold medicine', 'sore throat', 'cough remedy'],
            'pain': ['headache relief', 'back pain', 'muscle pain'],
            'oral_health': ['toothache', 'sensitive teeth', 'gum pain'],
            'nasal': ['stuffy nose', 'nasal congestion', 'sinus relief']
        }
        
        self.regions = {
            'UK': 'GB',
            'US': 'US', 
            'Germany': 'DE',
            'Australia': 'AU',
            'Canada': 'CA',
            'SouthAfrica': 'ZA'
        }
    
    def collect_trends_data(self, keywords, geo='', timeframe='today 12-m'):
        """
        Collect Google Trends data for specific keywords
        """
        try:
            self.pytrends.build_payload(
                keywords, 
                cat=0, 
                timeframe=timeframe, 
                geo=geo, 
                gprop=''
            )
            
            # Get interest over time
            interest_df = self.pytrends.interest_over_time()
            
            if not interest_df.empty:
                interest_df = interest_df.drop(columns=['isPartial'], errors='ignore')
                interest_df['geo'] = geo if geo else 'GLOBAL'
                interest_df.reset_index(inplace=True)
                return interest_df
            
            return pd.DataFrame()
            
        except Exception as e:
            print(f"⚠️  Error collecting trends for {keywords}: {e}")
            return pd.DataFrame()
    
    def collect_all_trends(self, output_path='data/raw/google_trends_data.csv'):
        """
        Collect trends data for all keyword groups and regions
        """
        all_data = []
        total_requests = len(self.keyword_groups) * len(self.regions)
        current = 0
        
        print(f"🔍 Collecting Google Trends data...")
        print(f"📊 Total requests: {total_requests}")
        
        for category, keywords in self.keyword_groups.items():
            for region_name, region_code in self.regions.items():
                current += 1
                print(f"[{current}/{total_requests}] {category} - {region_name}...", end=' ')
                
                df = self.collect_trends_data(keywords, geo=region_code)
                
                if not df.empty:
                    df['category'] = category
                    df['region'] = region_name
                    all_data.append(df)
                    print("✅")
                else:
                    print("⚠️  No data")
                
                # Rate limiting - Google restricts requests
                time.sleep(2)
        
        if all_data:
            final_df = pd.concat(all_data, ignore_index=True)
            final_df.to_csv(output_path, index=False)
            print(f"\n✅ Saved {len(final_df):,} trend records to {output_path}")
            return final_df
        else:
            print("\n❌ No trends data collected")
            return pd.DataFrame()

if __name__ == "__main__":
    collector = GoogleTrendsCollector()
    df = collector.collect_all_trends()
    
    if not df.empty:
        print("\n📊 Sample data:")
        print(df.head())
        print("\n📈 Date range:")
        print(f"From: {df['date'].min()}")
        print(f"To: {df['date'].max()}")
