# CSUP — Calibrated Synthetic-User Pipeline for LLM-Based A/B Testing

> **Research question:** Can LLM synthetic users produce reliable A/B test signals — and how do we know when they can't?

CSUP treats every LLM-generated A/B choice as a **noisy measurement** rather than a clean preference. It decomposes, controls, and reports the uncertainty behind synthetic-user judgments so that practitioners know which results to trust and which to escalate to human testing.

---

## Project Structure

```
├── ab_tests/
│   ├── corpus_candidates.json          # 23 base A/B test scenarios (UI/UX, Copy, Rec)
│   └── corpus_exp4.json                # 10 prompt-variant test cases (V2/V3)
├── personas/
│   ├── demographic.json                # 20 personas — short attribute labels
│   ├── biographical.json               # 20 personas — narrative descriptions
│   └── interview.json                  # 20 personas — first-person interview style
├── data/
│   ├── experiment.db                   # SQLite database (generated at runtime)
│   └── human/                          # Human validation data (reserved)
├── references/
│   ├── ab_test_corpus_redesigned.xlsx   # Original test-case design spreadsheet
│   ├── human_survey_en_vi_complete.xlsx # Human survey reference
│   ├── metadata.csv                    # Reference image metadata
│   └── <platform>/                     # Screenshot references (amazon, shopee, …)
├── scripts/
│   ├── csup_analysis.py                # CSUP pipeline — 9 experiments, SURS, CI
│   ├── run_analysis.py                 # Descriptive analysis & visualisation
│   ├── statistical_analysis.py         # Fleiss' κ, Krippendorff's α, mixed-effects
│   ├── gap_analysis.py                 # Position bias, drift, convergence analysis
│   ├── select_test_cases.py            # Test-case selection for prompt experiments
│   └── migrate_db.py                   # Database schema migration utility
├── analysis/
│   ├── figures/                        # Descriptive charts (PNG)
│   ├── tables/                         # Statistical tables (CSV / TXT)
│   └── csup_results/                   # CSUP output (figures, LaTeX tables, SURS)
├── pipeline.py                         # Core experiment runner (async, 4 models)
├── init_db.py                          # Database schema initialiser
├── export_results.py                   # Export DB → CSV / Excel + summary stats
├── gen_tables.py                       # LaTeX appendix table generator
├── run_all.ps1                         # One-click batch runner (PowerShell)
├── requirements.txt                    # Python dependencies
└── README.md
```

---

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Set API keys

```powershell
# Windows PowerShell
$env:OPENAI_API_KEY    = "sk-..."
$env:ANTHROPIC_API_KEY = "sk-ant-..."
$env:TOGETHER_API_KEY  = "tgp_v1_..."
$env:DEEPSEEK_API_KEY  = "sk-..."
```

### 3. Initialise the database

```bash
python init_db.py
```

### 4. Run experiment phases

```bash
# Position-bias calibration (no persona)
python pipeline.py --phase position_bias

# Full experiment (3 persona depths × 4 models × 3 runs)
python pipeline.py --phase full

# Individual persona levels
python pipeline.py --phase b3   # Demographic
python pipeline.py --phase b4   # Biographical
python pipeline.py --phase b5   # Interview

# Prompt-robustness experiment (Exp 4)
python pipeline.py --phase exp4

# Repeat-stability experiment (Exp 5)
python pipeline.py --phase exp5
```

### 5. Export & analyse results

```bash
# Export raw data
python export_results.py

# Descriptive analysis
python scripts/run_analysis.py
python scripts/statistical_analysis.py
python scripts/gap_analysis.py

# CSUP analysis (9 experiments)
python scripts/csup_analysis.py --db data/experiment.db --output analysis/csup_results

# Generate LaTeX appendix table
python gen_tables.py
```

Or run everything at once:

```powershell
.\run_all.ps1
```

---

## Models

| Model | Provider | Endpoint |
|---|---|---|
| GPT-4o | OpenAI | `api.openai.com` |
| Claude 3.5 Sonnet | Anthropic | `api.anthropic.com` |
| Llama 3.3 70B | Together AI | `api.together.xyz` |
| DeepSeek-V4-Flash | DeepSeek | `api.deepseek.com` |

---

## Experiment Design

### Data Collection (~32,000 API calls across 33 test cases)

| Phase | Conditions | Calls |
|---|---|---|
| Position-bias calibration | 23 tests × 4 models × 25 runs × 2 orders | ~4,600 |
| Full persona experiment | 23 tests × 60 personas × 4 models × 3 runs | ~16,560 |
| Prompt robustness (Exp 4) | 10 variants × 60 personas × 4 models × 3 runs | ~7,200 |
| Repeat stability (Exp 5) | 5 tests × 60 personas × 4 models × 6 extra runs | ~7,200 |

### Counterbalancing

Each A/B comparison is run under three order conditions:

1. **Run 1** — Original order (A presented first)
2. **Run 2** — Swapped order (B presented first)
3. **Run 3** — Random order

---

## Key Findings

### Variance Decomposition

| Source | Share of total variance |
|---|---|
| Semantic design signal | 32.2% |
| Repeat sampling | 25.1% |
| Prompt wording | 24.3% |
| Display order | 7.5% |
| Model family | 5.4% |
| Persona depth | 5.5% |

> Prompt wording and repeat sampling together explain ~50% of variance — raw LLM A/B testing can measure noise rather than design quality.

### Calibration Pipeline

| Stage | Std P(A) |
|---|---|
| Raw single-model output | 0.333 |
| + Counterbalancing | 0.090 |
| + Ensemble aggregation | 0.320 |
| Full CSUP pipeline | **0.075** |

### SURS — Synthetic User Reliability Score

| Rating | Count | Description |
|---|---|---|
| High | 4 | Highly reliable — safe to trust |
| Moderate | 24 | Usable with caveats |
| Low | 5 | Unreliable — escalate to human testing |

### Persona Depth (Hallucination of Depth)

| Persona type | Full 4-model consensus |
|---|---|
| Demographic | 71.1% |
| Biographical | 62.7% |
| Interview-style | 65.5% |

> Richer personas reduce cross-model consensus rather than improving it.

### Multi-Model Ensemble

| Ensemble size (k) | Avg agreement with full |
|---|---|
| k=1 (single model) | 0.901–0.945 |
| k=2 | 0.924 |
| k=3 | 0.943 |
| k=4 (full) | 1.000 |

---

## Technical Notes

- **SQLite checkpointing** — the pipeline can be safely interrupted and resumed at any time.
- **Relative paths** — the project runs on any machine without path changes.
- **Rate limiting** — handled automatically with exponential backoff and configurable concurrency.
- **Run numbers** — `run_number` supports 1–9 (runs 4–9 are used for repeat-stability experiments).
- **DeepSeek reasoning model** — `deepseek-v4-flash` uses chain-of-thought internally; `max_tokens` is set to 512 to accommodate reasoning tokens.

---

## Citation

If you use CSUP in your research, please cite:

```
@inproceedings{csup2026,
  title     = {From Synthetic Users to Calibrated Instruments: Decomposing Uncertainty in LLM-Based A/B Testing},
  author    = {Anonymous},
  booktitle = {HCOMP 2026},
  year      = {2026}
}
```

---

## License

MIT
