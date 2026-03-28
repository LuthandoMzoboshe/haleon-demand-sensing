> **Disclaimer:** This is an independent portfolio project for learning purposes. 
> It is not affiliated with, endorsed by, or representative of Haleon PLC. 
> Product names are used as realistic examples in a simulated business scenario.

# 🏥 Haleon Demand Sensing Pipeline

[![GitHub](https://img.shields.io/badge/GitHub-LuthandoMzoboshe-blue?logo=github)](https://github.com/LuthandoMzoboshe/haleon-demand-sensing)
[![Python](https://img.shields.io/badge/Python-3.10-blue.svg)](https://www.python.org/)
[![Data Quality](https://img.shields.io/badge/Quality%20Tests-6%2F6%20Passing-brightgreen.svg)]()
[![Airflow](https://img.shields.io/badge/Airflow-2.8.0-orange.svg)](https://airflow.apache.org/)

> **AI-Assisted Data Engineering Portfolio Project**  
> Predicting consumer healthcare product demand using external market signals

**Author:** Luthando Mzoboshe  
**Project Link:** [github.com/LuthandoMzoboshe/haleon-demand-sensing](https://github.com/LuthandoMzoboshe/haleon-demand-sensing)

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
