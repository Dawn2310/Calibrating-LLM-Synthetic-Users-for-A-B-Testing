import os
import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Config paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "experiment.db")
ANALYSIS_DIR = os.path.join(BASE_DIR, "analysis")
FIGURES_DIR = os.path.join(ANALYSIS_DIR, "figures")
TABLES_DIR = os.path.join(ANALYSIS_DIR, "tables")

# Ensure directories exist
os.makedirs(FIGURES_DIR, exist_ok=True)
os.makedirs(TABLES_DIR, exist_ok=True)

# Set visual style
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams['figure.figsize'] = (10, 6)

def load_data():
    conn = sqlite3.connect(DB_PATH)
    # Load api calls where status is completed and parsed_choice is A or B
    api_calls = pd.read_sql_query(
        "SELECT * FROM api_calls WHERE status='completed' AND parsed_choice IN ('A', 'B')", 
        conn
    )
    # Extract domain from test_id (e.g. 'UI-01' -> 'UI')
    api_calls['domain'] = api_calls['test_id'].apply(lambda x: x.split('-')[0])
    
    # Map domain names
    domain_map = {'UI': 'UI/UX', 'COPY': 'Copywriting', 'REC': 'Recommendation'}
    api_calls['domain'] = api_calls['domain'].map(lambda x: domain_map.get(x, x))
    
    # Ensure categorical order for persona
    api_calls['persona_type'] = pd.Categorical(
        api_calls['persona_type'], 
        categories=['demographic', 'biographical', 'interview'], 
        ordered=True
    )
    
    # Load position bias where choice is A or B
    pb = pd.read_sql_query(
        "SELECT * FROM position_bias WHERE choice IN ('A', 'B')", 
        conn
    )
    conn.close()
    return api_calls, pb

def analyze_position_bias(pb):
    print("Analyzing Position Bias...")
    
    # 1. Overall A/B choice distribution per model per order
    agg_pb = pb.groupby(['model', 'ab_order', 'choice']).size().unstack(fill_value=0)
    agg_pb['total'] = agg_pb['A'] + agg_pb['B']
    agg_pb['A_pct'] = agg_pb['A'] / agg_pb['total'] * 100
    agg_pb['B_pct'] = agg_pb['B'] / agg_pb['total'] * 100
    
    agg_pb.to_csv(os.path.join(TABLES_DIR, "position_bias_summary.csv"))
    
    # Visualization: A/B Selection Rate by Model and Order
    agg_pb_reset = agg_pb.reset_index()
    
    plt.figure(figsize=(12, 6))
    sns.barplot(data=agg_pb_reset, x='model', y='A_pct', hue='ab_order', palette='Set2')
    plt.title("Percentage of 'A' Choices by Model and Prompt Order (Position Bias Phase)", fontsize=14)
    plt.ylabel("Percentage of 'A' Choices (%)")
    plt.axhline(50, color='red', linestyle='--', label='50% Random Guessing')
    plt.legend(title="Order")
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "position_bias_A_selection_rate.png"))
    plt.close()
    
    # 2. Swap Consistency
    # We need to match the original vs swapped for the same test_id, model, and run_number
    pb_orig = pb[pb['ab_order'] == 'original'].set_index(['test_id', 'model', 'run_number'])
    pb_swap = pb[pb['ab_order'] == 'swapped'].set_index(['test_id', 'model', 'run_number'])
    
    joined = pb_orig.join(pb_swap, lsuffix='_orig', rsuffix='_swap', how='inner')
    # Consistent if Choice in orig == Choice in swap (meaning it picked the exact same variant, regardless of position)
    # Wait: if choice is 'A' in original, and 'B' in swapped -> it picked the same underlying variant.
    # So "Consistent" means choice_orig != choice_swap!
    joined['consistent_variant'] = joined['choice_orig'] != joined['choice_swap']
    joined['consistent_position'] = joined['choice_orig'] == joined['choice_swap']
    
    consistency = joined.groupby('model').agg(
        total_pairs=('consistent_variant', 'count'),
        consistent_variant=('consistent_variant', 'sum'),
        consistent_position=('consistent_position', 'sum')
    )
    consistency['variant_consistency_pct'] = consistency['consistent_variant'] / consistency['total_pairs'] * 100
    consistency['position_consistency_pct'] = consistency['consistent_position'] / consistency['total_pairs'] * 100
    
    consistency.to_csv(os.path.join(TABLES_DIR, "position_bias_consistency.csv"))

