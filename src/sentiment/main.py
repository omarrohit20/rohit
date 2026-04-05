import json
from datetime import datetime
from config import NEWS_SOURCES, GROQ_API_KEY, OUTPUT_FILE
from nse_stocks import NSEStockLoader
from web_scraper import NewsScraper
from sentiment_analyzer import SentimentAnalyzer
from database import MongoDBHandler

class SentimentAnalysisEngine:
    def __init__(self, use_mongodb=True):
        self.stock_loader = NSEStockLoader()
        self.scraper = NewsScraper(NEWS_SOURCES)
        self.analyzer = SentimentAnalyzer(GROQ_API_KEY)
        self.results = {}
        self.use_mongodb = use_mongodb
        self.db_handler = None
        
        if self.use_mongodb:
            try:
                self.db_handler = MongoDBHandler(db_name="chartlink")
            except Exception as e:
                print(f"Warning: MongoDB connection failed. Will save to JSON only.")
                print(f"Error: {e}")
                self.use_mongodb = False
    
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
            
            # Analyze sentiment once for this article using the first mentioned scrip
            primary_scrip = mentioned_scrips[0]
            primary_company = self.stock_loader.get_company_name(primary_scrip)
            
            analysis = self.analyzer.analyze_sentiment(
                article.headline,
                article.content,
                primary_scrip,
                primary_company
            )
            
            # Determine target scrips
            all_target_scrips = set(mentioned_scrips)
            
            # Check if this is sectoral news
            is_sectoral = analysis.get("is_sectoral", False)
            severity = analysis.get("severity", "Unknown")
            
            if is_sectoral:
                # For sectoral news, only process if severity is High
                if severity != "High":
                    continue  # Skip this article for sectoral processing
                
                # Expand to all sector stocks
                mentioned_sectors = self.stock_loader.find_sector_in_text(
                    article.headline + " " + article.content
                )
                for sector in mentioned_sectors:
                    sector_stocks = self.stock_loader.get_sector_stocks(sector)
                    all_target_scrips.update(sector_stocks)
            
            # Apply this analysis to all target scrips
            for scrip in all_target_scrips:
                company = self.stock_loader.get_company_name(scrip)
                
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
                
                # Note: overall_sentiment will be calculated after all news are collected
        
        # Step 4.5: Calculate overall sentiment for each stock
        print("\n4.5. Calculating overall sentiment...")
        self.calculate_overall_sentiments()
        
        # Step 5: Generate output
        print("\n5. Generating output...")
        self.generate_output()
        
        # Step 6: Save to MongoDB
        if self.use_mongodb and self.db_handler:
            print("\n6. Saving to MongoDB...")
            self.save_to_mongodb()
        
        print(f"\n✓ Analysis complete!")
        print(f"Total stocks with news: {len(self.results)}")
        if self.use_mongodb:
            print(f"Data saved to MongoDB database 'chartlink'")
        print(f"JSON file saved to: {OUTPUT_FILE}")
    
    def generate_output(self):
        """Generate downloadable JSON file"""
        output_list = list(self.results.values())
        
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(output_list, f, indent=2, ensure_ascii=False)
        
        print(f"JSON output saved to: {OUTPUT_FILE}")
    
    def calculate_overall_sentiments(self):
        """Calculate overall sentiment for each stock based on news impact and severity"""
        for scrip, data in self.results.items():
            news_list = data["news_analysis"]["news"]
            
            has_high_positive = any(
                news.get("severity") == "High" and news.get("impact") == "Positive" 
                for news in news_list
            )
            has_high_negative = any(
                news.get("severity") == "High" and news.get("impact") == "Negative" 
                for news in news_list
            )
            
            if has_high_positive:
                overall_sentiment = "Positive"
            elif has_high_negative:
                overall_sentiment = "Negative"
            else:
                # If no high impact news, check for medium impact
                has_medium_positive = any(
                    news.get("severity") == "Medium" and news.get("impact") == "Positive" 
                    for news in news_list
                )
                has_medium_negative = any(
                    news.get("severity") == "Medium" and news.get("impact") == "Negative" 
                    for news in news_list
                )
                
                if has_medium_positive:
                    overall_sentiment = "Positive"
                elif has_medium_negative:
                    overall_sentiment = "Negative"
                else:
                    # Default to neutral or based on majority of low impact
                    positive_count = sum(1 for news in news_list if news.get("impact") == "Positive")
                    negative_count = sum(1 for news in news_list if news.get("impact") == "Negative")
                    
                    if positive_count > negative_count:
                        overall_sentiment = "Positive"
                    elif negative_count > positive_count:
                        overall_sentiment = "Negative"
                    else:
                        overall_sentiment = "Neutral"
            
            data["news_analysis"]["overall_sentiment"] = overall_sentiment
            data["last_updated"] = datetime.now().isoformat()
    
    def save_to_mongodb(self):
        """Save results to MongoDB"""
        if not self.db_handler:
            print("MongoDB handler not initialized")
            return
        
        try:
            success = self.db_handler.insert_sentiment_data(self.results)
            if success:
                print("✓ Data successfully saved to MongoDB")
            else:
                print("✗ Failed to save data to MongoDB")
        except Exception as e:
            print(f"Error saving to MongoDB: {e}")
            import traceback
            traceback.print_exc()
    
    def __del__(self):
        """Cleanup on destruction"""
        if self.db_handler:
            self.db_handler.close()

def main():
    engine = SentimentAnalysisEngine(use_mongodb=True)
    engine.run()

if __name__ == "__main__":
    main()
