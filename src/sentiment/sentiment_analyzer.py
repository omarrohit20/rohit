from groq import Groq
import json
from config import GROQ_API_KEY, GROQ_MODEL, EXCLUDE_KEYWORDS

class SentimentAnalyzer:
    def __init__(self, api_key):
        self.client = Groq(api_key=api_key)
        self.model = GROQ_MODEL
    
    def should_exclude_news(self, headline, content):
        """Check if news should be excluded"""
        text = (headline + " " + content).lower()
        
        for keyword in EXCLUDE_KEYWORDS:
            if keyword.lower() in text:
                return True
        
        # Check for "already factored in" patterns
        factored_patterns = [
            "already priced in",
            "factored in",
            "market expected",
            "as expected"
        ]
        
        for pattern in factored_patterns:
            if pattern in text:
                return True
        
        # Exclude price movement news (shares fall, surge, rise, etc.)
        price_movement_patterns = [
            "share price falls",
            "share price fall",
            "shares fall",
            "shares falls",
            "stock falls",
            "stock fall",
            "share price surge",
            "share price surges",
            "shares surge",
            "shares surges",
            "stock surge",
            "stock surges",
            "share price rise",
            "share price rises",
            "shares rise",
            "shares rises",
            "stock rise",
            "stock rises",
            "share price gains",
            "shares gain",
            "stock gains",
            "share price drops",
            "shares drop",
            "stock drops",
            "share price decline",
            "shares decline",
            "stock declines",
            "share price tumbles",
            "shares tumble",
            "stock tumbles",
            "share price slips",
            "shares slip",
            "stock slips",
            "share price jumps",
            "shares jump",
            "stock jumps",
            "share price climbs",
            "shares climb",
            "stock climbs",
            "share price soars",
            "shares soar",
            "stock soars",
            "share price plunges",
            "shares plunge",
            "stock plunges",
            "share price rallies",
            "shares rally",
            "stock rallies",
            "share price tanks",
            "shares tank",
            "stock tanks",
            "hits 52-week high",
            "hits 52-week low",
            "all-time high",
            "all-time low",
            "day's high",
            "day's low",
            "amid volume surge",
            "volume buzzers"
        ]
        
        for pattern in price_movement_patterns:
            if pattern in text:
                return True
        
        # Exclude market-wide index movement news
        market_index_patterns = [
            "sensex sinks",
            "sensex sink",
            "sensex tumbles",
            "sensex tumble",
            "sensex falls",
            "sensex fall",
            "sensex drops",
            "sensex drop",
            "sensex plunges",
            "sensex plunge",
            "sensex slides",
            "sensex slide",
            "sensex declines",
            "sensex decline",
            "nifty sinks",
            "nifty sink",
            "nifty tumbles",
            "nifty tumble",
            "nifty falls",
            "nifty fall",
            "nifty drops",
            "nifty drop",
            "nifty plunges",
            "nifty plunge",
            "nifty slides",
            "nifty slide",
            "nifty declines",
            "nifty decline",
            "biggest weekly drop",
            "biggest weekly decline",
            "biggest weekly fall",
            "largest weekly drop",
            "largest weekly decline",
            "biggest daily drop",
            "biggest daily decline",
            "bears regain",
            "bears regain control",
            "bears take control",
            "bear market",
            "bull market",
            "market selloff",
            "market correction",
            "broader indices",
            "broader market",
            "indices log",
            "indices slide",
            "indices fall",
            "indices drop",
            "indices decline",
            "market volatility",
            "volatile week",
            "volatile session",
            "closing bell",
            "market closing",
            "market opening",
            "opening bell",
            "market snapshot",
            "market wrap",
            "weekly decline",
            "weekly drop",
            "weekly fall",
            "weekly loss"
        ]
        
        for pattern in market_index_patterns:
            if pattern in text:
                return True
        
        return False
    
    def analyze_sentiment(self, headline, content, scrip, company):
        """Analyze sentiment using Groq LLM"""
        
        prompt = f"""
Analyze the following news article about {company} ({scrip}) stock:

Headline: {headline}
Content: {content}

Provide analysis in JSON format:
{{
    "impact": "Positive|Negative|Neutral",
    "severity": "High|Medium|Low|Unknown",
    "reasoning": "Brief explanation",
    "is_sectoral": true|false,
    "is_quarterly_result": true|false,
    "overall_sentiment": "Positive|Negative|Neutral"
}}

Consider:
1. Impact on stock price (Positive/Negative/Neutral)
2. Severity of impact (High/Medium/Low/Unknown)
3. Whether it's sectoral news affecting multiple companies
4. Whether it's about quarterly results
5. Overall sentiment

Respond only with valid JSON.
"""
        
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a financial analyst expert in stock market sentiment analysis. Provide concise, accurate analysis."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=self.model,
                temperature=0.3,
                max_tokens=500
            )
            
            response = chat_completion.choices[0].message.content
            
            # Extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                analysis = json.loads(json_str)
                return analysis
            else:
                return self._default_analysis()
                
        except Exception as e:
            print(f"Error analyzing sentiment: {e}")
            return self._default_analysis()
    
    def _default_analysis(self):
        """Return default analysis when API fails"""
        return {
            "impact": "Neutral",
            "severity": "Unknown",
            "reasoning": "Unable to analyze",
            "is_sectoral": False,
            "is_quarterly_result": False,
            "overall_sentiment": "Neutral"
        }
