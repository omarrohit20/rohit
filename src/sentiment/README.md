# NSE 500 Stock Sentiment Analysis

Automated sentiment analysis for NSE 500 stocks using web scraping and Groq LLM.

## Features

- Scrapes news from Zerodha Pulse and MoneyControl
- Analyzes sentiment using Groq's free LLM API
- Filters news from last 24 hours
- Excludes irrelevant news (top gainers/losers, already factored in)
- Includes sectoral and quarterly result news
- Generates structured JSON output

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set Groq API key:
```bash
export GROQ_API_KEY="your-api-key-here"
```

Or edit `config.py` directly.

3. Run the analysis:
```bash
python main.py
```

## Output Format

```json
[
  {
    "scrip": "TATASTEEL",
    "company": "Tata Steel Ltd.",
    "news_analysis": {
      "news": [
        {
          "Date": "2025-01-15",
          "Time": "10:30:00",
          "headline": "Tata Steel announces expansion plan",
          "link": "https://example.com/news",
          "impact": "Positive",
          "severity": "High"
        }
      ],
      "overall_sentiment": "Positive"
    }
  }
]
```

## Configuration

Edit `config.py` to customize:
- News sources
- API keys
- Exclusion keywords
- Output file path

## Notes

- Respects rate limits with delays between requests
- Uses free Groq API (llama-3.1-70b-versatile model)
- Sample NSE 500 list included - replace with actual data source
