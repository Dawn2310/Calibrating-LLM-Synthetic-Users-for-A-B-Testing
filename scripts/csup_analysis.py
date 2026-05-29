"""
CSUP Analysis Pipeline — Complete Tier 2+3
==========================================
Runs all 9 experiments from existing data + generates tables/figures.

Usage:
    python csup_analysis.py --db data/experiment.db --output ./csup_results/

Requirements:
    pip install openpyxl pandas numpy scipy scikit-learn matplotlib seaborn statsmodels
"""


import argparse
import json
import os
import warnings
from collections import Counter, defaultdict
from itertools import combinations

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats

warnings.filterwarnings('ignore')

# ============================================================
# DATA LOADING
# ============================================================

def load_api_calls(db_path):
    """Load api_calls from experiment.db"""
    import sqlite3
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query(
        "SELECT * FROM api_calls WHERE status='completed' AND parsed_choice IN ('A','B')",
        conn
    )
    conn.close()
    # Encode choice as binary
    df['choice_A'] = (df['parsed_choice'] == 'A').astype(int)
    # Extract domain
    def get_domain(test_id):
        if test_id.startswith('UI'): return 'UI/UX'
        elif test_id.startswith('COPY'): return 'Copywriting'
        elif test_id.startswith('REC'): return 'Recommendation'
        return 'Unknown'
    df['domain'] = df['test_id'].apply(get_domain)
    print(f"Loaded {len(df)} api_calls")
    print(f"Models: {sorted(df['model'].unique())}")
    print(f"Persona types: {sorted(df['persona_type'].unique())}")
    print(f"Tests: {sorted(df['test_id'].unique())}")
    return df


def load_position_bias(db_path):
    """Load position bias data from experiment.db"""
    import sqlite3
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query(
        "SELECT * FROM position_bias WHERE choice IN ('A','B')",
        conn
    )
    conn.close()
    df['choice_A'] = (df['choice'] == 'A').astype(int)
    print(f"Loaded {len(df)} position_bias rows")
    return df


# ============================================================
# EXP 1: Overall Agreement
# ============================================================

def exp1_overall_agreement(df, output_dir):
    """Compute Fleiss' kappa, Cohen's kappa pairwise, % agreement"""
    print("\n" + "="*60)
    print("EXP 1: Overall Between-Model Agreement")
    print("="*60)
    
    models = sorted(df['model'].unique())
    n_models = len(models)
    
    # Create majority vote per (test_id, persona_id, model)
    votes = df.groupby(['test_id', 'persona_id', 'model'])['choice_A'].agg(
        lambda x: 1 if x.mean() > 0.5 else 0
    ).reset_index()
    votes.columns = ['test_id', 'persona_id', 'model', 'majority_A']
    
    # Pivot to wide format: rows = (test, persona), cols = models
    pivot = votes.pivot_table(index=['test_id', 'persona_id'], 
                              columns='model', values='majority_A').dropna()
    
    # --- Pairwise Cohen's kappa ---
    results = []
    for m1, m2 in combinations(models, 2):
        agree = (pivot[m1] == pivot[m2]).mean()
        # Cohen's kappa
        p_o = agree
        p1_a = pivot[m1].mean()
        p2_a = pivot[m2].mean()
        p_e = p1_a * p2_a + (1-p1_a) * (1-p2_a)
        kappa = (p_o - p_e) / (1 - p_e) if p_e < 1 else 0
        results.append({
            'pair': f"{m1} vs {m2}",
            'cohens_kappa': round(kappa, 3),
            'raw_agreement': round(agree * 100, 2)
        })
        print(f"  {m1} vs {m2}: κ={kappa:.3f}, agree={agree*100:.1f}%")
    
    # --- Fleiss' kappa ---
    n_items = len(pivot)
    n_raters = n_models
    n_categories = 2
    
    # Count how many raters chose A and B for each item
    counts = np.zeros((n_items, n_categories))
    for i, (idx, row) in enumerate(pivot.iterrows()):
        n_a = sum(row[m] for m in models)
        counts[i, 0] = n_a          # chose A
        counts[i, 1] = n_raters - n_a  # chose B
    
    # Fleiss kappa computation
    N = n_items
    n = n_raters
    k = n_categories
    
    p_j = counts.sum(axis=0) / (N * n)  # proportion per category
    P_i = (np.sum(counts**2, axis=1) - n) / (n * (n-1))  # per-item agreement
    P_bar = P_i.mean()
    P_e = np.sum(p_j**2)
    fleiss_kappa = (P_bar - P_e) / (1 - P_e) if P_e < 1 else 0
    
    print(f"\n  Fleiss' κ (all {n_models} models): {fleiss_kappa:.3f}")
    print(f"  Krippendorff's α ≈ {fleiss_kappa:.3f}")  # approximation for binary
    
    # --- Heatmap figure ---
    agree_matrix = np.eye(n_models) * 100
    for r in results:
        m1, m2 = r['pair'].split(' vs ')
        i1, i2 = models.index(m1), models.index(m2)
        agree_matrix[i1, i2] = r['raw_agreement']
        agree_matrix[i2, i1] = r['raw_agreement']
    
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(agree_matrix, annot=True, fmt='.1f', 
                xticklabels=models, yticklabels=models,
                cmap='YlGnBu', vmin=75, vmax=100, ax=ax)
    ax.set_title(f'Overall Pairwise Model Agreement (%)\nFleiss\' κ = {fleiss_kappa:.3f}')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'exp1_agreement_heatmap.png'), dpi=300)
    plt.close()
    
    return {
        'fleiss_kappa': fleiss_kappa,
        'pairwise': results,
        'pivot': pivot
    }


# ============================================================
# EXP 2: Variance Decomposition
# ============================================================

