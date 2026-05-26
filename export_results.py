import os
import sqlite3
import csv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'data', 'experiment.db')
OUTPUT_DIR = os.path.join(BASE_DIR, 'data')

def main():
    if not os.path.exists(DB_PATH):
        print(f"Error: Database file not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get list of tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall() if not row[0].startswith('sqlite_')]
    
    print("=" * 60)
    print("      EXPERIMENT RESULTS EXPORTER & SUMMARY STATISTICS")
    print("=" * 60)
    print(f"Database: {os.path.abspath(DB_PATH)}")
    print(f"Tables found: {', '.join(tables)}")
    print("-" * 60)

    # 1. Print Summary Statistics
    # API Calls overview
    if 'api_calls' in tables:
        cursor.execute("SELECT COUNT(*), status FROM api_calls GROUP BY status")
        status_counts = cursor.fetchall()
        print("\n[api_calls] Status Summary:")
        for count, status in status_counts:
            print(f"  - {status.upper()}: {count} rows")

        cursor.execute("""
            SELECT model, 
                   COUNT(*) as total,
                   SUM(CASE WHEN parsed_choice = 'A' THEN 1 ELSE 0 END) as count_A,
                   SUM(CASE WHEN parsed_choice = 'B' THEN 1 ELSE 0 END) as count_B,
                   SUM(CASE WHEN parsed_choice = 'INVALID' THEN 1 ELSE 0 END) as count_invalid,
                   ROUND(AVG(response_time_ms) / 1000.0, 2) as avg_time_sec,
                   SUM(prompt_tokens + completion_tokens) as total_tokens
            FROM api_calls 
            WHERE status = 'completed'
            GROUP BY model
        """)
        model_stats = cursor.fetchall()
        print("\n[api_calls] Model Preferences & Stats (Completed Runs):")
        for row in model_stats:
            model, total, a, b, inv, avg_t, tokens = row
            pct_a = (a / (a + b)) * 100 if (a + b) > 0 else 0
            pct_b = (b / (a + b)) * 100 if (a + b) > 0 else 0
            print(f"  * Model: {model}")
            print(f"    - Total completed: {total}")
            print(f"    - Choice A: {a} ({pct_a:.1f}%) | Choice B: {b} ({pct_b:.1f}%) | Invalid: {inv}")
            print(f"    - Avg Response Time: {avg_t} seconds")
            print(f"    - Total Tokens Used: {tokens:,}")
            print()

        # Breakdown by persona_type
        cursor.execute("""
            SELECT persona_type, model, 
                   COUNT(*) as total,
                   SUM(CASE WHEN parsed_choice = 'A' THEN 1 ELSE 0 END) as count_A,
                   SUM(CASE WHEN parsed_choice = 'B' THEN 1 ELSE 0 END) as count_B
            FROM api_calls 
            WHERE status = 'completed'
            GROUP BY persona_type, model
            ORDER BY persona_type, model
        """)
        persona_stats = cursor.fetchall()
        print("\n[api_calls] Breakdown by Persona Type (Richness Gradient):")
        current_ptype = None
        for row in persona_stats:
            ptype, model, total, a, b = row
            if ptype != current_ptype:
                print(f"  [{ptype.upper()}]")
                current_ptype = ptype
            pct_a = (a / (a + b)) * 100 if (a + b) > 0 else 0
            print(f"    - {model}: Total {total} | A: {a} ({pct_a:.1f}%) | B: {b}")
        print()

    # Position Bias overview
    if 'position_bias' in tables:
        cursor.execute("SELECT COUNT(*) FROM position_bias")
        pb_count = cursor.fetchone()[0]
        if pb_count > 0:
            print(f"\n[position_bias] Found {pb_count} records.")
            cursor.execute("""
                SELECT model, ab_order, 
                       SUM(CASE WHEN choice = 'A' THEN 1 ELSE 0 END) as count_A,
                       SUM(CASE WHEN choice = 'B' THEN 1 ELSE 0 END) as count_B
                FROM position_bias
                GROUP BY model, ab_order
            """)
            for row in cursor.fetchall():
                model, order, a, b = row
                print(f"  * {model} ({order}): Choice A = {a}, Choice B = {b}")

    # Human Responses overview
    if 'human_responses' in tables:
        cursor.execute("SELECT COUNT(*) FROM human_responses")
        hr_count = cursor.fetchone()[0]
        print(f"\n[human_responses] Found {hr_count} records.")

    print("-" * 60)
    print("Exporting tables to CSV...")

    # 2. Export each table to CSV
    csv_paths = {}
    for table in tables:
        cursor.execute(f"SELECT * FROM {table}")
        rows = cursor.fetchall()
        if not rows:
            print(f"  - Table {table} is empty. Skipping CSV export.")
            continue

        column_names = [description[0] for description in cursor.description]
        csv_file_path = os.path.join(OUTPUT_DIR, f"{table}.csv")
        
        with open(csv_file_path, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(column_names)
            writer.writerows(rows)
        
        print(f"  - Table '{table}' successfully exported to: {os.path.basename(csv_file_path)}")
        csv_paths[table] = csv_file_path

    # 3. Try to export to a nice Excel file with sheets if pandas is available
    try:
        import pandas as pd
        excel_path = os.path.join(OUTPUT_DIR, "experiment_results.xlsx")
        print("\nPandas detected! Creating multi-sheet Excel file...")
        
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            for table in tables:
                df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
                if not df.empty:
                    df.to_excel(writer, sheet_name=table, index=False)
                    print(f"  - Sheet '{table}' added to Excel.")
        print(f"\n[SUCCESS] Excel workbook successfully saved at: {os.path.abspath(excel_path)}")
        print("You can open this file directly in Microsoft Excel or Google Sheets!")
    except ImportError:
        print("\n[INFO] 'pandas' or 'openpyxl' not installed, skipped generating .xlsx workbook.")
        print("All data is fully exported in the CSV files listed above in the 'data' directory.")
        print("To generate a single Excel file next time, run: pip install pandas openpyxl")
    except Exception as e:
        print(f"\n[WARNING] Error writing Excel file: {e}")

    conn.close()
    print("=" * 60)

if __name__ == '__main__':
    main()
