import sys
import os
import sqlite3
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# Add scripts directory to path to import csup_analysis
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))
import csup_analysis

def analyze_surs_sensitivity():
    print("=== 1. SURS Sensitivity Analysis ===")
    df = csup_analysis.load_api_calls('data/experiment.db')
    
    # Run preliminary analyses to get components
    order_effects, r_order, flips, total_tests = csup_analysis.exp3_order_robustness(df, 'analysis/csup_results')
    r_prompt, v_prompt = csup_analysis.exp4_prompt_robustness(df, 'analysis/csup_results')
    consensus, rates, r_persona = csup_analysis.exp6_persona_consistency(df, 'analysis/csup_results')
    
    # Build models for model consistency
    models = sorted(df['model'].unique())
    tests = sorted(df['test_id'].unique())
    
    surs_data = []
    
    # Different weighting schemes
    weights_equal = {'order': 0.20, 'prompt': 0.20, 'repeat': 0.20, 'model': 0.20, 'persona': 0.20}
    weights_custom1 = {'order': 0.20, 'prompt': 0.30, 'repeat': 0.20, 'model': 0.15, 'persona': 0.15}
    weights_custom2 = {'order': 0.15, 'prompt': 0.40, 'repeat': 0.15, 'model': 0.15, 'persona': 0.15}
    
    for test_id in tests:
        t_df = df[df['test_id'] == test_id]
        
        # R_order
        r_o = r_order.get(test_id, 0.5)
        
        # R_prompt
        base_id = test_id
        for base, variants in csup_analysis.PROMPT_VARIANT_FAMILIES.items():
            if test_id in variants:
                base_id = base
                break
        r_p = r_prompt.get(base_id, np.nan)
        
        # R_repeat
        from collections import Counter
        consistencies = []
        for m in models:
            cells = t_df[t_df['model'] == m].groupby('persona_id')['choice_A'].agg(list)
            for choices in cells:
                if len(choices) >= 2:
                    maj = Counter(choices).most_common(1)[0][1]
                    consistencies.append(maj / len(choices))
        r_r = np.mean(consistencies) if consistencies else 0
        
        # R_model
        votes = t_df.groupby(['persona_id', 'model'])['choice_A'].agg(lambda x: 1 if x.mean() > 0.5 else 0).reset_index()
        votes.columns = ['persona_id', 'model', 'vote']
        pivot = votes.pivot_table(index='persona_id', columns='model', values='vote').dropna()
        if len(pivot) > 0 and len(pivot.columns) >= 2:
            agree_rates = []
            import itertools
            for m1, m2 in itertools.combinations(pivot.columns, 2):
                agree_rates.append((pivot[m1] == pivot[m2]).mean())
            r_m = np.mean(agree_rates)
        else:
            r_m = 0.5
            
        # R_persona
        pt = t_df['persona_type'].iloc[0] if len(t_df) > 0 else 'biographical'
        r_per = r_persona.get(pt, 0.5)
        
        # We only care about tests with all 5 components (the base tests that have R_prompt)
        if not np.isnan(r_p):
            # Calculate SURS
            surs_equal = (r_o * weights_equal['order'] + r_p * weights_equal['prompt'] + r_r * weights_equal['repeat'] + r_m * weights_equal['model'] + r_per * weights_equal['persona'])
            surs_c1 = (r_o * weights_custom1['order'] + r_p * weights_custom1['prompt'] + r_r * weights_custom1['repeat'] + r_m * weights_custom1['model'] + r_per * weights_custom1['persona'])
            surs_c2 = (r_o * weights_custom2['order'] + r_p * weights_custom2['prompt'] + r_r * weights_custom2['repeat'] + r_m * weights_custom2['model'] + r_per * weights_custom2['persona'])
            
            def get_tier(s): return 'High' if s >= 0.8 else 'Moderate' if s >= 0.6 else 'Low'
            
            surs_data.append({
                'test_id': test_id,
                'SURS_equal': surs_equal, 'Tier_equal': get_tier(surs_equal),
                'SURS_c1': surs_c1, 'Tier_c1': get_tier(surs_c1),
                'SURS_c2': surs_c2, 'Tier_c2': get_tier(surs_c2)
            })
            
    res_df = pd.DataFrame(surs_data)
    print(f"\nAnalyzed {len(res_df)} tests that have R_prompt (full 5 components).")
    
    # Check if tiers change
    changes_c1 = (res_df['Tier_equal'] != res_df['Tier_c1']).sum()
    changes_c2 = (res_df['Tier_equal'] != res_df['Tier_c2']).sum()
    
    print(f"Weight Scheme 1 (Prompt 30%): {changes_c1} tests changed tier.")
    print(f"Weight Scheme 2 (Prompt 40%): {changes_c2} tests changed tier.")
    
    # Breakdown
    for t in ['High', 'Moderate', 'Low']:
        n_eq = (res_df['Tier_equal'] == t).sum()
        n_c1 = (res_df['Tier_c1'] == t).sum()
        print(f"  Tier {t}: Equal={n_eq}, C1={n_c1}")

    print("\n")


def analyze_variance_bootstrap():
    print("=== 2. Variance Bootstrap CI ===")
    print("We will run a simplified mixed-effects model to get variance components.")
    # Because statsmodels mixedlm is very slow for large datasets with crossed random effects,
    # we will use an ANOVA-like variance components estimation for the bootstrap to be tractable.
    
    conn = sqlite3.connect('data/experiment.db')
    df = pd.read_sql_query("SELECT test_id, model, persona_type, ab_order, parsed_choice FROM api_calls WHERE status='completed' AND parsed_choice IN ('A','B')", conn)
    conn.close()
    
    df['choice_A'] = (df['parsed_choice'] == 'A').astype(int)
    
    def get_var_components(data):
        v_total = data['choice_A'].var()
        v_sem = data.groupby('test_id')['choice_A'].mean().var()
        v_mod = data.groupby('model')['choice_A'].mean().var()
        v_ord = data.groupby('ab_order')['choice_A'].mean().var()
        v_per = data.groupby('persona_type')['choice_A'].mean().var()
        v_rep = data.groupby(['test_id', 'model', 'persona_type'])['choice_A'].var().mean() # approx
        
        # Add a mock prompt variance (we know it's approx 0.084 from earlier)
        # We will just focus on the non-prompt ones or use fixed ratios.
        # This is just a demonstration script for the CI.
        
        components = {
            'Semantic': v_sem,
            'Model': v_mod,
            'Order': v_ord,
            'Persona': v_per,
            'Repeat': v_rep
        }
        tot = sum(components.values())
        return {k: v/tot*100 for k,v in components.items()}
    
    # Original
    orig = get_var_components(df)
    
    # Bootstrap
    B = 100
    boot_res = []
    print(f"Running {B} bootstrap samples...")
    for i in range(B):
        sample = df.sample(frac=1.0, replace=True)
        boot_res.append(get_var_components(sample))
        
    boot_df = pd.DataFrame(boot_res)
    
    print("\nVariance Components Bootstrap 95% CI:")
    for k in orig.keys():
        lower = boot_df[k].quantile(0.025)
        upper = boot_df[k].quantile(0.975)
        print(f"  {k}: {orig[k]:.1f}% [{lower:.1f}%, {upper:.1f}%]")

if __name__ == '__main__':
    analyze_surs_sensitivity()
    analyze_variance_bootstrap()
