# TradingAgents Web Interface

Streamlit-based web interface for TradingAgents.

## Quick Start

```bash
# Install Streamlit
pip install streamlit

# Run the web app
streamlit run web/app.py
```

## Features

- Interactive ticker and date selection
- Multi-LLM provider support
- Real-time analysis progress
- Organized report display with tabs
- Bull/Bear debate visualization
- Risk management breakdown

## Configuration

Set your API keys in `.env` file:
```
OPENAI_API_KEY=your_key
GOOGLE_API_KEY=your_key
ANTHROPIC_API_KEY=your_key
...
```

## Usage

1. Select ticker symbol (e.g., NVDA, AAPL)
2. Choose analysis date
3. Select LLM provider and models
4. Choose analyst team
5. Click "Start Analysis"
6. View results in organized tabs

## Tips

- Use `gpt-5.4-mini` for faster analysis
- Increase debate rounds for deeper analysis
- Select fewer analysts for quicker results