def exp2_variance_decomposition(df, output_dir, v_prompt_value=None):
    """Decompose variance into semantic/order/prompt/persona/model/repeat/residual.
    
    Args:
        v_prompt_value: Optional float. If provided (from Exp 4), adds prompt
                        wording as a separate variance component.
    """
    print("\n" + "="*60)
    print("EXP 2: Variance Decomposition")
    print("="*60)
    
    # Compute P(A) at different aggregation levels
    total_var = df['choice_A'].var()
    
    # V_semantic: variance across test cases
    test_means = df.groupby('test_id')['choice_A'].mean()
    v_semantic = test_means.var()
    
    # V_model: variance across models
    model_means = df.groupby('model')['choice_A'].mean()
    v_model = model_means.var()
    
    # V_order: variance across ab_order
    order_means = df.groupby('ab_order')['choice_A'].mean()
    v_order = order_means.var()
    
    # V_persona_type: variance across persona depth levels
    ptype_means = df.groupby('persona_type')['choice_A'].mean()
    v_persona_type = ptype_means.var()
    
    # V_persona_individual: variance across individual personas within type
    persona_means = df.groupby('persona_id')['choice_A'].mean()
    v_persona_individual = persona_means.var()
    
    # V_repeat: variance across runs (within same test/persona/model)
    cell_means = df.groupby(['test_id', 'persona_id', 'model'])['choice_A'].mean()
    cell_vars = df.groupby(['test_id', 'persona_id', 'model'])['choice_A'].var()
    v_repeat = cell_vars.mean()  # average within-cell variance
    
    # Build components dict — include V_prompt if available
    v_explained = v_semantic + v_model + v_order + v_persona_type + v_repeat
    if v_prompt_value is not None:
        v_explained += v_prompt_value
    v_residual = max(0, total_var - v_explained)
    
    # Normalize to percentages
    components = {'Semantic (test case)': v_semantic}
    if v_prompt_value is not None:
        components['Prompt wording'] = v_prompt_value
    components.update({
        'Model family': v_model,
        'Display order': v_order,
        'Persona depth': v_persona_type,
        'Repeat sampling': v_repeat,
        'Residual': v_residual
    })
    
    total = sum(components.values())
    pct = {k: v/total*100 for k, v in components.items()}
    
    print("\n  Variance Decomposition:")
    print(f"  {'Component':<25} {'Variance':<12} {'% of Total':<10}")
    print(f"  {'-'*47}")
    for name, var in components.items():
        print(f"  {name:<25} {var:<12.6f} {pct[name]:<10.1f}%")
    
    # --- Pie chart ---
    fig, ax = plt.subplots(figsize=(8, 6))
    colors_full = ['#2ecc71', '#e67e22', '#3498db', '#e74c3c', '#f39c12', '#9b59b6', '#95a5a6']
    colors = colors_full[:len(components)]
    wedges, texts, autotexts = ax.pie(
        list(pct.values()), labels=list(pct.keys()), autopct='%1.1f%%',
        colors=colors, startangle=90, textprops={'fontsize': 9}
    )
    ax.set_title('Variance Decomposition of Synthetic User A/B Choices')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'exp2_variance_decomposition.png'), dpi=300)
    plt.close()
    
    # --- Stacked bar ---
    fig, ax = plt.subplots(figsize=(10, 4))
    bottom = 0
    for (name, p), color in zip(pct.items(), colors):
        ax.barh(0, p, left=bottom, color=color, label=f'{name} ({p:.1f}%)')
        bottom += p
    ax.set_xlim(0, 100)
    ax.set_xlabel('% of Total Variance')
    ax.set_yticks([])
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=3, fontsize=8)
    ax.set_title('Variance Decomposition — Stacked')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'exp2_variance_bar.png'), dpi=300)
    plt.close()
    
    return components, pct


# ============================================================
# EXP 3: Order Robustness + Auto-Counterbalance
# ============================================================

def exp3_order_robustness(df, output_dir):
    """Compare raw vs counterbalanced output"""
    print("\n" + "="*60)
    print("EXP 3: Order Robustness + Auto-Counterbalance")
    print("="*60)
    
    models = sorted(df['model'].unique())
    
    # Split by order
    orig = df[df['ab_order'] == 'original']
    swap = df[df['ab_order'] == 'swapped']
    
    # Per-model order effect
    print("\n  Per-model order effect:")
    order_effects = {}
    for m in models:
        p_orig = orig[orig['model'] == m]['choice_A'].mean()
        p_swap = swap[swap['model'] == m]['choice_A'].mean()
        effect = p_orig - p_swap
        order_effects[m] = {
            'p_original': p_orig,
            'p_swapped': p_swap,
            'effect_pp': effect * 100
        }
        print(f"  {m}: original={p_orig:.3f}, swapped={p_swap:.3f}, Δ={effect*100:.1f}pp")
    
    # Counterbalanced preference per (test, persona, model)
    raw_votes = orig.groupby(['test_id', 'persona_id', 'model'])['choice_A'].mean()
    
    # Counterbalanced = average of original and (1 - swapped)
    orig_agg = orig.groupby(['test_id', 'persona_id', 'model'])['choice_A'].mean()
    swap_agg = swap.groupby(['test_id', 'persona_id', 'model'])['choice_A'].mean()
    
    # Align indices
    common = orig_agg.index.intersection(swap_agg.index)
    counter_agg = (orig_agg.loc[common] + (1 - swap_agg.loc[common])) / 2
    
    # R_order per test case
    r_order = {}
    for test_id in sorted(df['test_id'].unique()):
        t_orig = orig[orig['test_id'] == test_id]['choice_A'].mean()
        t_swap = swap[swap['test_id'] == test_id]['choice_A'].mean()
        r = 1 - abs(t_orig - t_swap) / 0.5
        r_order[test_id] = max(0, r)
    
    print(f"\n  R_order per test (mean={np.mean(list(r_order.values())):.3f}):")
    for t, r in sorted(r_order.items(), key=lambda x: x[1]):
        flag = "⚠️" if r < 0.6 else "✓"
        print(f"    {flag} {t}: {r:.3f}")
    
    # Count flipped tests after counterbalancing
    flips = 0
    total_tests = 0
    for test_id in sorted(df['test_id'].unique()):
        for m in models:
            mask_o = (orig['test_id'] == test_id) & (orig['model'] == m)
            mask_s = (swap['test_id'] == test_id) & (swap['model'] == m)
            if mask_o.sum() > 0 and mask_s.sum() > 0:
                raw_pref = 'A' if orig[mask_o]['choice_A'].mean() > 0.5 else 'B'
                p_counter = (orig[mask_o]['choice_A'].mean() + (1 - swap[mask_s]['choice_A'].mean())) / 2
                counter_pref = 'A' if p_counter > 0.5 else 'B'
                total_tests += 1
                if raw_pref != counter_pref:
                    flips += 1
    
    print(f"\n  Tests FLIPPED after counterbalancing: {flips}/{total_tests} ({100*flips/total_tests:.1f}%)")
    
    # --- Figure: order effect bar chart ---
    fig, ax = plt.subplots(figsize=(10, 5))
    x = np.arange(len(models))
    width = 0.35
    bars1 = ax.bar(x - width/2, [order_effects[m]['p_original'] * 100 for m in models],
                   width, label='Original order', color='#2ecc71', alpha=0.8)
    bars2 = ax.bar(x + width/2, [order_effects[m]['p_swapped'] * 100 for m in models],
                   width, label='Swapped order', color='#e74c3c', alpha=0.8)
    ax.axhline(y=50, color='gray', linestyle='--', alpha=0.5, label='50% (no bias)')
    ax.set_ylabel('Variant A Selection Rate (%)')
    ax.set_title('Order Effect: Original vs Swapped (with persona)')
    ax.set_xticks(x)
    ax.set_xticklabels(models, rotation=15, ha='right')
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'exp3_order_effect.png'), dpi=300)
    plt.close()
    
    return order_effects, r_order, flips, total_tests


