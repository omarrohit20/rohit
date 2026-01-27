import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from dateutil import parser
import time
import re

class NewsArticle:
    def __init__(self, headline, link, date=None, time_str=None, content=""):
        self.headline = headline
        self.link = link
        self.date = date or datetime.now().strftime("%Y-%m-%d")
        self.time = time_str or datetime.now().strftime("%H:%M:%S")
        self.content = content

class NewsScraper:
    def __init__(self, sources):
        self.sources = sources
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def scrape_zerodha_pulse(self, url):
        """Scrape news from Zerodha Pulse"""
        articles = []
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find article containers (adjust selectors based on actual site structure)
            news_items = soup.find_all(['article', 'div'], class_=re.compile('post|article|news'))
            
            for item in news_items[:50]:  # Limit to recent articles
                try:
                    headline_elem = item.find(['h2', 'h3', 'a'])
                    if not headline_elem:
                        continue
                    
                    headline = headline_elem.get_text(strip=True)
                    link = headline_elem.get('href') or item.find('a')['href']
                    
                    if not link.startswith('http'):
                        link = f"https://pulse.zerodha.com{link}"
                    
                    date_elem = item.find(['time', 'span'], class_=re.compile('date|time'))
                    date_str = date_elem.get_text(strip=True) if date_elem else ""
                    
                    content = item.get_text(strip=True)[:500]
                    
                    articles.append(NewsArticle(headline, link, content=content))
                except Exception as e:
                    continue
                    
        except Exception as e:
            print(f"Error scraping Zerodha Pulse: {e}")
        
        return articles
    
    def scrape_moneycontrol(self, url):
        """Scrape news from MoneyControl"""
        articles = []
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # MoneyControl specific selectors
            news_items = soup.find_all('li', class_=re.compile('clearfix'))
            
            for item in news_items:
                try:
                    headline_elem = item.find('h2') or item.find('a')
                    if not headline_elem:
                        continue
                    
                    headline = headline_elem.get_text(strip=True)
                    link_elem = item.find('a')
                    link = link_elem['href'] if link_elem else ""
                    
                    if not link.startswith('http'):
                        link = f"https://www.moneycontrol.com{link}"
                    
                    date_elem = item.find('span', class_=re.compile('date|time'))
                    
                    content = item.get_text(strip=True)[:500]
                    
                    articles.append(NewsArticle(headline, link, content=content))
                except Exception as e:
                    continue
                    
        except Exception as e:
            print(f"Error scraping MoneyControl: {e}")
        
        return articles
    
    def scrape_all(self):
        """Scrape all configured news sources"""
        all_articles = []
        
        for source in self.sources:
            print(f"Scraping: {source}")
            
            if 'zerodha' in source:
                articles = self.scrape_zerodha_pulse(source)
            elif 'moneycontrol' in source:
                articles = self.scrape_moneycontrol(source)
            else:
                continue
            
            all_articles.extend(articles)
            time.sleep(2)  # Be respectful to servers
        
        return all_articles
    
    def filter_last_24_hours(self, articles):
        """Filter articles from last 24 hours"""
        cutoff_time = datetime.now() - timedelta(hours=24)
        filtered = []
        
        for article in articles:
            try:
                article_date = parser.parse(article.date)
                if article_date >= cutoff_time:
                    filtered.append(article)
            except:
                # If date parsing fails, include article
                filtered.append(article)
        
        return filtered
