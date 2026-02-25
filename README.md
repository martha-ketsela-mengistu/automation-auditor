# Automaton Auditor

AI-powered code review system using multi-agent debate.

## Setup

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and setup
git clone https://github.com/martha-ketsela-mengistu/automation-auditor
cd automation-auditor
uv venv
source .venv/bin/activate
uv pip install -e .

# Copy environment variables
cp .env.example .env
# Edit .env with your API keys
```

## Basic Usage
Run an audit against a GitHub repository and its accompanying PDF report:

```bash
python -m src.main --repo-url "https://github.com/martha-ketsela-mengistu/automation-auditor" --pdf-path "./reports/interim_report.pdf"
```