# ============================================================
# EXP 4: Prompt Robustness
# ============================================================

# Mapping from base test_id to its prompt variants (V2=condensed, V3=expanded)
PROMPT_VARIANT_FAMILIES = {
    'UI-09':   ['UI-09-V2',   'UI-09-V3'],
    'COPY-04': ['COPY-04-V2', 'COPY-04-V3'],
    'REC-06':  ['REC-06-V2',  'REC-06-V3'],
    'UI-01':   ['UI-01-V2',   'UI-01-V3'],
    'REC-03':  ['REC-03-V2',  'REC-03-V3'],
}


def exp4_prompt_robustness(df, output_dir):
    """Measure how much A/B results change when variant descriptions are reworded.

    Compares base test cases (V1) against condensed (V2) and expanded (V3)
    prompt variants.  Computes Cohen's kappa for each pair and derives
    R_prompt per test case.

    Returns:
        r_prompt  — dict {base_test_id: R_prompt} (range 0-1, higher = more robust)
        v_prompt  — float, estimated prompt-wording variance for Exp 2
    """
    print("\n" + "="*60)
    print("EXP 4: Prompt Robustness")
    print("="*60)

    models = sorted(df['model'].unique())

    # Collect per-family results
    family_results = []
    r_prompt = {}

    for base_id, variants in PROMPT_VARIANT_FAMILIES.items():
        v2_id, v3_id = variants
        ids_present = [tid for tid in [base_id, v2_id, v3_id]
                       if tid in df['test_id'].unique()]
        if len(ids_present) < 2:
            print(f"  Skipping {base_id}: not enough variants in data "
                  f"(found {ids_present})")
            continue

        # Majority vote per (persona_id, model) for each version
        def _majority_votes(test_id):
            sub = df[df['test_id'] == test_id]
            if sub.empty:
                return pd.Series(dtype=int)
            votes = sub.groupby(['persona_id', 'model'])['choice_A'].agg(
                lambda x: 1 if x.mean() > 0.5 else 0
            )
            return votes

        v1_votes = _majority_votes(base_id)
        v2_votes = _majority_votes(v2_id)
        v3_votes = _majority_votes(v3_id)

        # Compute Cohen's kappa for every pair that has data
        pairs = []
        for label, va, vb in [('V1-V2', v1_votes, v2_votes),
                               ('V1-V3', v1_votes, v3_votes),
                               ('V2-V3', v2_votes, v3_votes)]:
            common_idx = va.index.intersection(vb.index)
            if len(common_idx) < 10:
                continue
            a_vals = va.loc[common_idx].values
            b_vals = vb.loc[common_idx].values
            p_o = (a_vals == b_vals).mean()
            p1 = a_vals.mean()
            p2 = b_vals.mean()
            p_e = p1 * p2 + (1 - p1) * (1 - p2)
            kappa = (p_o - p_e) / (1 - p_e) if p_e < 1 else 1.0
            pairs.append({'pair': label, 'kappa': kappa, 'agree': p_o})

        if not pairs:
            continue

        mean_kappa = np.mean([p['kappa'] for p in pairs])
        r_prompt[base_id] = max(0.0, min(1.0, mean_kappa))

        print(f"\n  {base_id}:")
        for p in pairs:
            print(f"    {p['pair']}: kappa={p['kappa']:.3f}, agree={p['agree']*100:.1f}%")
        print(f"    R_prompt = {r_prompt[base_id]:.3f}")

        # Per-model breakdown
        for m in models:
            m_kappas = []
            for label, va, vb in [('V1-V2', v1_votes, v2_votes),
                                   ('V1-V3', v1_votes, v3_votes),
                                   ('V2-V3', v2_votes, v3_votes)]:
                idx_m = [idx for idx in va.index.intersection(vb.index)
                         if idx[1] == m]  # (persona_id, model)
                if len(idx_m) < 5:
                    continue
                a_m = va.loc[idx_m].values
                b_m = vb.loc[idx_m].values
                po = (a_m == b_m).mean()
                p1 = a_m.mean()
                p2 = b_m.mean()
                pe = p1 * p2 + (1 - p1) * (1 - p2)
                k = (po - pe) / (1 - pe) if pe < 1 else 1.0
                m_kappas.append(k)
            if m_kappas:
                family_results.append({
                    'base_test': base_id, 'model': m,
                    'mean_kappa': np.mean(m_kappas)
                })

    # --- V_prompt estimate: variance of P(A) across prompt versions ---
    version_means = []
    for base_id, variants in PROMPT_VARIANT_FAMILIES.items():
        all_ids = [base_id] + variants
        for tid in all_ids:
            sub = df[df['test_id'] == tid]
            if not sub.empty:
                version_means.append(sub['choice_A'].mean())
    v_prompt = np.var(version_means) if len(version_means) >= 2 else 0.0
    print(f"\n  Estimated V_prompt = {v_prompt:.6f}")

    # Prompt Sensitivity Score = 1 - mean(R_prompt)
    if r_prompt:
        mean_r = np.mean(list(r_prompt.values()))
        print(f"  Mean R_prompt = {mean_r:.3f}")
        print(f"  Prompt Sensitivity = {1 - mean_r:.3f}")

    # --- Figure 8: Prompt sensitivity per test x model ---
    if family_results:
        fr_df = pd.DataFrame(family_results)
        fig, ax = plt.subplots(figsize=(10, 5))
        bases = sorted(fr_df['base_test'].unique())
        x = np.arange(len(bases))
        width = 0.18
        for i, m in enumerate(models):
            vals = []
            for b in bases:
                row = fr_df[(fr_df['base_test'] == b) & (fr_df['model'] == m)]
                vals.append(row['mean_kappa'].values[0] if len(row) > 0 else 0)
            ax.bar(x + i * width, vals, width, label=m, alpha=0.85)
        ax.set_xticks(x + width * (len(models) - 1) / 2)
        ax.set_xticklabels(bases, rotation=15, ha='right')
        ax.set_ylabel("Cohen's kappa (prompt robustness)")
        ax.set_title('Prompt Robustness: Cross-Version Agreement per Test x Model')
        ax.axhline(y=0.6, color='#e74c3c', linestyle='--', alpha=0.5,
                   label='Fair (0.6)')
        ax.legend(fontsize=8)
        ax.set_ylim(bottom=-0.1, top=1.05)
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'exp4_prompt_sensitivity.png'),
                    dpi=300)
        plt.close()

    return r_prompt, v_prompt


