"""
Core data transformation logic - Bronze → Silver → Gold
"""
import pandas as pd
import numpy as np
from pathlib import Path

class DataTransformer:
    def __init__(self):
        self.bronze_dir = Path("data/bronze")
        self.silver_dir = Path("data/silver")
        self.gold_dir = Path("data/gold")
        
        for d in [self.bronze_dir, self.silver_dir, self.gold_dir]:
            d.mkdir(parents=True, exist_ok=True)
    
    def bronze_layer(self):
        """Load raw CSVs and save as Parquet"""
        print("\n🥉 BRONZE LAYER: Loading raw data...")
        
        sales = pd.read_csv("data/raw/haleon_sales_data.csv", parse_dates=['sale_date'])
        weather = pd.read_csv("data/raw/weather_data.csv", parse_dates=['date'])
        trends = pd.read_csv("data/raw/google_trends_data.csv", parse_dates=['date'])
        flu = pd.read_csv("data/raw/flu_surveillance_data.csv", parse_dates=['week_ending'])
        
        sales.to_parquet(self.bronze_dir / "sales.parquet", index=False)
        weather.to_parquet(self.bronze_dir / "weather.parquet", index=False)
        trends.to_parquet(self.bronze_dir / "trends.parquet", index=False)
        flu.to_parquet(self.bronze_dir / "flu.parquet", index=False)
        
        print(f"  ✅ Sales: {len(sales):,}")
        print(f"  ✅ Weather: {len(weather):,}")
        print(f"  ✅ Trends: {len(trends):,}")
        print(f"  ✅ Flu: {len(flu):,}")
        
        return sales, weather, trends, flu
    
    def silver_layer(self, sales, weather, trends, flu):
        """Clean and aggregate data"""
        print("\n🥈 SILVER LAYER: Cleaning data...")
        
        # Rename date columns for consistency
        sales = sales.rename(columns={'sale_date': 'date'})
        flu = flu.rename(columns={'week_ending': 'date'})
        
        # Aggregate trends by date and region
        trend_cols = [c for c in trends.columns if c not in ['date', 'geo', 'region', 'category']]
        trends_agg = trends.groupby(['date', 'region'])[trend_cols].mean().reset_index()
        trends_agg['trend_score'] = trends_agg[trend_cols].mean(axis=1)
        trends_agg['trend_z_score'] = (trends_agg['trend_score'] - trends_agg['trend_score'].mean()) / trends_agg['trend_score'].std()
        
        # Map region names
        region_map = {
            'UK': 'UK_London',
            'US': 'US_NewYork',
            'Germany': 'Germany_Berlin',
            'Australia': 'Australia_Sydney',
            'Canada': 'Canada_Toronto',
            'SouthAfrica': 'SouthAfrica_CapeTown'
        }
        trends_agg['region'] = trends_agg['region'].map(region_map)
        
        # Calculate sales velocity
        sales = sales.sort_values(['region', 'product_name', 'date'])
        sales['sales_growth_pct'] = sales.groupby(['region', 'product_name'])['units_sold'].pct_change() * 100
        sales['sales_growth_pct'] = sales['sales_growth_pct'].fillna(0)
        
        # Save silver
        sales.to_parquet(self.silver_dir / "sales_clean.parquet", index=False)
        weather.to_parquet(self.silver_dir / "weather_clean.parquet", index=False)
        trends_agg.to_parquet(self.silver_dir / "trends_clean.parquet", index=False)
        flu.to_parquet(self.silver_dir / "flu_clean.parquet", index=False)
        
        print(f"  ✅ Silver layer complete")
        
        return sales, weather, trends_agg, flu
    
    def gold_layer(self, sales, weather, trends, flu):
        """Join data and calculate Demand Risk Score"""
        print("\n🥇 GOLD LAYER: Joining & calculating risk scores...")
        
        # Start with sales
        gold = sales.copy()
        
        # Join weather
        gold = gold.merge(weather, on=['date', 'region'], how='left')
        print(f"  ✅ Joined weather")
        
        # Join trends
        gold = gold.merge(
            trends[['date', 'region', 'trend_score', 'trend_z_score']], 
            on=['date', 'region'], 
            how='left'
        )
        print(f"  ✅ Joined trends")
        
        # Expand flu data from weekly to daily (forward fill)
        all_dates = pd.date_range(gold['date'].min(), gold['date'].max(), freq='D')
        flu_daily_list = []
        
        for region in gold['region'].unique():
            region_flu = flu[flu['region'] == region].copy()
            if len(region_flu) > 0:
                daily = pd.DataFrame({'date': all_dates})
                daily = daily.merge(region_flu, on='date', how='left')
                daily['region'] = region
                daily['flu_activity_level'] = daily['flu_activity_level'].fillna(method='ffill')
                daily['activity_score'] = daily['activity_score'].fillna(method='ffill')
                flu_daily_list.append(daily)
        
        if flu_daily_list:
            flu_daily = pd.concat(flu_daily_list, ignore_index=True)
            gold = gold.merge(
                flu_daily[['date', 'region', 'flu_activity_level', 'activity_score']], 
                on=['date', 'region'], 
                how='left'
            )
            print(f"  ✅ Joined flu data")
        
        # ========== CALCULATE RISK SCORES ==========
        print("\n  🎯 Calculating Demand Risk Score...")
        
        # 1. Temperature Risk (max 25 points)
        gold['temp_risk'] = 0
        gold.loc[gold['temp_delta_from_monthly_avg'] < -5, 'temp_risk'] = 25
        gold.loc[(gold['temp_delta_from_monthly_avg'] >= -5) & (gold['temp_delta_from_monthly_avg'] < -2), 'temp_risk'] = 15
        
        # 2. Trend Risk (max 30 points)
        gold['trend_risk'] = 0
        gold.loc[gold['trend_z_score'] > 2.0, 'trend_risk'] = 30
        gold.loc[(gold['trend_z_score'] >= 1.5) & (gold['trend_z_score'] <= 2.0), 'trend_risk'] = 20
        
        # 3. Flu Risk (max 25 points)
        flu_risk_map = {'Very High': 25, 'High': 18, 'Moderate': 10, 'Low': 5, 'Minimal': 0}
        gold['flu_risk'] = gold['flu_activity_level'].map(flu_risk_map).fillna(0)
        
        # 4. Sales Velocity Risk (max 20 points)
        gold['velocity_risk'] = 0
        gold.loc[gold['sales_growth_pct'] > 30, 'velocity_risk'] = 20
        gold.loc[(gold['sales_growth_pct'] >= 15) & (gold['sales_growth_pct'] <= 30), 'velocity_risk'] = 12
        
        # Total Risk Score
        gold['demand_risk_score'] = (
            gold['temp_risk'] + gold['trend_risk'] + 
            gold['flu_risk'] + gold['velocity_risk']
        )
        
        # Risk Category
        gold['risk_category'] = 'NORMAL'
        gold.loc[gold['demand_risk_score'] >= 40, 'risk_category'] = 'WARNING'
        gold.loc[gold['demand_risk_score'] >= 70, 'risk_category'] = 'CRITICAL'
        
        # Action Recommendation
        gold['action_recommendation'] = gold['risk_category'].map({
            'CRITICAL': 'Increase stock immediately - high demand spike expected',
            'WARNING': 'Monitor closely - potential demand increase',
            'NORMAL': 'No action needed'
        })
        
        # Save
        gold.to_parquet(self.gold_dir / "demand_risk_analytics.parquet", index=False)
        gold.to_csv(self.gold_dir / "demand_risk_analytics.csv", index=False)
        
        print(f"\n  ✅ Gold layer created: {len(gold):,} records")
        print(f"\n  📊 Risk Score Summary:")
        print(f"     Average: {gold['demand_risk_score'].mean():.1f}")
        print(f"     Max: {gold['demand_risk_score'].max():.0f}")
        print(f"\n  ⚠️  Risk Categories:")
        print(gold['risk_category'].value_counts())
        
        # Show sample high-risk records
        print("\n🔥 Sample HIGH RISK records:")
        high_risk = gold[gold['risk_category'].isin(['CRITICAL', 'WARNING'])].nlargest(5, 'demand_risk_score')
        if len(high_risk) > 0:
            print(high_risk[['date', 'region', 'product_name', 'demand_risk_score', 'risk_category']].to_string(index=False))
        
        return gold
        
        # Expand flu data from weekly to daily 
    def run_pipeline(self):
        """Execute full pipeline"""
        print("=" * 70)
        print("🚀 HALEON DATA TRANSFORMATION PIPELINE")
        print("=" * 70)
        
        sales, weather, trends, flu = self.bronze_layer()
        sales, weather, trends, flu = self.silver_layer(sales, weather, trends, flu)
        gold = self.gold_layer(sales, weather, trends, flu)
        
        print("\n" + "=" * 70)
        print("✅ TRANSFORMATION COMPLETE")
        print("=" * 70)
        
        return gold

if __name__ == "__main__":
    transformer = DataTransformer()
    transformer.run_pipeline()

    def run_with_quality_checks(self):
        """Run pipeline with data quality validation"""
        # Run transformation
        result = self.run_pipeline()
        
        # Run quality checks
        print("\n" + "=" * 70)
        print("Running data quality validation...")
        print("=" * 70)
        
        import sys
        sys.path.append('src/data_quality')
        from quality_tests import DataQualityValidator
        
        validator = DataQualityValidator()
        validation_passed = validator.validate_gold_layer()
        
        if validation_passed:
            print("\n✅ Pipeline completed with all quality checks passed")
        else:
            print("\n⚠️  Pipeline completed but quality checks failed")
        
        return result, validation_passed
