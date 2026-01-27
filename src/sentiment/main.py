import json
from datetime import datetime
from config import NEWS_SOURCES, GROQ_API_KEY, OUTPUT_FILE
from nse_stocks import NSEStockLoader
from web_scraper import NewsScraper
from sentiment_analyzer import SentimentAnalyzer

class SentimentAnalysisEngine:
    def __init__(self):
        self.stock_loader = NSEStockLoader()
        self.scraper = NewsScraper(NEWS_SOURCES)
        self.analyzer = SentimentAnalyzer(GROQ_API_KEY)
        self.results = {}
    
    def run(self):
        """Main execution flow"""
        print("Starting NSE 500 Sentiment Analysis...")
        
        # Step 1: Load NSE 500 stocks
        print("\n1. Loading NSE 500 stocks...")
        stocks = self.stock_loader.load_nse_500()
        print(f"Loaded {len(stocks)} stocks")
        
        # Step 2: Scrape news
        print("\n2. Scraping news from sources...")
        articles = self.scraper.scrape_all()
        print(f"Scraped {len(articles)} articles")
        
        # Step 3: Filter last 24 hours
        print("\n3. Filtering articles from last 24 hours...")
        recent_articles = self.scraper.filter_last_24_hours(articles)
        print(f"Found {len(recent_articles)} recent articles")
        
        # Step 4: Process each article
        print("\n4. Analyzing sentiment for each article...")
        
        for idx, article in enumerate(recent_articles):
            print(f"Processing article {idx+1}/{len(recent_articles)}...")
            
            # Check if should exclude
            if self.analyzer.should_exclude_news(article.headline, article.content):
                continue
            
            # Find mentioned scrips
            mentioned_scrips = self.stock_loader.find_scrip_in_text(
                article.headline + " " + article.content
            )
            
            if not mentioned_scrips:
                continue
            
            # Analyze sentiment for each mentioned scrip
            for scrip in mentioned_scrips:
                company = self.stock_loader.get_company_name(scrip)
                
                analysis = self.analyzer.analyze_sentiment(
                    article.headline,
                    article.content,
                    scrip,
                    company
                )
                
                # Store result
                if scrip not in self.results:
                    self.results[scrip] = {
                        "scrip": scrip,
                        "company": company,
                        "news_analysis": {
                            "news": [],
                            "overall_sentiment": "Neutral"
                        }
                    }
                
                news_item = {
                    "Date": article.date,
                    "Time": article.time,
                    "headline": article.headline,
                    "link": article.link,
                    "impact": analysis.get("impact", "Neutral"),
                    "severity": analysis.get("severity", "Unknown")
                }
                
                self.results[scrip]["news_analysis"]["news"].append(news_item)
                
                # Update overall sentiment
                self.results[scrip]["news_analysis"]["overall_sentiment"] = \
                    analysis.get("overall_sentiment", "Neutral")
        
        # Step 5: Generate output
        print("\n5. Generating output JSON...")
        self.generate_output()
        
        print(f"\n✓ Analysis complete! Results saved to {OUTPUT_FILE}")
        print(f"Total stocks with news: {len(self.results)}")
    
    def generate_output(self):
        """Generate downloadable JSON file"""
        output_list = list(self.results.values())
        
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(output_list, f, indent=2, ensure_ascii=False)
        
        print(f"Output saved to: {OUTPUT_FILE}")

def main():
    engine = SentimentAnalysisEngine()
    engine.run()

if __name__ == "__main__":
    main()