# ============================================================
# EXP 5: Repeat Stability Curve
# ============================================================

def exp5_repeat_stability(df, output_dir):
    """Compute drift rate at increasing n (number of repeated runs).

    Uses runs 1-3 for all test cases, plus runs 4-9 where available.
    Plots diminishing-returns curve and identifies optimal n*.

    Returns:
        stability_results — dict with per-model drift curves
    """
    print("\n" + "="*60)
    print("EXP 5: Repeat Stability Curve")
    print("="*60)

    models = sorted(df['model'].unique())

    # Determine maximum available n per (test, persona, model)
    run_counts = df.groupby(
        ['test_id', 'persona_id', 'model']
    )['run_number'].nunique()

    max_available_n = run_counts.max()
    print(f"  Max runs per cell available: {max_available_n}")

    # Pick n values to evaluate: always include 1 and 3; add higher if data exists
    n_values = [1, 3]
    for n in [5, 7, 9]:
        # Need at least some cells with >=n runs to plot a point
        if (run_counts >= n).sum() > 10:
            n_values.append(n)
    n_values = sorted(set(n_values))
    print(f"  Evaluating n = {n_values}")

    stability_results = {m: {} for m in models}

    for m in models:
        m_df = df[df['model'] == m]
        for n in n_values:
            # For each cell, take the first n runs and compute majority stability
            consistencies = []
            for (test_id, persona_id), cell in m_df.groupby(
                    ['test_id', 'persona_id']):
                runs_available = sorted(cell['run_number'].unique())
                if len(runs_available) < n:
                    continue
                selected_runs = runs_available[:n]
                choices = cell[cell['run_number'].isin(
                    selected_runs)]['choice_A'].values
                if len(choices) < n:
                    continue
                # Majority vote
                n_a = choices.sum()
                n_b = len(choices) - n_a
                c_intra = max(n_a, n_b) / len(choices)
                consistencies.append(c_intra)

            if consistencies:
                avg_c = np.mean(consistencies)
                drift = 1 - avg_c
                stability_results[m][n] = {
                    'C_intra': avg_c,
                    'drift_rate': drift,
                    'n_cells': len(consistencies)
                }

    # Print results table
    print(f"\n  {'Model':<25} ", end='')
    for n in n_values:
        print(f"n={n:<6}", end='')
    print()
    print(f"  {'-'*60}")
    for m in models:
        print(f"  {m:<25} ", end='')
        for n in n_values:
            if n in stability_results[m]:
                d = stability_results[m][n]['drift_rate']
                print(f"{d*100:<6.2f}%", end='')
            else:
                print(f"{'n/a':<7}", end='')
        print()

    # Find optimal n* per model
    print("\n  Optimal n* (marginal improvement < 0.5%):")
    for m in models:
        prev_drift = None
        optimal_n = n_values[0]
        for n in n_values:
            if n in stability_results[m]:
                drift = stability_results[m][n]['drift_rate']
                if prev_drift is not None:
                    improvement = prev_drift - drift
                    if improvement < 0.005:  # < 0.5 percentage points
                        optimal_n = n_values[n_values.index(n) - 1] \
                            if n_values.index(n) > 0 else n
                        break
                prev_drift = drift
                optimal_n = n
        print(f"    {m}: n* = {optimal_n}")

    # --- Figure 9: Drift rate vs n ---
    fig, ax = plt.subplots(figsize=(8, 5))
    colors_model = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12']
    for i, m in enumerate(models):
        ns = [n for n in n_values if n in stability_results[m]]
        drifts = [stability_results[m][n]['drift_rate'] * 100 for n in ns]
        if ns:
            ax.plot(ns, drifts, 'o-', label=m, linewidth=2, markersize=8,
                    color=colors_model[i % len(colors_model)])

    ax.set_xlabel('Number of Repeated Runs (n)')
    ax.set_ylabel('Drift Rate (%)')
    ax.set_title('Repeat Stability Curve: Drift Rate vs Number of Runs')
    ax.set_xticks(n_values)
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'exp5_repeat_stability.png'), dpi=300)
    plt.close()

    return stability_results


# ============================================================
# EXP 6: Persona Consistency
# ============================================================

