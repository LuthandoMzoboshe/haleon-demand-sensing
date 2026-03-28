"""
Configuration settings for the pipeline
"""
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
BRONZE_DIR = DATA_DIR / "bronze"
SILVER_DIR = DATA_DIR / "silver"
GOLD_DIR = DATA_DIR / "gold"

# Data files
RAW_FILES = {
    'sales': RAW_DIR / "haleon_sales_data.csv",
    'trends': RAW_DIR / "google_trends_data.csv",
    'weather': RAW_DIR / "weather_data.csv",
    'flu': RAW_DIR / "flu_surveillance_data.csv"
}

# Risk scoring weights
RISK_WEIGHTS = {
    'temperature_delta': 25,  # Max 25 points
    'trend_spike': 30,        # Max 30 points
    'flu_activity': 25,       # Max 25 points
    'sales_velocity': 20      # Max 20 points
}

# Risk thresholds
RISK_THRESHOLDS = {
    'CRITICAL': 70,   # >= 70 points
    'WARNING': 40,    # >= 40 points
    'NORMAL': 0       # < 40 points
}
