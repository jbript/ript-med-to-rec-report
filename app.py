from flask import Flask, request, jsonify
import pandas as pd
import io
from datetime import datetime
import os

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def med_to_rec_report():
    try:
        if request.method == 'GET':
            return jsonify({
                'service': 'RIPT Med to Rec Report',
                'status': 'active',
                'version': '1.0',
                'timestamp': datetime.now().isoformat()
            })
        
        if request.method == 'POST':
            if 'file' in request.files:
                file = request.files['file']
                df = pd.read_csv(file)
            else:
                return jsonify({'error': 'No file provided'}), 400
            
            report_data = generate_med_to_rec_report(df)
            
            result = {
                'status': 'success',
                'timestamp': datetime.now().isoformat(),
                'records_found': len(report_data),
                'data': report_data.to_dict('records')[:10]  # First 10 records
            }
            
            if len(report_data) > 0:
                result['total_units'] = int(report_data['Available'].sum())
            
            return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def generate_med_to_rec_report(df):
    ADULT_CUTOFF = 5
    
    required_columns = [
        'Brand', 'Product Type', 'Subtype', 'Product Name', 'Amount',
        'Unit of Measure', 'Location', 'Available', 'Unit Cost', 'Total Cost'
    ]
    
    df = df[required_columns].copy()
    
    df['Key'] = (
        df['Brand'].astype(str) + '|' + 
        df['Product Type'].astype(str) + '|' +
        df['Subtype'].fillna('').astype(str) + '|' + 
        df['Product Name'].astype(str) + '|' +
        df['Amount'].astype(str) + df['Unit of Measure'].astype(str)
    )
    
    med = df[df['Location'] == "LIVE MEDICAL PRODUCTS"].copy()
    adult = df[df['Location'] == "A. LIVE ADULT USE PRODUCTS"]
    
    if len(med) == 0:
        return pd.DataFrame(columns=required_columns + ['Adult_Available'])
    
    adult_counts = adult.groupby('Key')['Available'].sum().rename('Adult_Available')
    med = med.merge(adult_counts, on='Key', how='left').fillna({'Adult_Available': 0})
    
    report = med[med['Adult_Available'] <= ADULT_CUTOFF].copy()
    report = report.drop(columns='Key')
    report = report.sort_values(['Product Type', 'Brand', 'Product Name'])
    
    return report

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=True, host='0.0.0.0', port=port)