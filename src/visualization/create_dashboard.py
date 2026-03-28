"""
Interactive Dashboard Generator using Plotly
Creates HTML dashboard from gold layer data
"""
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from pathlib import Path

class DashboardGenerator:
    def __init__(self):
        self.data_file = Path('data/gold/demand_risk_analytics.parquet')
        self.output_file = Path('dashboards/haleon_dashboard.html')
        self.output_file.parent.mkdir(exist_ok=True)
        
    def load_data(self):
        """Load gold layer data"""
        df = pd.read_parquet(self.data_file)
        df['date'] = pd.to_datetime(df['date'])
        return df
    
    def create_kpi_cards(self, df):
        """Create KPI summary cards"""
        total_products = df['product_name'].nunique()
        avg_risk = df['demand_risk_score'].mean()
        high_risk = len(df[df['risk_category'].isin(['WARNING', 'CRITICAL'])])
        total_revenue = df['revenue'].sum()
        
        fig = go.Figure()
        
        fig.add_trace(go.Indicator(
            mode = "number",
            value = total_products,
            title = {"text": "Products Monitored"},
            domain = {'x': [0, 0.25], 'y': [0, 1]}
        ))
        
        fig.add_trace(go.Indicator(
            mode = "number",
            value = avg_risk,
            title = {"text": "Avg Risk Score"},
            number = {'suffix': "/100"},
            domain = {'x': [0.25, 0.5], 'y': [0, 1]}
        ))
        
        fig.add_trace(go.Indicator(
            mode = "number",
            value = high_risk,
            title = {"text": "High-Risk Alerts"},
            domain = {'x': [0.5, 0.75], 'y': [0, 1]}
        ))
        
        fig.add_trace(go.Indicator(
            mode = "number",
            value = total_revenue / 1000000,
            title = {"text": "Total Revenue"},
            number = {'prefix': "$", 'suffix': "M"},
            domain = {'x': [0.75, 1], 'y': [0, 1]}
        ))
        
        fig.update_layout(
            height=200,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        
        return fig
    
    def create_risk_heatmap(self, df):
        """Create risk heatmap by region and product"""
        pivot = df.groupby(['region', 'product_name'])['demand_risk_score'].mean().reset_index()
        pivot_table = pivot.pivot(index='region', columns='product_name', values='demand_risk_score')
        
        fig = go.Figure(data=go.Heatmap(
            z=pivot_table.values,
            x=pivot_table.columns,
            y=pivot_table.index,
            colorscale=[
                [0, 'green'],
                [0.4, 'yellow'],
                [0.7, 'orange'],
                [1, 'red']
            ],
            text=pivot_table.values.round(1),
            texttemplate='%{text}',
            textfont={"size": 10},
            colorbar=dict(title="Risk Score")
        ))
        
        fig.update_layout(
            title="Risk Heatmap: Region × Product",
            xaxis_title="Product",
            yaxis_title="Region",
            height=400
        )
        
        return fig
    
    def create_time_series(self, df):
        """Create risk score time series"""
        time_data = df.groupby(['date', 'product_category'])['demand_risk_score'].mean().reset_index()
        
        fig = px.line(
            time_data,
            x='date',
            y='demand_risk_score',
            color='product_category',
            title='Risk Score Trend Over Time',
            labels={'demand_risk_score': 'Avg Risk Score', 'date': 'Date'}
        )
        
        # Add horizontal lines for risk thresholds
        fig.add_hline(y=40, line_dash="dash", line_color="orange", 
                     annotation_text="WARNING Threshold")
        fig.add_hline(y=70, line_dash="dash", line_color="red", 
                     annotation_text="CRITICAL Threshold")
        
        fig.update_layout(height=400)
        
        return fig
    
    def create_risk_decomposition(self, df):
        """Create stacked bar chart of risk components"""
        risk_components = df.groupby('product_name')[
            ['temp_risk', 'trend_risk', 'flu_risk', 'velocity_risk']
        ].mean().reset_index()
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='Temperature Risk',
            x=risk_components['product_name'],
            y=risk_components['temp_risk'],
            marker_color='lightblue'
        ))
        
        fig.add_trace(go.Bar(
            name='Trend Risk',
            x=risk_components['product_name'],
            y=risk_components['trend_risk'],
            marker_color='lightcoral'
        ))
        
        fig.add_trace(go.Bar(
            name='Flu Risk',
            x=risk_components['product_name'],
            y=risk_components['flu_risk'],
            marker_color='lightgreen'
        ))
        
        fig.add_trace(go.Bar(
            name='Sales Velocity Risk',
            x=risk_components['product_name'],
            y=risk_components['velocity_risk'],
            marker_color='lightyellow'
        ))
        
        fig.update_layout(
            barmode='stack',
            title='Risk Score Decomposition by Product',
            xaxis_title='Product',
            yaxis_title='Risk Points',
            height=400
        )
        
        return fig
    
    def create_regional_comparison(self, df):
        """Create regional risk comparison"""
        regional = df.groupby('region').agg({
            'demand_risk_score': 'mean',
            'revenue': 'sum',
            'units_sold': 'sum'
        }).reset_index()
        
        regional = regional.sort_values('demand_risk_score', ascending=False)
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=regional['region'],
            y=regional['demand_risk_score'],
            marker_color=['red' if x >= 40 else 'green' for x in regional['demand_risk_score']],
            text=regional['demand_risk_score'].round(1),
            textposition='outside'
        ))
        
        fig.update_layout(
            title='Average Risk Score by Region',
            xaxis_title='Region',
            yaxis_title='Risk Score',
            height=400
        )
        
        return fig
    
    def create_alert_table(self, df):
        """Create table of high-risk products"""
        alerts = df[df['risk_category'].isin(['WARNING', 'CRITICAL'])].copy()
        alerts = alerts.nlargest(10, 'demand_risk_score')
        
        fig = go.Figure(data=[go.Table(
            header=dict(
                values=['Date', 'Region', 'Product', 'Risk Score', 'Category', 'Recommendation'],
                fill_color='paleturquoise',
                align='left'
            ),
            cells=dict(
                values=[
                    alerts['date'].dt.strftime('%Y-%m-%d'),
                    alerts['region'],
                    alerts['product_name'],
                    alerts['demand_risk_score'].round(1),
                    alerts['risk_category'],
                    alerts['action_recommendation']
                ],
                fill_color=[['white' if cat == 'WARNING' else 'lightcoral' 
                           for cat in alerts['risk_category']]],
                align='left'
            )
        )])
        
        fig.update_layout(
            title='Top 10 High-Risk Alerts',
            height=400
        )
        
        return fig
    
    def create_full_dashboard(self):
        """Generate complete HTML dashboard"""
        print("🎨 Generating interactive dashboard...")
        
        df = self.load_data()
        
        # Create all visualizations
        kpi_fig = self.create_kpi_cards(df)
        heatmap_fig = self.create_risk_heatmap(df)
        timeseries_fig = self.create_time_series(df)
        decomp_fig = self.create_risk_decomposition(df)
        regional_fig = self.create_regional_comparison(df)
        table_fig = self.create_alert_table(df)
        
        # Combine into single HTML
        with open(self.output_file, 'w') as f:
            f.write('''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Haleon Demand Sensing Dashboard</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 2.5em;
        }
        .header p {
            margin: 10px 0 0 0;
            opacity: 0.9;
        }
        .chart-container {
            background: white;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .footer {
            text-align: center;
            padding: 20px;
            color: #666;
            font-size: 0.9em;
        }
        .footer a {
            color: #667eea;
            text-decoration: none;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🏥 Haleon Demand Sensing Dashboard</h1>
        <p>Real-time risk monitoring for consumer healthcare products</p>
        <p style="font-size: 0.9em;">Built with Python • Airflow • External APIs</p>
    </div>
''')
            
            # Write each chart
            f.write('<div class="chart-container">')
            f.write(kpi_fig.to_html(include_plotlyjs='cdn', full_html=False))
            f.write('</div>')
            
            f.write('<div class="chart-container">')
            f.write(heatmap_fig.to_html(include_plotlyjs=False, full_html=False))
            f.write('</div>')
            
            f.write('<div class="chart-container">')
            f.write(timeseries_fig.to_html(include_plotlyjs=False, full_html=False))
            f.write('</div>')
            
            f.write('<div class="chart-container">')
            f.write(decomp_fig.to_html(include_plotlyjs=False, full_html=False))
            f.write('</div>')
            
            f.write('<div class="chart-container">')
            f.write(regional_fig.to_html(include_plotlyjs=False, full_html=False))
            f.write('</div>')
            
            f.write('<div class="chart-container">')
            f.write(table_fig.to_html(include_plotlyjs=False, full_html=False))
            f.write('</div>')
            
            f.write('''
    <div class="footer">
        <p>📊 Dashboard generated from 13,140 data points</p>
        <p>🔗 <a href="https://github.com/LuthandoMzoboshe/haleon-demand-sensing" target="_blank">View Source Code on GitHub</a></p>
        <p>👤 Created by Luthando Mzoboshe</p>
    </div>
</body>
</html>
''')
        
        print(f"✅ Dashboard created: {self.output_file}")
        print(f"🌐 Open in browser: file://{self.output_file.absolute()}")
        
        return self.output_file

if __name__ == "__main__":
    generator = DashboardGenerator()
    generator.create_full_dashboard()
