import pandas as pd
import sys
from datetime import datetime

ADULT_CUTOFF = 5  # ≤ 5 units triggers the alert

def generate_report(input_csv, output_xlsx=None):
    """Generate Med to Rec Report - exact replica of ChatGPT version"""
    
    df = pd.read_csv(input_csv, usecols=[
        'Brand', 'Product Type', 'Subtype', 'Product Name', 'Amount',
        'Unit of Measure', 'Location', 'Available', 'Unit Cost', 'Total Cost'
    ])
    
    # Build a unique key for matching SKUs across locations
    df['Key'] = (
        df['Brand'] + '|' + df['Product Type'] + '|' +
        df['Subtype'].fillna('') + '|' + df['Product Name'] + '|' +
        df['Amount'].astype(str) + df['Unit of Measure']
    )
    
    # Split by location
    med = df[df['Location'] == "LIVE MEDICAL PRODUCTS"].copy()
    adult = df[df['Location'] == "A. LIVE ADULT USE PRODUCTS"]
    
    # Adult-use counts per SKU
    adult_counts = (
        adult.groupby('Key')['Available']
        .sum()
        .rename('Adult_Available')
    )
    
    # Merge onto medical rows
    med = med.merge(adult_counts, on='Key', how='left').fillna({'Adult_Available': 0})
    
    # Filter -- adult-use ≤ 5
    report = med[med['Adult_Available'] <= ADULT_CUTOFF].copy()
    
    # Cleanup & formatting
    report.drop(columns='Key', inplace=True)
    report.sort_values(['Product Type', 'Brand', 'Product Name'], inplace=True)
    report['Unit Cost'] = report['Unit Cost'].apply(lambda x: f"${x:.2f}")
    report['Total Cost'] = report['Total Cost'].apply(lambda x: f"${x:.2f}")
    
    # Totals row
    tot_avail = report['Available'].sum()
    tot_cost = (
        report['Total Cost'].str.replace('[,$]', '', regex=True).astype(float).sum()
    )
    total_row = {
        'Brand': 'TOTAL', 'Product Type': '', 'Subtype': '', 'Product Name': '',
        'Amount': '', 'Unit of Measure': '', 'Location': '',
        'Available': int(tot_avail), 'Unit Cost': '',
        'Total Cost': f"${tot_cost:,.2f}", 'Adult_Available': ''
    }
    report = pd.concat([report, pd.DataFrame([total_row])], ignore_index=True)
    
    if output_xlsx:
        report.to_excel(output_xlsx, index=False)
        print(f"📁 Report exported to: {output_xlsx}")
    
    return report

def display_interactive_table(report):
    """Display the report in a nice interactive format"""
    
    if len(report) == 0:
        print("✅ No items need transfer - all medical products have >5 units in Adult Use")
        return
    
    print(f"\n{'='*80}")
    print(f"🌿 RIPT DISPENSARY - MED TO REC REPORT")
    print(f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}")
    
    # Summary stats (excluding totals row)
    data_rows = report[report['Brand'] != 'TOTAL']
    totals_row = report[report['Brand'] == 'TOTAL'].iloc[0] if len(report) > len(data_rows) else None
    
    print(f"\n📊 SUMMARY:")
    print(f"   • Items needing transfer: {len(data_rows)}")
    if totals_row is not None:
        print(f"   • Total units to transfer: {totals_row['Available']}")
        print(f"   • Total value: {totals_row['Total Cost']}")
    
    if len(data_rows) > 0:
        print(f"\n📋 DETAILED REPORT:")
        print(f"{'='*120}")
        
        # Header
        header = f"{'BRAND':<20} {'PRODUCT TYPE':<15} {'PRODUCT NAME':<40} {'MED UNITS':<10} {'ADULT UNITS':<12} {'TOTAL COST':<12}"
        print(header)
        print("─" * 120)
        
        # Data rows
        for _, row in data_rows.iterrows():
            product_name = str(row['Product Name'])[:38] + ".." if len(str(row['Product Name'])) > 40 else str(row['Product Name'])
            line = f"{str(row['Brand']):<20} {str(row['Product Type']):<15} {product_name:<40} {row['Available']:<10} {row['Adult_Available']:<12} {row['Total Cost']:<12}"
            print(line)
        
        # Totals row
        if totals_row is not None:
            print("─" * 120)
            print(f"{'TOTAL':<20} {'':<15} {'':<40} {totals_row['Available']:<10} {'':<12} {totals_row['Total Cost']:<12}")
        
        print("=" * 120)

def main():
    """Main execution function"""
    
    if len(sys.argv) < 2:
        print("🌿 RIPT Med to Rec Report Generator")
        print("Usage: python3 complete_med_to_rec.py <treez_inventory_file.csv> [output.xlsx]")
        print("\nExamples:")
        print("  python3 complete_med_to_rec.py inventory.csv")
        print("  python3 complete_med_to_rec.py inventory.csv med_to_rec_report.xlsx")
        return
    
    input_csv = sys.argv[1]
    output_xlsx = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        print(f"🔄 Processing: {input_csv}")
        report = generate_report(input_csv, output_xlsx)
        
        # Display interactive table
        display_interactive_table(report)
        
        # Options menu
        print(f"\n🔧 OPTIONS:")
        print(f"1. Export to Excel: python3 complete_med_to_rec.py {input_csv} med_to_rec_report.xlsx")
        print(f"2. View raw data: print(report.to_string())")
        print(f"3. Push to Google Sheets: [Coming soon]")
        
        print(f"\n✅ Report complete!")
        
    except FileNotFoundError:
        print(f"❌ Error: File '{input_csv}' not found")
        print("Make sure the file path is correct and the file exists")
    except KeyError as e:
        print(f"❌ Error: Missing required column {e}")
        print("Make sure this is a Treez inventory valuation CSV with all required columns")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()