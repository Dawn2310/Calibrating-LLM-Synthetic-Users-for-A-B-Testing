import os
import sqlite3
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "experiment.db")

def main():
    conn = sqlite3.connect(DB_PATH)
    # Get all completed calls with valid choices
    df = pd.read_sql_query(
        "SELECT test_id, persona_id, model, parsed_choice FROM api_calls WHERE status='completed' AND parsed_choice IN ('A', 'B')", 
        conn
    )
    conn.close()
    
    if df.empty:
        print("No data found!")
        return

    df['choice_A'] = (df['parsed_choice'] == 'A').astype(int)
    
    # We want agreement across 4 models. 
    # For each test_id and persona_id, we have up to 4 models (and 3 runs each, but let's just take majority vote per model or all rows).
    # Since we want a single agreement score per test_id, let's look at cross-model agreement.
    
    # Calculate majority vote per (test_id, persona_id, model)
    votes = df.groupby(['test_id', 'persona_id', 'model'])['choice_A'].agg(
        lambda x: 1 if x.mean() > 0.5 else 0
    ).reset_index()
    
    # Pivot so columns are models
    pivot = votes.pivot_table(index=['test_id', 'persona_id'], columns='model', values='choice_A').dropna()
    models = pivot.columns.tolist()
    
    # Calculate % agreement (all models agree) per test_id
    pivot['all_agree'] = pivot[models].apply(lambda x: x.nunique() == 1, axis=1)
    
    # Calculate standard deviation of model means per test_id (lower std = higher agreement)
    agreement_by_test = pivot.groupby('test_id')['all_agree'].mean() * 100
    
    # Let's also look at the overall P(A) per test to see if it's heavily skewed
    p_a_by_test = df.groupby('test_id')['choice_A'].mean() * 100
    
    summary = pd.DataFrame({
        'Full_Consensus_Pct': agreement_by_test,
        'P_A_Pct': p_a_by_test
    }).sort_values('Full_Consensus_Pct', ascending=False)
    
    print("=== TEST CASE AGREEMENT RANKING ===")
    print(summary.to_string(float_format="%.1f"))
    
    # Select 5 tests
    top_2 = summary.head(2).index.tolist()
    bottom_2 = summary.tail(2).index.tolist()
    
    # middle 1
    mid_idx = len(summary) // 2
    middle_1 = summary.iloc[[mid_idx]].index.tolist()
    
    print("\n=== SELECTED TEST CASES FOR EXP 4 ===")
    print(f"Top 2 (Most Stable): {top_2}")
    print(f"Bottom 2 (Most Controversial): {bottom_2}")
    print(f"Middle 1 (Average): {middle_1}")
    
if __name__ == "__main__":
    main()