def analyze_persona_richness(df):
    print("Analyzing Persona Richness Effect...")
    
    # Calculate choice distribution
    agg = df.groupby(['persona_type', 'model', 'parsed_choice']).size().unstack(fill_value=0)
    agg['total'] = agg['A'] + agg['B']
    agg['A_pct'] = agg['A'] / agg['total'] * 100
    
    agg.to_csv(os.path.join(TABLES_DIR, "persona_richness_summary.csv"))
    
    agg_reset = agg.reset_index()
    
    # Visualization: Preference Shift across Persona Types
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=agg_reset, x='persona_type', y='A_pct', hue='model', marker='o', linewidth=2.5, markersize=8)
    plt.title("Percentage of 'A' Choices across Persona Richness Levels", fontsize=14)
    plt.ylabel("Percentage of 'A' Choices (%)")
    plt.xlabel("Persona Type (Richness)")
    plt.axhline(50, color='gray', linestyle='--')
    plt.ylim(40, 70)
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "persona_richness_shift.png"))
    plt.close()

def analyze_model_agreement(df):
    print("Analyzing Model Agreement...")
    
    # Pivot so each row is a unique trial (test_id, persona_id, ab_order, run_number)
    # and columns are models with their choice as values.
    pivot = df.pivot_table(
        index=['test_id', 'persona_id', 'persona_type', 'ab_order', 'run_number'],
        columns='model',
        values='parsed_choice',
        aggfunc='first'
    ).dropna()
    
    models = pivot.columns.tolist()
    if len(models) < 2:
        print("Not enough models for agreement analysis.")
        return
    
    # Calculate pairwise agreement percentage overall
    agreement_matrix = pd.DataFrame(index=models, columns=models, dtype=float)
    for m1 in models:
        for m2 in models:
            if m1 == m2:
                agreement_matrix.loc[m1, m2] = 100.0
            else:
                matches = (pivot[m1] == pivot[m2]).sum()
                agreement_matrix.loc[m1, m2] = (matches / len(pivot)) * 100.0
                
    agreement_matrix.to_csv(os.path.join(TABLES_DIR, "model_agreement_overall.csv"))
    
    # Visualization: Heatmap
    plt.figure(figsize=(8, 6))
    sns.heatmap(agreement_matrix, annot=True, cmap="YlGnBu", fmt=".1f", cbar_kws={'label': 'Agreement (%)'})
    plt.title("Overall Pairwise Model Agreement (%)", fontsize=14)
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "model_agreement_heatmap.png"))
    plt.close()
    
    # Agreement by Persona Type (All models agree)
    if len(models) >= 2:
        pivot['all_agree'] = pivot[models].apply(lambda x: x.nunique() == 1, axis=1)
        
        agreement_by_persona = pivot.groupby('persona_type')['all_agree'].mean() * 100
        agreement_by_persona.to_csv(os.path.join(TABLES_DIR, "model_agreement_by_persona.csv"))
        
        plt.figure(figsize=(8, 5))
        sns.barplot(x=agreement_by_persona.index, y=agreement_by_persona.values, palette='viridis')
        plt.title(f"Full Consensus Rate (All {len(models)} Models Agree) by Persona Richness", fontsize=14)
        plt.ylabel("Consensus Rate (%)")
        plt.xlabel("Persona Type")
        plt.ylim(0, 100)
        plt.tight_layout()
        plt.savefig(os.path.join(FIGURES_DIR, "model_consensus_by_persona.png"))
        plt.close()

def analyze_domain_breakdown(df):
    print("Analyzing Domain Breakdown...")
    
    agg = df.groupby(['domain', 'model', 'parsed_choice']).size().unstack(fill_value=0)
    agg['total'] = agg['A'] + agg['B']
    agg['A_pct'] = agg['A'] / agg['total'] * 100
    
    agg.to_csv(os.path.join(TABLES_DIR, "domain_breakdown_summary.csv"))
    
    agg_reset = agg.reset_index()
    
    plt.figure(figsize=(12, 6))
    sns.barplot(data=agg_reset, x='domain', y='A_pct', hue='model', palette='pastel')
    plt.title("Percentage of 'A' Choices by Domain and Model", fontsize=14)
    plt.ylabel("Percentage of 'A' Choices (%)")
    plt.xlabel("Test Domain")
    plt.axhline(50, color='gray', linestyle='--')
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "domain_breakdown.png"))
    plt.close()

def main():
    print("Loading data...")
    df, pb = load_data()
    
    if len(pb) > 0:
        analyze_position_bias(pb)
        
    if len(df) > 0:
        analyze_persona_richness(df)
        analyze_model_agreement(df)
        analyze_domain_breakdown(df)
        
    print(f"Analysis complete! Results saved in {ANALYSIS_DIR}")

if __name__ == "__main__":
    main()
