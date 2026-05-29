$ErrorActionPreference = "Stop"

# Set API keys before running (do NOT commit real keys)
# $env:OPENAI_API_KEY = "your-key-here"
# $env:ANTHROPIC_API_KEY = "your-key-here"
# $env:TOGETHER_API_KEY = "your-key-here"
# $env:DEEPSEEK_API_KEY = "your-key-here"

# ============ TIER 1: Data Collection ============
Write-Host "=== TIER 1: DATA COLLECTION ==="

Write-Host "Starting Position Bias phase..."
python -u pipeline.py --phase position_bias

Write-Host "Starting Full Persona phase..."
python -u pipeline.py --phase full

# ============ TIER 2-3: Data Collection ============
Write-Host "`n=== TIER 2-3: DATA COLLECTION ==="

Write-Host "Starting Exp 4 (Prompt Robustness)..."
python -u pipeline.py --phase exp4

Write-Host "Starting Exp 5 (Repeat Stability)..."
python -u pipeline.py --phase exp5

# ============ TIER 1: Analysis ============
Write-Host "`n=== TIER 1: ANALYSIS ==="

Write-Host "Exporting results to CSV/Excel..."
python -u export_results.py

Write-Host "Running run_analysis.py..."
python -u scripts/run_analysis.py

Write-Host "Running statistical_analysis.py..."
python -u scripts/statistical_analysis.py

Write-Host "Running gap_analysis.py..."
python scripts/gap_analysis.py

# ============ TIER 2+3: CSUP Analysis ============
Write-Host "`n=== TIER 2+3: CSUP ANALYSIS ==="

Write-Host "Running CSUP analysis pipeline (9 experiments)..."
python scripts/csup_analysis.py --db data/experiment.db --output analysis/csup_results

Write-Host "`nALL TASKS COMPLETED!"

