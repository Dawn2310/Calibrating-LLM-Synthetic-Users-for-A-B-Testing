import os
import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Setup paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "experiment.db")
DATA_DIR = os.path.join(BASE_DIR, "data")
FIGURES_DIR = os.path.join(BASE_DIR, "analysis", "figures")
os.makedirs(FIGURES_DIR, exist_ok=True)

sns.set_theme(style="whitegrid")

def load_and_clean_data():
    print("--- TASK 1: Data Parsing & Cleaning ---")
    conn = sqlite3.connect(DB_PATH)
    
    # 1. Load Position Bias Data (B1)
    pb_df = pd.read_sql_query(
        "SELECT test_id, model, run_number, ab_order, choice as true_variant_chosen FROM position_bias WHERE choice IN ('A', 'B')", 
        conn
    )
    pb_df['persona_level'] = 'B1'
    pb_df['persona_id'] = 'None'
    
    # 2. Load API Calls Data (B3, B4, B5)
    ac_df = pd.read_sql_query(
        "SELECT test_id, model, run_number, ab_order, persona_id, persona_type, parsed_choice as true_variant_chosen FROM api_calls WHERE status='completed' AND parsed_choice IN ('A', 'B')", 
        conn
    )
    
    level_map = {
        'demographic': 'B3',
        'biographical': 'B4',
        'interview': 'B5'
    }
    ac_df['persona_level'] = ac_df['persona_type'].map(level_map)
    ac_df = ac_df.drop(columns=['persona_type'])
    
    # Merge datasets
    df = pd.concat([pb_df, ac_df], ignore_index=True)
    
    # 3. Determine Option 1 and Option Selected By LLM
    # If original, Option 1 is A. If swapped, Option 1 is B.
    df['Option_1_is'] = np.where(df['ab_order'] == 'original', 'Variant_A', 'Variant_B')
    
    # LLM picked Option 1 if it picked A in original, or B in swapped.
    picked_option_1 = ((df['ab_order'] == 'original') & (df['true_variant_chosen'] == 'A')) | \
                      ((df['ab_order'] == 'swapped') & (df['true_variant_chosen'] == 'B'))
                      
    df['option_selected_by_llm'] = np.where(picked_option_1, 'Option_1', 'Option_2')
    df['chose_option_1'] = picked_option_1.astype(int)
    
    # Reorder columns
    cols = ['test_id', 'model', 'persona_level', 'persona_id', 'run_number', 'ab_order', 'Option_1_is', 'option_selected_by_llm', 'true_variant_chosen', 'chose_option_1']
    df = df[cols]
    
    out_path = os.path.join(DATA_DIR, "cleaned_master_dataset.csv")
    df.to_csv(out_path, index=False)
    print(f"Cleaned dataset saved to {out_path} ({len(df)} rows)")
    
    return df

def calc_gap1_floor(df):
    print("\n--- TASK 2: B1 Calibration Floor (Gap 1: Position Bias) ---")
    b1_df = df[df['persona_level'] == 'B1']
    
    # % of times Option 1 was selected
    bias_stats = b1_df.groupby('model')['chose_option_1'].mean() * 100
    
    print("Percentage of selecting Option 1 (regardless of Variant) with No Persona:")
    for model, pct in bias_stats.items():
        print(f"  - {model}: {pct:.2f}%")
        if pct > 60:
            print(f"    => {model} has SEVERE Position Bias (>60%).")
        elif pct > 50:
            print(f"    => {model} has slight Position Bias.")
            
    # Visualize B1 Bias
    plt.figure(figsize=(8, 5))
    ax = sns.barplot(x=bias_stats.index, y=bias_stats.values, hue=bias_stats.index, palette='Reds', legend=False)
    plt.axhline(50, color='gray', linestyle='--', label='50% Ideal (No bias)')
    plt.axhline(60, color='red', linestyle='-.', label='60% Severe Bias Threshold')
    plt.title("B1 Calibration Floor (Option 1 Selection Rate) - Position Bias", fontsize=14)
    plt.ylabel("Option 1 Selection Rate (%)")
    plt.ylim(0, 100)
    
    for container in ax.containers:
        ax.bar_label(container, fmt='%.1f%%', padding=3)
        
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "Gap1_Position_Bias_Floor.png"))
    plt.close()