def exp6_persona_consistency(df, output_dir):
    """Analyze persona depth effect on agreement"""
    print("\n" + "="*60)
    print("EXP 6: Persona Consistency (Hallucination of Depth)")
    print("="*60)
    
    models = sorted(df['model'].unique())
    n_models = len(models)
    ptypes = ['demographic', 'biographical', 'interview']
    
    # Full consensus rate per persona type
    consensus = {}
    for pt in ptypes:
        pt_df = df[df['persona_type'] == pt]
        # Majority vote per (test, persona, model)
        votes = pt_df.groupby(['test_id', 'persona_id', 'model'])['choice_A'].agg(
            lambda x: 1 if x.mean() > 0.5 else 0
        ).reset_index()
        votes.columns = ['test_id', 'persona_id', 'model', 'vote']
        
        pivot = votes.pivot_table(index=['test_id', 'persona_id'],
                                  columns='model', values='vote').dropna()
        
        # Full consensus = all models agree
        full_agree = (pivot.std(axis=1) == 0).mean() * 100
        consensus[pt] = full_agree
        print(f"  {pt}: {full_agree:.1f}% full consensus")
    
    # Variant A selection rate by persona type × model
    print("\n  Variant A rate by depth × model:")
    rates = {}
    for pt in ptypes:
        rates[pt] = {}
        for m in models:
            r = df[(df['persona_type'] == pt) & (df['model'] == m)]['choice_A'].mean()
            rates[pt][m] = r
        print(f"  {pt}: {', '.join(f'{m}={rates[pt][m]:.3f}' for m in models)}")
    
    # R_persona per persona type
    r_persona = {}
    for pt in ptypes:
        persona_rates = df[df['persona_type'] == pt].groupby('persona_id')['choice_A'].mean()
        r = 1 - persona_rates.std()
        r_persona[pt] = max(0, r)
        print(f"  R_persona ({pt}): {r_persona[pt]:.3f}")
    
    # --- Figure: consensus bar chart ---
    fig, ax = plt.subplots(figsize=(8, 5))
    colors_pt = ['#2c3e50', '#16a085', '#27ae60']
    bars = ax.bar(ptypes, [consensus[pt] for pt in ptypes], color=colors_pt)
    for bar, pt in zip(bars, ptypes):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                f'{consensus[pt]:.1f}%', ha='center', fontsize=11)
    ax.set_ylabel('Full Consensus Rate (%)')
    ax.set_xlabel('Persona Depth Level')
    ax.set_title(f'Full {n_models}-Model Consensus by Persona Depth')
    ax.set_ylim(0, 100)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'exp6_persona_consensus.png'), dpi=300)
    plt.close()
    
    # --- Figure: persona richness shift ---
    fig, ax = plt.subplots(figsize=(9, 5))
    for m in models:
        vals = [rates[pt][m] * 100 for pt in ptypes]
        ax.plot(ptypes, vals, 'o-', label=m, linewidth=2, markersize=8)
    ax.axhline(y=50, color='gray', linestyle='--', alpha=0.5, label='50% neutral')
    ax.set_ylabel("Percentage of 'A' Choices (%)")
    ax.set_xlabel('Persona Type (Richness)')
    ax.set_title("Variant A Selection Rate Across Persona Richness Levels")
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'exp6_persona_shift.png'), dpi=300)
    plt.close()
    
    return consensus, rates, r_persona


# ============================================================
# EXP 7: Multi-Model Ensemble
# ============================================================

def exp7_ensemble(df, output_dir):
    """Evaluate ensemble reliability at k=1,2,3,...,n_models"""
    print("\n" + "="*60)
    print("EXP 7: Multi-Model Ensemble Effect")
    print("="*60)
    
    models = sorted(df['model'].unique())
    n_models = len(models)
    
    # Majority vote per (test, persona, model) using all 3 runs
    votes = df.groupby(['test_id', 'persona_id', 'model'])['choice_A'].agg(
        lambda x: 1 if x.mean() > 0.5 else 0
    ).reset_index()
    votes.columns = ['test_id', 'persona_id', 'model', 'vote']
    
    pivot = votes.pivot_table(index=['test_id', 'persona_id'],
                              columns='model', values='vote').dropna()
    
    # k=1: self-consistency across runs per model
    print("\n  k=1 (single model) — within-run consistency:")
    k1_results = {}
    for m in models:
        m_df = df[df['model'] == m]
        cells = m_df.groupby(['test_id', 'persona_id'])['choice_A'].agg(list)
        consistencies = []
        for choices in cells:
            if len(choices) >= 2:
                majority = Counter(choices).most_common(1)[0][1]
                consistencies.append(majority / len(choices))
        avg_c = np.mean(consistencies)
        k1_results[m] = avg_c
        print(f"    {m}: {avg_c:.3f}")
    
    # k=2,3,...,n: ensemble majority vote consistency
    ensemble_results = {}
    for k in range(2, n_models + 1):
        combos = list(combinations(models, k))
        agreements = []
        for combo in combos:
            cols = list(combo)
            sub = pivot[cols]
            # Majority vote
            majority = (sub.sum(axis=1) > k/2).astype(int)
            # Measure consistency: how often does ensemble agree with full ensemble?
            full_majority = (pivot[models].sum(axis=1) > n_models/2).astype(int)
            agree = (majority == full_majority).mean()
            agreements.append(agree)
        
        avg_agree = np.mean(agreements)
        ensemble_results[k] = avg_agree
        print(f"  k={k}: {len(combos)} combos, avg agreement with full={avg_agree:.3f}")
    
    # --- Figure: ensemble curve ---
    fig, ax = plt.subplots(figsize=(8, 5))
    ks = [1] + list(ensemble_results.keys())
    vals = [np.mean(list(k1_results.values()))] + list(ensemble_results.values())
    ax.plot(ks, [v*100 for v in vals], 'o-', linewidth=2, markersize=10, color='#3498db')
    ax.set_xlabel('Number of Models in Ensemble (k)')
    ax.set_ylabel('Reliability (%)')
    ax.set_title('Ensemble Reliability vs Number of Models')
    ax.set_xticks(ks)
    ax.set_ylim(80, 101)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'exp7_ensemble_curve.png'), dpi=300)
    plt.close()
    
    return k1_results, ensemble_results


# ============================================================
# EXP 8: SURS Computation
# ============================================================

