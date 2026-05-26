import os
import sqlite3
import pandas as pd
import numpy as np
from sklearn.metrics import cohen_kappa_score
from statsmodels.stats.inter_rater import aggregate_raters, fleiss_kappa
import statsmodels.formula.api as smf
import krippendorff

# Config paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "experiment.db")
ANALYSIS_DIR = os.path.join(BASE_DIR, "analysis")
TABLES_DIR = os.path.join(ANALYSIS_DIR, "tables")

os.makedirs(TABLES_DIR, exist_ok=True)

def load_data():
    print("Loading data from database...")
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        "SELECT * FROM api_calls WHERE status='completed' AND parsed_choice IN ('A', 'B')", 
        conn
    )
    conn.close()
    
    # Map choice to binary (A = 1, B = 0)
    df['choice_A'] = (df['parsed_choice'] == 'A').astype(int)
    
    # Ensure categorical types
    df['persona_type'] = pd.Categorical(
        df['persona_type'], 
        categories=['demographic', 'biographical', 'interview'], 
        ordered=True
    )
    return df

def analyze_agreement(df):
    print("\n--- 1. Inter-rater Reliability (Model Agreement) ---")
    
    # Pivot so each row is a unique trial and columns are models with their choice (0 or 1)
    pivot = df.pivot_table(
        index=['test_id', 'persona_id', 'persona_type', 'ab_order', 'run_number'],
        columns='model',
        values='choice_A',
        aggfunc='first'
    ).dropna()
    
    models = pivot.columns.tolist()
    if len(models) < 2:
        print("Not enough models for agreement analysis.")
        return

    results = []

    # A. Cohen's Kappa (Pairwise)
    print("Pairwise Cohen's Kappa:")
    for i in range(len(models)):
        for j in range(i + 1, len(models)):
            m1 = models[i]
            m2 = models[j]
            kappa = cohen_kappa_score(pivot[m1], pivot[m2])
            print(f"  {m1} vs {m2}: {kappa:.4f}")
            results.append({"Metric": "Cohen's Kappa", "Comparison": f"{m1} vs {m2}", "Value": kappa})

    # B. Fleiss' Kappa (Overall)
    print("\nOverall Fleiss' Kappa:")
    arr, categories = aggregate_raters(pivot[models].values)
    f_kappa = fleiss_kappa(arr)
    print(f"  All {len(models)} Models: {f_kappa:.4f}")
    results.append({"Metric": "Fleiss' Kappa", "Comparison": "All Models", "Value": f_kappa})

    # C. Krippendorff's Alpha (Overall)
    print("\nOverall Krippendorff's Alpha:")
    # krippendorff expects data shape: (raters, items)
    reliability_data = pivot[models].values.T
    k_alpha = krippendorff.alpha(reliability_data=reliability_data, level_of_measurement='nominal')
    print(f"  All {len(models)} Models: {k_alpha:.4f}")
    results.append({"Metric": "Krippendorff's Alpha", "Comparison": "All Models", "Value": k_alpha})

    # Export
    res_df = pd.DataFrame(results)
    out_path = os.path.join(TABLES_DIR, "statistical_agreement_metrics.csv")
    res_df.to_csv(out_path, index=False)
    print(f"\n=> Saved agreement metrics to: {out_path}")

def analyze_bootstrap_ci(df, n_iterations=1000):
    print(f"\n--- 2. Bootstrap Confidence Intervals (A Selection Rate, N={n_iterations}) ---")
    
    models = df['model'].unique()
    results = []
    
    for m in models:
        model_data = df[df['model'] == m]['choice_A'].values
        n = len(model_data)
        
        # Bootstrap means
        boot_means = []
        for _ in range(n_iterations):
            sample = np.random.choice(model_data, size=n, replace=True)
            boot_means.append(np.mean(sample))
            
        boot_means = np.array(boot_means)
        mean_rate = np.mean(model_data)
        ci_lower = np.percentile(boot_means, 2.5)
        ci_upper = np.percentile(boot_means, 97.5)
        
        print(f"  {m}: Mean = {mean_rate*100:.2f}% | 95% CI: [{ci_lower*100:.2f}%, {ci_upper*100:.2f}%]")
        results.append({
            "Model": m,
            "A_Selection_Rate_Pct": mean_rate * 100,
            "CI_Lower_95_Pct": ci_lower * 100,
            "CI_Upper_95_Pct": ci_upper * 100
        })
        
    # Export
    res_df = pd.DataFrame(results)
    out_path = os.path.join(TABLES_DIR, "bootstrap_ci_selection_rates.csv")
    res_df.to_csv(out_path, index=False)
    print(f"=> Saved Bootstrap CI to: {out_path}")

def analyze_mixed_effects(df):
    print("\n--- 3. Mixed-Effects Regression ---")
    print("Formula: choice_A ~ C(model) + C(persona_type) + C(ab_order)")
    print("Random Effect Group: test_id (Test Case naturally biases towards A or B)")
    
    # We use a Linear Probability Model with random effects as an approximation
    # since ordinary linear mixed models are more stable and interpretable in statsmodels
    # for large factorial designs, compared to Binomial GLMM.
    
    formula = "choice_A ~ C(model) + C(persona_type) + C(ab_order)"
    
    try:
        model = smf.mixedlm(formula, df, groups=df["test_id"])
        result = model.fit()
        print("\n" + str(result.summary()))
        
        # Save summary to text file
        out_path = os.path.join(TABLES_DIR, "mixed_effects_regression_summary.txt")
        with open(out_path, "w") as f:
            f.write(str(result.summary()))
        print(f"\n=> Saved Mixed-Effects Regression summary to: {out_path}")
        
    except Exception as e:
        print(f"Error fitting Mixed-Effects model: {e}")

def main():
    print("=" * 60)
    print("      COMPREHENSIVE STATISTICAL ANALYSIS (WEEK 6)")
    print("=" * 60)
    
    df = load_data()
    if df.empty:
        print("No valid data found in api_calls.")
        return
        
    analyze_agreement(df)
    analyze_bootstrap_ci(df)
    analyze_mixed_effects(df)
    
    print("\n" + "=" * 60)
    print("Analysis Complete!")

if __name__ == "__main__":
    main()