def calc_gap3_ceiling(df):
    print("\n--- TASK 3: B2 Local Consistency Ceiling (Gap 3: AI Drift) ---")
    b1_df = df[df['persona_level'] == 'B1']
    
    # Intra-agreement is calculated across the 25 runs.
    # Group by test_id, model, ab_order
    # Count frequency of the dominant choice, divide by total runs in that group.
    
    def intra_agreement(group):
        mode_count = group['true_variant_chosen'].value_counts().max()
        return mode_count / len(group)
    
    agreements = b1_df.groupby(['test_id', 'model', 'ab_order']).apply(intra_agreement).reset_index(name='intra_agreement')
    
    # Average intra-agreement per model
    ceiling_stats = agreements.groupby('model')['intra_agreement'].mean() * 100
    
    print("Internal Consensus Rate (Intra-agreement) from repeated runs:")
    for model, pct in ceiling_stats.items():
        print(f"  - {model}: {pct:.2f}%")
        print(f"    => Even on the same test case, {model} contradicts itself {100-pct:.2f}% of the time.")
        
    plt.figure(figsize=(8, 5))
    ax = sns.barplot(x=ceiling_stats.index, y=ceiling_stats.values, hue=ceiling_stats.index, palette='Blues', legend=False)
    plt.title("B2 Local Consistency Ceiling (Intra-agreement)", fontsize=14)
    plt.ylabel("Internal Consistency (%)")
    plt.ylim(0, 100)
    for container in ax.containers:
        ax.bar_label(container, fmt='%.1f%%', padding=3)
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "Gap3_Intra_Agreement_Ceiling.png"))
    plt.close()

def calc_gap2_convergence(df):
    print("\n--- TASK 4: Analyze B3 -> B4 -> B5 Convergence (Gap 2) ---")
    levels = ['B3', 'B4', 'B5']
    target_df = df[df['persona_level'].isin(levels)]
    
    # 1. Position Bias Drop
    print("1. Position Bias Drop:")
    bias_drop = target_df.groupby(['persona_level', 'model'])['chose_option_1'].mean() * 100
    bias_drop_df = bias_drop.reset_index()
    
    plt.figure(figsize=(10, 5))
    sns.lineplot(data=bias_drop_df, x='persona_level', y='chose_option_1', hue='model', marker='o', linewidth=2.5, markersize=8)
    plt.axhline(50, color='gray', linestyle='--', label='Ideal')
    plt.title("Position Bias Drop Across Persona Levels", fontsize=14)
    plt.ylabel("Option 1 Selection Rate (%)")
    plt.xlabel("Persona Depth Level")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "Gap2_Position_Bias_Drop.png"))
    plt.close()
    
    # 2. Consensus Increase
    print("2. Consensus Rate Growth Across All Models:")
    # Pivot to get models as columns
    pivot = target_df.pivot_table(
        index=['test_id', 'persona_id', 'persona_level', 'ab_order'],
        columns='model',
        values='true_variant_chosen',
        aggfunc='first'
    ).dropna()
    
    # All models agree
    models = pivot.columns.tolist()
    pivot['all_agree'] = pivot[models].apply(lambda x: x.nunique() == 1, axis=1)
    
    consensus_rate = pivot.groupby('persona_level')['all_agree'].mean() * 100
    
    for lvl in levels:
        if lvl in consensus_rate:
            print(f"  - {lvl}: {consensus_rate[lvl]:.2f}% full consensus.")
            
    plt.figure(figsize=(8, 5))
    ax = sns.barplot(x=consensus_rate.index, y=consensus_rate.values, hue=consensus_rate.index, palette='Purples', legend=False)
    plt.title(f"Convergence Rate (Full Consensus) of All {len(models)} Models", fontsize=14)
    plt.ylabel("Full Consensus Rate (%)")
    plt.xlabel("Persona Depth Level")
    plt.ylim(0, 100)
    for container in ax.containers:
        ax.bar_label(container, fmt='%.1f%%', padding=3)
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "Gap2_Convergence_Consensus.png"))
    plt.close()

def main():
    df = load_and_clean_data()
    calc_gap1_floor(df)
    calc_gap3_ceiling(df)
    calc_gap2_convergence(df)
    print("\n=> All tasks executed successfully! Check 'analysis/figures/' for visual evidence.")

if __name__ == "__main__":
    main()