def exp8_surs(df, r_order, r_persona, k1_results, fleiss_kappa, output_dir,
             r_prompt_dict=None):
    """Compute Synthetic User Reliability Score per test case.

    Args:
        r_prompt_dict: Optional dict {base_test_id: R_prompt} from Exp 4.
                       When provided for a test, SURS uses 5 equal-weighted
                       components (0.20 each); otherwise falls back to 4 (0.25).
    """
    print("\n" + "="*60)
    print("EXP 8: SURS -- Synthetic User Reliability Score")
    print("="*60)
    
    if r_prompt_dict is None:
        r_prompt_dict = {}

    models = sorted(df['model'].unique())
    tests = sorted(df['test_id'].unique())
    
    surs_data = []
    for test_id in tests:
        t_df = df[df['test_id'] == test_id]
        
        # R_order (from exp3)
        r_o = r_order.get(test_id, 0.5)
        
        # R_prompt (from exp4) — look up base test_id
        # For variant test_ids like UI-09-V2, map back to base UI-09
        base_id = test_id
        for base, variants in PROMPT_VARIANT_FAMILIES.items():
            if test_id in variants:
                base_id = base
                break
        r_p = r_prompt_dict.get(base_id, np.nan)
        
        # R_repeat — average within-model consistency for this test
        consistencies = []
        for m in models:
            cells = t_df[t_df['model'] == m].groupby('persona_id')['choice_A'].agg(list)
            for choices in cells:
                if len(choices) >= 2:
                    maj = Counter(choices).most_common(1)[0][1]
                    consistencies.append(maj / len(choices))
        r_r = np.mean(consistencies) if consistencies else 0
        
        # R_model — cross-model agreement for this test
        votes = t_df.groupby(['persona_id', 'model'])['choice_A'].agg(
            lambda x: 1 if x.mean() > 0.5 else 0
        ).reset_index()
        votes.columns = ['persona_id', 'model', 'vote']
        pivot = votes.pivot_table(index='persona_id', columns='model', values='vote').dropna()
        if len(pivot) > 0 and len(pivot.columns) >= 2:
            agree_rates = []
            for m1, m2 in combinations(models, 2):
                if m1 in pivot.columns and m2 in pivot.columns:
                    agree_rates.append((pivot[m1] == pivot[m2]).mean())
            r_m = np.mean(agree_rates) if agree_rates else 0
        else:
            r_m = 0
        
        # R_persona — consistency across personas for this test
        persona_rates = t_df.groupby('persona_id')['choice_A'].mean()
        r_s = max(0, 1 - persona_rates.std() * 2)  # scale so std=0.5 -> R=0
        
        # SURS: 5 components when R_prompt is available, else 4
        if not np.isnan(r_p):
            surs = 0.2 * r_o + 0.2 * r_p + 0.2 * r_r + 0.2 * r_m + 0.2 * r_s
        else:
            surs = 0.25 * r_o + 0.25 * r_r + 0.25 * r_m + 0.25 * r_s
        
        # Flag
        if surs >= 0.8:
            flag = 'High'
        elif surs >= 0.6:
            flag = 'Moderate'
        else:
            flag = 'Low'
        
        surs_data.append({
            'test_id': test_id,
            'R_order': round(r_o, 3),
            'R_prompt': round(r_p, 3) if not np.isnan(r_p) else 'n/a',
            'R_repeat': round(r_r, 3),
            'R_model': round(r_m, 3),
            'R_persona': round(r_s, 3),
            'SURS': round(surs, 3),
            'flag': flag
        })
    
    surs_df = pd.DataFrame(surs_data).sort_values('SURS', ascending=False)
    
    print(f"\n  {'Test':<10} {'R_order':<9} {'R_prompt':<9} {'R_repeat':<9} "
          f"{'R_model':<9} {'R_persona':<10} {'SURS':<7} {'Flag'}")
    print(f"  {'-'*72}")
    for _, row in surs_df.iterrows():
        rp_str = f"{row['R_prompt']:<9}" if row['R_prompt'] != 'n/a' else 'n/a      '
        print(f"  {row['test_id']:<10} {row['R_order']:<9} {rp_str} "
              f"{row['R_repeat']:<9} {row['R_model']:<9} {row['R_persona']:<10} "
              f"{row['SURS']:<7} {row['flag']}")
    
    # Summary
    n_high = sum(1 for _, r in surs_df.iterrows() if r['flag'] == 'High')
    n_mod = sum(1 for _, r in surs_df.iterrows() if r['flag'] == 'Moderate')
    n_low = sum(1 for _, r in surs_df.iterrows() if r['flag'] == 'Low')
    n_with_prompt = sum(1 for _, r in surs_df.iterrows() if r['R_prompt'] != 'n/a')
    print(f"\n  Summary: {n_high} High, {n_mod} Moderate, {n_low} Low")
    print(f"  Tests with R_prompt: {n_with_prompt}/{len(surs_df)}")
    
    # --- Figure: SURS histogram ---
    fig, ax = plt.subplots(figsize=(10, 5))
    colors_bar = []
    for _, r in surs_df.iterrows():
        if r['flag'] == 'High': colors_bar.append('#2ecc71')
        elif r['flag'] == 'Moderate': colors_bar.append('#f39c12')
        else: colors_bar.append('#e74c3c')
    
    ax.bar(range(len(surs_df)), surs_df['SURS'].values, color=colors_bar)
    ax.set_xticks(range(len(surs_df)))
    ax.set_xticklabels(surs_df['test_id'].values, rotation=45, ha='right')
    ax.axhline(y=0.8, color='#2ecc71', linestyle='--', alpha=0.7, label='High (>=0.8)')
    ax.axhline(y=0.6, color='#f39c12', linestyle='--', alpha=0.7, label='Moderate (>=0.6)')
    ax.set_ylabel('SURS Score')
    ax.set_title('Synthetic User Reliability Score per Test Case')
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'exp8_surs_scores.png'), dpi=300)
    plt.close()
    
    return surs_df


# ============================================================
# EXP 9: Full Pipeline Comparison
# ============================================================

