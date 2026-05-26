# Anchoring Silicon Users: A/B Test Experiment Pipeline

> **Research Question:** Does the richness of persona descriptions (Demographic → Biographical → Interview) change how LLMs make A/B test decisions?

## Project Structure

```
├── ab_tests/
│   └── corpus_candidates.json        # 23 UI/UX A/B test scenarios
├── personas/
│   ├── demographic.json              # 20 personas — short labels (5–11 words)
│   ├── biographical.json             # 20 personas — narrative (45–55 words)
│   └── interview.json                # 20 personas — interview transcript (105–127 words)
├── data/
│   └── experiment.db                 # SQLite database (generated at runtime)
├── references/
│   ├── ab_test_corpus_redesigned.xlsx # Original test-case spreadsheet
│   ├── human_survey_en_vi_complete.xlsx
│   ├── metadata.csv                  # Reference image metadata
│   └── <platform>/                   # Screenshot references (amazon, shopee, …)
├── scripts/
│   ├── run_analysis.py               # Descriptive analysis & visualisation
│   ├── statistical_analysis.py       # Fleiss' κ, Krippendorff's α, mixed-effects model
│   └── gap_analysis.py               # Gap 1–3 analysis (position bias, drift, convergence)
├── analysis/
│   ├── figures/                      # Generated charts (PNG)
│   └── tables/                       # Computed statistical tables (CSV/TXT)
├── pipeline.py                       # Core experiment runner (async, 4 models)
├── init_db.py                        # Database schema initialiser
├── export_results.py                 # Export DB → CSV/Excel + summary stats
├── run_all.ps1                       # One-click batch runner (PowerShell)
├── requirements.txt                  # Python dependencies
└── README.md                         # This file
```

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set API Keys

Set the following environment variables before running:

**Windows (PowerShell):**
```powershell
$env:OPENAI_API_KEY    = "sk-..."
$env:ANTHROPIC_API_KEY = "sk-ant-..."
$env:TOGETHER_API_KEY  = "tgp_v1_..."
$env:DEEPSEEK_API_KEY  = "sk-..."
```

**Linux / macOS:**
```bash
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export TOGETHER_API_KEY="tgp_v1_..."
export DEEPSEEK_API_KEY="sk-..."
```

### 3. Initialise Database

```bash
python init_db.py
```

### 4. Run Experiment Phases

```bash
# Phase 1: Position Bias measurement (no persona)
python pipeline.py --phase position_bias

# Phase 2: Demographic personas (B3)
python pipeline.py --phase b3

# Phase 3: Biographical personas (B4)
python pipeline.py --phase b4

# Phase 4: Interview personas (B5)
python pipeline.py --phase b5
```

### 5. Export & Analyse Results

```bash
python export_results.py
python scripts/run_analysis.py
python scripts/statistical_analysis.py
python scripts/gap_analysis.py
```

Results are saved to `data/` (CSV/Excel) and `analysis/` (figures & tables).

## Models Used

| Model | Provider | API |
|---|---|---|
| GPT-4o | OpenAI | `api.openai.com` |
| Claude Sonnet 4.6 | Anthropic | `api.anthropic.com` |
| Llama 3.3 70B | Together AI | `api.together.xyz` |
| DeepSeek-V4-Flash | DeepSeek | `api.deepseek.com` |

## Experiment Design

- **23 test cases** × **20 personas** × **4 models** × **3 runs** = **5,520 calls per phase**
- **Position Bias:** 23 × 4 models × 25 runs × 2 orders = **4,600 calls**
- **Total dataset:** ~21,160 API calls

Each run uses a different A/B presentation order:
1. **Run 1:** Original order (A = control, B = variant)
2. **Run 2:** Swapped order (A = variant, B = control)
3. **Run 3:** Random order

## Key Findings

| Gap | Finding |
|---|---|
| **Gap 1 — Calibration Floor** | Without personas, models choose based on *position* 82–92% of the time (Recency Bias) |
| **Gap 2 — Hallucination of Depth** | Deeper personas *reduce* cross-model consensus (73.8% → 62.2%) |
| **Gap 3 — Consistency Ceiling** | Internal drift ranges from 0.43% (Claude) to 8.00% (DeepSeek) |

## Notes

- The pipeline uses **SQLite checkpointing** — you can safely interrupt and resume at any time.
- All file paths are **relative** — the project runs on any machine without path changes.
- Rate limiting is handled automatically with exponential backoff and configurable concurrency.
