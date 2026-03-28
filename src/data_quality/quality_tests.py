"""
Data Quality Validation using Great Expectations
"""
import great_expectations as gx
from great_expectations.core.batch import RuntimeBatchRequest
import pandas as pd
from pathlib import Path

class DataQualityValidator:
    def __init__(self):
        self.context = gx.get_context()
        self.gold_file = Path("data/gold/demand_risk_analytics.parquet")
    
    def validate_gold_layer(self):
        """Run quality checks on gold layer data"""
        print("=" * 70)
        print("🔍 DATA QUALITY VALIDATION")
        print("=" * 70)
        
        df = pd.read_parquet(self.gold_file)
        print(f"\n📊 Validating {len(df):,} records...")
        
        # Simple validation checks
        checks_passed = 0
        checks_failed = 0
        
        # Check 1: No null risk scores
        if df['demand_risk_score'].isnull().sum() == 0:
            print("✅ Risk scores: No nulls")
            checks_passed += 1
        else:
            print("❌ Risk scores: Contains nulls")
            checks_failed += 1
        
        # Check 2: Risk score range
        if (df['demand_risk_score'] >= 0).all() and (df['demand_risk_score'] <= 100).all():
            print("✅ Risk scores: Valid range (0-100)")
            checks_passed += 1
        else:
            print("❌ Risk scores: Out of range")
            checks_failed += 1
        
        # Check 3: Valid categories
        valid_categories = ['NORMAL', 'WARNING', 'CRITICAL']
        if df['risk_category'].isin(valid_categories).all():
            print("✅ Risk categories: Valid")
            checks_passed += 1
        else:
            print("❌ Risk categories: Invalid values")
            checks_failed += 1
        
        # Check 4: Valid products
        valid_products = ['Theraflu', 'Panadol', 'Otrivin', 'Sensodyne', 'Advil', 'Centrum']
        if df['product_name'].isin(valid_products).all():
            print("✅ Product names: Valid")
            checks_passed += 1
        else:
            print("❌ Product names: Invalid values")
            checks_failed += 1
        
        # Check 5: Positive revenue
        if (df['revenue'] > 0).all():
            print("✅ Revenue: All positive")
            checks_passed += 1
        else:
            print("❌ Revenue: Contains non-positive values")
            checks_failed += 1
        
        # Check 6: Row count
        if 1000 <= len(df) <= 100000:
            print(f"✅ Row count: {len(df):,} (within expected range)")
            checks_passed += 1
        else:
            print(f"❌ Row count: {len(df):,} (outside expected range)")
            checks_failed += 1
        
        print("\n" + "=" * 70)
        print("📊 VALIDATION SUMMARY")
        print("=" * 70)
        print(f"✅ Passed: {checks_passed}")
        print(f"❌ Failed: {checks_failed}")
        print(f"Total: {checks_passed + checks_failed}")
        
        if checks_failed == 0:
            print("\n🎉 ALL QUALITY CHECKS PASSED!")
        else:
            print("\n⚠️  SOME CHECKS FAILED - REVIEW DATA")
        
        return checks_failed == 0

if __name__ == "__main__":
    validator = DataQualityValidator()
    validator.validate_gold_layer()