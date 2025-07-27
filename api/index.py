import pandas as pd
from datetime import datetime
import json

def generate_med_to_rec_report(df):
    """Your working Med to Rec logic"""
    ADULT_CUTOFF = 5
    
    required_columns = [
        'Brand', 'Product Type', 'Subtype', 'Product Name', 'Amount',
        'Unit of Measure', 'Location', 'Available', 'Unit Cost', 'Total Cost'
    ]
    
    df = df[required_columns].copy()
    
    # Build composite key
    df['Key'] = (
        df['Brand'] + '|' + df['Product Type'] + '|' +
        df['Subtype'].fillna('') + '|' + df['Product Name'] + '|' +
        df['Amount'].astype(str) + df['Unit of Measure']
    )
    
    # Split by location
    med = df[df['Location'] == "LIVE MEDICAL PRODUCTS"].copy()
    adult = df[df['Location'] == "A. LIVE ADULT USE PRODUCTS"]
    
    if len(med) == 0:
        return pd.DataFrame(columns=required_columns + ['Adult_Available'])
    
    # Calculate adult-use counts per SKU
    adult_counts = adult.groupby('Key')['Available'].sum().rename('Adult_Available')
    med = med.merge(adult_counts, on='Key', how='left').fillna({'Adult_Available': 0})
    
    # Filter to items where adult-use ≤ 5 units
    report = med[med['Adult_Available'] <= ADULT_CUTOFF].copy()
    report = report.drop(columns='Key')
    report = report.sort_values(['Product Type', 'Brand', 'Product Name'])
    
    # Format currency
    report['Unit Cost'] = report['Unit Cost'].apply(lambda x: f"${x:.2f}")
    report['Total Cost'] = report['Total Cost'].apply(lambda x: f"${x:.2f}")
    
    # Add totals row
    if len(report) > 0:
        tot_avail = report['Available'].sum()
        tot_cost = report['Total Cost'].str.replace('[,$]', '', regex=True).astype(float).sum()
        total_row = {
            'Brand': 'TOTAL', 'Product Type': '', 'Subtype': '', 'Product Name': '',
            'Amount': '', 'Unit of Measure': '', 'Location': '',
            'Available': int(tot_avail), 'Unit Cost': '',
            'Total Cost': f"${tot_cost:,.2f}", 'Adult_Available': ''
        }
        report = pd.concat([report, pd.DataFrame([total_row])], ignore_index=True)
    
    return report

def handler(request):
    """Vercel serverless function handler"""
    
    # Handle GET request - API status
    if request.method == 'GET':
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'service': 'RIPT Med to Rec Report API',
                'status': 'active',
                'version': '1.0',
                'timestamp': datetime.now().isoformat(),
                'endpoints': {
                    'GET /api/': 'API status',
                    'POST /api/': 'Upload CSV for Med to Rec report'
                }
            })
        }
    
    # Handle POST request - process CSV
    if request.method == 'POST':
        try:
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'status': 'success',
                    'message': 'Med to Rec API is working! File upload functionality coming soon.',
                    'timestamp': datetime.now().isoformat()
                })
            }
        except Exception as e:
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': str(e)})
            }

# Vercel entry point
def lambda_handler(event, context):
    return handler(event)
