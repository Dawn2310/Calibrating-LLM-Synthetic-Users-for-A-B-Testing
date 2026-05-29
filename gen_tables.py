import json
import os

with open('ab_tests/corpus_candidates.json', 'r', encoding='utf-8') as f:
    base = json.load(f)
with open('ab_tests/corpus_exp4.json', 'r', encoding='utf-8') as f:
    exp4 = json.load(f)

all_tests = base + exp4
all_tests.sort(key=lambda x: x['test_id'])

md_content = '# Full 33 Scenarios / Variants\n\n'
md_content += '| Test ID | Product Context | Variant A | Variant B | Metric |\n'
md_content += '|---|---|---|---|---|\n'
for t in all_tests:
    ctx = t['product_context'].replace('\n', ' ')
    va = t['variant_a'].replace('\n', ' ')
    vb = t['variant_b'].replace('\n', ' ')
    met = t['metric'].replace('\n', ' ')
    tid = t['test_id']
    md_content += f'| {tid} | {ctx} | {va} | {vb} | {met} |\n'

with open('analysis/csup_results/full_scenarios_variants_table.md', 'w', encoding='utf-8') as f:
    f.write(md_content)

tex_content = '''\\begin{table*}[h]
\\centering
\\scriptsize
\\renewcommand{\\arraystretch}{1.3}
\\begin{tabular}{p{1.5cm} p{3.5cm} p{4cm} p{4cm} p{2cm}}
\\toprule
\\textbf{Test ID} & \\textbf{Product Context} & \\textbf{Variant A} & \\textbf{Variant B} & \\textbf{Metric} \\\\
\\midrule
'''
for t in all_tests:
    ctx = t['product_context'].replace('%', '\\%').replace('&', '\\&').replace('#', '\\#').replace('$', '\\$').replace('\n', ' ')
    va = t['variant_a'].replace('%', '\\%').replace('&', '\\&').replace('#', '\\#').replace('$', '\\$').replace('\n', ' ')
    vb = t['variant_b'].replace('%', '\\%').replace('&', '\\&').replace('#', '\\#').replace('$', '\\$').replace('\n', ' ')
    met = t['metric'].replace('%', '\\%').replace('&', '\\&').replace('#', '\\#').replace('$', '\\$').replace('\n', ' ')
    tid = t['test_id']
    tex_content += f'{tid} & {ctx} & {va} & {vb} & {met} \\\\\n\\midrule\n'

tex_content += '''\\bottomrule
\\end{tabular}
\\caption{Full 33 Base Scenarios and Variants Used in Experiments}
\\label{tab:full_scenarios}
\\end{table*}
'''

os.makedirs('analysis/csup_results/latex_tables', exist_ok=True)
with open('analysis/csup_results/latex_tables/table_appendix_scenarios.tex', 'w', encoding='utf-8') as f:
    f.write(tex_content)