def exp9_pipeline_comparison(df, output_dir):
    """Compare Raw vs Counterbalanced vs Ensemble vs Full CSUP"""
    print("\n" + "="*60)
    print("EXP 9: Full Pipeline Comparison (Raw vs CSUP)")
    print("="*60)
    
    models = sorted(df['model'].unique())
    n_models = len(models)
    tests = sorted(df['test_id'].unique())
    orig = df[df['ab_order'] == 'original']
    swap = df[df['ab_order'] == 'swapped']
    
    conditions = {}
    
    # --- Condition 1: Raw (1 model, 1 run, original order) ---
    # Use first model alphabetically, run 1
    first_model = models[0]
    raw_df = orig[(orig['model'] == first_model) & (orig['run_number'] == 1)]
    raw_prefs = raw_df.groupby('test_id')['choice_A'].mean()
    conditions['Raw single'] = raw_prefs
    
    # --- Condition 2: Counterbalanced (1 model, 2 runs averaged) ---
    orig_1m = orig[orig['model'] == first_model].groupby('test_id')['choice_A'].mean()
    swap_1m = swap[swap['model'] == first_model].groupby('test_id')['choice_A'].mean()
    common = orig_1m.index.intersection(swap_1m.index)
    counter_prefs = (orig_1m.loc[common] + (1 - swap_1m.loc[common])) / 2
    conditions['Counterbalanced'] = counter_prefs
    
    # --- Condition 3: Ensemble (all models, majority vote) ---
    votes = df.groupby(['test_id', 'persona_id', 'model'])['choice_A'].agg(
        lambda x: 1 if x.mean() > 0.5 else 0
    ).reset_index()
    votes.columns = ['test_id', 'persona_id', 'model', 'vote']
    pivot = votes.pivot_table(index=['test_id', 'persona_id'],
                              columns='model', values='vote').dropna()
    ensemble_vote = (pivot.sum(axis=1) > n_models/2).astype(int)
    ensemble_prefs = ensemble_vote.groupby('test_id').mean()
    conditions['Ensemble'] = ensemble_prefs
    
    # --- Condition 4: Full CSUP (ensemble + counterbalance) ---
    # Use counterbalanced per model, then ensemble
    csup_votes = {}
    for m in models:
        orig_m = orig[orig['model'] == m].groupby(['test_id', 'persona_id'])['choice_A'].mean()
        swap_m = swap[swap['model'] == m].groupby(['test_id', 'persona_id'])['choice_A'].mean()
        common_m = orig_m.index.intersection(swap_m.index)
        counter_m = (orig_m.loc[common_m] + (1 - swap_m.loc[common_m])) / 2
        csup_votes[m] = (counter_m > 0.5).astype(int)
    
    csup_df = pd.DataFrame(csup_votes).dropna()
    csup_ensemble = (csup_df.sum(axis=1) > n_models/2).astype(int)
    csup_prefs = csup_ensemble.groupby('test_id').mean()
    conditions['Full CSUP'] = csup_prefs
    
    # --- Compare variance across conditions ---
    print(f"\n  {'Condition':<20} {'Mean P(A)':<12} {'Std P(A)':<12} {'Range'}")
    print(f"  {'-'*56}")
    for name, prefs in conditions.items():
        print(f"  {name:<20} {prefs.mean():.3f}       {prefs.std():.3f}       "
              f"[{prefs.min():.2f}, {prefs.max():.2f}]")
    
    # --- Figure: pipeline comparison ---
    fig, axes = plt.subplots(1, 4, figsize=(16, 4), sharey=True)
    for ax, (name, prefs) in zip(axes, conditions.items()):
        common_tests = sorted(set(prefs.index) & set(tests))
        vals = [prefs.get(t, 0.5) for t in common_tests]
        colors = ['#2ecc71' if v > 0.5 else '#e74c3c' for v in vals]
        ax.barh(range(len(common_tests)), vals, color=colors, alpha=0.8)
        ax.axvline(x=0.5, color='gray', linestyle='--', alpha=0.5)
        ax.set_xlim(0, 1)
        ax.set_title(name, fontsize=10)
        ax.set_yticks(range(len(common_tests)))
        ax.set_yticklabels(common_tests, fontsize=7)
    axes[0].set_ylabel('Test Case')
    fig.suptitle('Pipeline Comparison: P(A) per Test Case', fontsize=12)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'exp9_pipeline_comparison.png'), dpi=300)
    plt.close()
    
    return conditions


# ============================================================
# POSITION BIAS ANALYSIS (from B1 data)
# ============================================================

def analyze_position_bias(pb_df, output_dir):
    """Analyze B1 calibration data for position bias floor"""
    print("\n" + "="*60)
    print("B1 POSITION BIAS FLOOR (Calibration Phase)")
    print("="*60)
    
    models = sorted(pb_df['model'].unique())
    
    # Option 1 rate (first-listed option preference)
    print("\n  Option 1 Rate (first-listed):")
    for m in models:
        m_df = pb_df[pb_df['model'] == m]
        # Original: first option = A, Swapped: first option = B
        orig_m = m_df[m_df['ab_order'] == 'original']
        swap_m = m_df[m_df['ab_order'] == 'swapped']
        
        # Option 1 = A in original, B in swapped
        opt1_orig = orig_m['choice_A'].mean()  # chose A = chose option 1
        opt1_swap = 1 - swap_m['choice_A'].mean()  # chose B = chose option 1
        
        opt1_rate = (opt1_orig * len(orig_m) + opt1_swap * len(swap_m)) / (len(orig_m) + len(swap_m))
        print(f"    {m}: Option1 Rate = {opt1_rate:.4f} ({opt1_rate*100:.1f}%)")
    
    # Position stick: % of time model follows position vs content
    print("\n  Position Stick:")
    for m in models:
        m_df = pb_df[pb_df['model'] == m]
        orig_m = m_df[m_df['ab_order'] == 'original']
        swap_m = m_df[m_df['ab_order'] == 'swapped']
        
        # Compare same test_id across orders
        orig_by_test = orig_m.groupby('test_id')['choice_A'].mean()
        swap_by_test = swap_m.groupby('test_id')['choice_A'].mean()
        
        common = orig_by_test.index.intersection(swap_by_test.index)
        if len(common) == 0:
            print(f"    {m}: No common tests to compare")
            continue
        
        # Position stick = chose same POSITION (not same VARIANT)
        # If orig chose A and swap chose B → same position (chose first both times) → WAIT
        # Actually: if orig chose A (option 1) and swap chose A (but A is now option 2) → stuck to CONTENT
        # If orig chose A and swap chose B → stuck to POSITION (chose option 1 both times)
        
        # Per test: position_stick = corr between "chose A in orig" and "chose B in swap"
        stick_count = 0
        content_count = 0
        total = 0
        for t in common:
            # Multiple runs per test, use majority
            o_choice = 1 if orig_by_test[t] > 0.5 else 0  # majority chose A in original
            s_choice = 1 if swap_by_test[t] > 0.5 else 0  # majority chose A in swapped
            
            total += 1
            if o_choice == 1 and s_choice == 0:
                # Orig: A, Swap: B → followed position (both chose "first option")
                stick_count += 1
            elif o_choice == 0 and s_choice == 1:
                # Orig: B, Swap: A → followed position (both chose "second option")  
                stick_count += 1
            else:
                # Same choice regardless of position → followed content
                content_count += 1
        
        if total > 0:
            pos_stick = stick_count / total
            print(f"    {m}: Position Stick = {pos_stick*100:.1f}% (content = {content_count/total*100:.1f}%)")
    
    # Drift rate from 25-fold repeats
    print("\n  Internal Drift (from repeated B1 prompts):")
    for m in models:
        m_df = pb_df[pb_df['model'] == m]
        # Group by (test_id, ab_order) — each has ~25 repeats
        cells = m_df.groupby(['test_id', 'ab_order'])['choice_A'].agg(list)
        consistencies = []
        for choices in cells:
            if len(choices) >= 5:
                n_a = sum(choices)
                n_b = len(choices) - n_a
                c_intra = max(n_a, n_b) / len(choices)
                consistencies.append(c_intra)
        
        if consistencies:
            avg_c = np.mean(consistencies)
            drift = 1 - avg_c
            print(f"    {m}: C_intra = {avg_c*100:.2f}%, Drift = {drift*100:.2f}%")


# ============================================================
# RELIABILITY-ADJUSTED CI
# ============================================================

