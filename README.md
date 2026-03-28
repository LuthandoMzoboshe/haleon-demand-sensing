# 🏥 Haleon Demand Sensing Pipeline

Predicting consumer healthcare product demand using external market signals.

## Problem Statement
Consumer healthcare products experience unpredictable demand spikes driven by weather changes, flu outbreaks, and search trends. Stockouts cost millions; overstocking leads to waste.

## Solution
Automated pipeline calculating real-time Demand Risk Score using:
- Google Trends (search behavior)
- Weather API (temperature drops)
- Flu surveillance data
- Historical sales data

## Tech Stack
- Python 3.10, Pandas, NumPy
- Parquet format (Medallion Architecture)
- Great Expectations (data quality)
- Open-Meteo, pytrends (external APIs)

## Results
- 13,140 records processed
- 6/6 quality checks passing
- Risk scores calculated per product/region

## Quick Start
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python src/transformation/data_transformer.py
python src/data_quality/quality_tests.py
