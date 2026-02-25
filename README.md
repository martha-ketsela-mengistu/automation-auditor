# Automaton Auditor

AI-powered code review system using multi-agent debate.

## Setup

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and setup
git clone <your-repo>
cd automaton-auditor
uv venv
source .venv/bin/activate
uv pip install -e .

# Copy environment variables
cp .env.example .env
# Edit .env with your API keys