$ErrorActionPreference = "Stop"

# Set API keys before running (do NOT commit real keys)
# $env:OPENAI_API_KEY = "your-key-here"
# $env:ANTHROPIC_API_KEY = "your-key-here"
# $env:TOGETHER_API_KEY = "your-key-here"
# $env:DEEPSEEK_API_KEY = "your-key-here"

Write-Host "Starting Position Bias phase..."
python -u pipeline.py --phase position_bias

Write-Host "Starting Full Persona phase..."
python -u pipeline.py --phase full

Write-Host "Running run_analysis.py..."
python -u scripts/run_analysis.py

Write-Host "Running statistical_analysis.py..."
python -u scripts/statistical_analysis.py

Write-Host "Running gap_analysis.py..."
python scripts/gap_analysis.py

Write-Host "ALL TASKS COMPLETED!"