def compute_adjusted_ci(df, variance_pct, output_dir):
    """Compute reliability-adjusted confidence intervals"""
    print("\n" + "="*60)
    print("RELIABILITY-ADJUSTED CONFIDENCE INTERVALS")
    print("="*60)
    
    tests = sorted(df['test_id'].unique())
    
    # Inflation factor from non-semantic variance
    semantic_pct = variance_pct.get('Semantic (test case)', 50)
    noise_pct = 100 - semantic_pct
    inflation = np.sqrt(1 + noise_pct / 100)
    
    print(f"  Semantic variance: {semantic_pct:.1f}%")
    print(f"  Noise variance: {noise_pct:.1f}%")
    print(f"  Inflation factor: {inflation:.3f}")
    
    results = []
    for test_id in tests:
        t_df = df[df['test_id'] == test_id]
        p_a = t_df['choice_A'].mean()
        n = len(t_df)
        
        # Standard CI
        se_std = np.sqrt(p_a * (1 - p_a) / n)
        ci_std = (p_a - 1.96 * se_std, p_a + 1.96 * se_std)
        
        # Adjusted CI
        se_adj = se_std * inflation
        ci_adj = (p_a - 1.96 * se_adj, p_a + 1.96 * se_adj)
        
        results.append({
            'test_id': test_id,
            'P_A': round(p_a, 3),
            'CI_std': f"[{ci_std[0]:.3f}, {ci_std[1]:.3f}]",
            'CI_adj': f"[{ci_adj[0]:.3f}, {ci_adj[1]:.3f}]",
            'CI_std_width': round(ci_std[1] - ci_std[0], 3),
            'CI_adj_width': round(ci_adj[1] - ci_adj[0], 3),
        })
    
    ci_df = pd.DataFrame(results)
    avg_expansion = ci_df['CI_adj_width'].mean() / ci_df['CI_std_width'].mean()
    
    print(f"\n  Average CI expansion: {avg_expansion:.2f}× wider")
    print(f"\n  {'Test':<10} {'P(A)':<7} {'Standard CI':<22} {'Adjusted CI':<22}")
    print(f"  {'-'*61}")
    for _, r in ci_df.iterrows():
        print(f"  {r['test_id']:<10} {r['P_A']:<7} {r['CI_std']:<22} {r['CI_adj']:<22}")
    
    return ci_df


# ============================================================
# LATEX TABLE EXPORT
# ============================================================

def export_latex_tables(exp1_res, variance_pct, surs_df, ci_df, output_dir):
    """Export all key tables as LaTeX"""
    print("\n" + "="*60)
    print("EXPORTING LATEX TABLES")
    print("="*60)
    
    latex_dir = os.path.join(output_dir, 'latex_tables')
    os.makedirs(latex_dir, exist_ok=True)
    
    # Table 1: Pairwise agreement
    if exp1_res and 'pairwise' in exp1_res:
        t1 = pd.DataFrame(exp1_res['pairwise'])
        t1.to_latex(os.path.join(latex_dir, 'table1_agreement.tex'),
                    index=False, escape=False, caption='Inter-model agreement.',
                    label='tab:agreement')
        print("  ✓ table1_agreement.tex")
    
    # Table: Variance decomposition
    if variance_pct:
        t2 = pd.DataFrame([
            {'Component': k, '% Variance': f'{v:.1f}%'} 
            for k, v in variance_pct.items()
        ])
        t2.to_latex(os.path.join(latex_dir, 'table_variance.tex'),
                    index=False, escape=False)
        print("  ✓ table_variance.tex")
    
    # Table: SURS
    if surs_df is not None:
        surs_export = surs_df[['test_id', 'R_order', 'R_repeat', 'R_model', 'R_persona', 'SURS', 'flag']]
        surs_export.to_latex(os.path.join(latex_dir, 'table_surs.tex'),
                            index=False, escape=False)
        print("  ✓ table_surs.tex")
    
    # Table: Adjusted CI
    if ci_df is not None:
        ci_df.to_latex(os.path.join(latex_dir, 'table_adjusted_ci.tex'),
                       index=False, escape=False)
        print("  ✓ table_adjusted_ci.tex")


# ============================================================
# MAIN
# ============================================================

def main():
    parser = argparse.ArgumentParser(description='CSUP Analysis Pipeline')
    parser.add_argument('--db', required=True, help='Path to experiment.db')
    parser.add_argument('--output', default='./csup_results/', help='Output directory')
    args = parser.parse_args()
    
    os.makedirs(args.output, exist_ok=True)
    os.makedirs(os.path.join(args.output, 'figures'), exist_ok=True)
    
    fig_dir = os.path.join(args.output, 'figures')
    
    # Load data
    print("Loading data...")
    df = load_api_calls(args.db)
    pb_df = load_position_bias(args.db)
    
    # Run experiments
    exp1_res = exp1_overall_agreement(df, fig_dir)
    order_effects, r_order, flips, total = exp3_order_robustness(df, fig_dir)
    r_prompt_dict, v_prompt = exp4_prompt_robustness(df, fig_dir)
    exp5_repeat_stability(df, fig_dir)
    analyze_position_bias(pb_df, fig_dir)
    
    # Exp 2 with V_prompt from Exp 4
    components, variance_pct = exp2_variance_decomposition(
        df, fig_dir, v_prompt_value=v_prompt if v_prompt > 0 else None)
    
    consensus, rates, r_persona = exp6_persona_consistency(df, fig_dir)
    k1_res, ensemble_res = exp7_ensemble(df, fig_dir)
    surs_df = exp8_surs(df, r_order, r_persona, k1_res,
                        exp1_res['fleiss_kappa'], fig_dir,
                        r_prompt_dict=r_prompt_dict)
    conditions = exp9_pipeline_comparison(df, fig_dir)
    ci_df = compute_adjusted_ci(df, variance_pct, fig_dir)
    
    # Export LaTeX tables
    export_latex_tables(exp1_res, variance_pct, surs_df, ci_df, args.output)
    
    # Save SURS to CSV
    surs_df.to_csv(os.path.join(args.output, 'surs_scores.csv'), index=False)
    
    print("\n" + "="*60)
    print("ALL EXPERIMENTS COMPLETE")
    print("="*60)
    print(f"  Figures saved to: {fig_dir}/")
    print(f"  LaTeX tables saved to: {args.output}/latex_tables/")
    print(f"  SURS scores saved to: {args.output}/surs_scores.csv")


if __name__ == '__main__':
    main()
