import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from dateutil import parser
import time
import re
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

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
        self.seen_articles = set()  # Track seen articles to avoid duplicates
    
    def _is_duplicate(self, headline, link):
        """Check if article is a duplicate based on headline or link"""
        # Create a unique key from headline and link
        headline_key = headline.lower().strip()
        link_key = link.lower().strip()
        
        # Check if we've seen this exact headline or link
        if headline_key in self.seen_articles or link_key in self.seen_articles:
            return True
        
        # Add to seen set
        self.seen_articles.add(headline_key)
        self.seen_articles.add(link_key)
        
        return False
    
    def scrape_zerodha_pulse(self, url):
        """Scrape news from Zerodha Pulse using Playwright"""
        articles = []
        
        try:
            with sync_playwright() as p:
                print("Launching browser for Zerodha Pulse...")
                
                # Launch browser (headless mode)
                browser = p.chromium.launch(headless=True)
                
                # Create context with user agent
                context = browser.new_context(
                    user_agent=self.headers['User-Agent'],
                    viewport={'width': 1920, 'height': 1080}
                )
                
                # Create new page
                page = context.new_page()
                
                print(f"Loading {url}...")
                
                # Navigate to URL with extended timeout
                page.goto(url, wait_until='domcontentloaded', timeout=30000)
                
                # Wait longer for JavaScript to render
                print("Waiting for content to load...")
                page.wait_for_timeout(5000)
                
                # Scroll to load more content (if lazy loading)
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(2000)
                
                # Get page content
                content = page.content()
                
                # Save HTML for debugging
                with open('zerodha_pulse_debug.html', 'w', encoding='utf-8') as f:
                    f.write(content)
                print("Saved page HTML to zerodha_pulse_debug.html for inspection")
                
                soup = BeautifulSoup(content, 'html.parser')
                
                # Try multiple selector strategies for Zerodha Pulse
                news_items = []
                
                # Strategy 1: Look for article tags
                news_items = soup.find_all('article')
                print(f"Strategy 1 (article tags): Found {len(news_items)} items")
                
                # Strategy 2: Look for div with post/item classes
                if not news_items:
                    news_items = soup.find_all('div', class_=re.compile('post|item|entry|feed-item'))
                    print(f"Strategy 2 (div.post/item): Found {len(news_items)} items")
                
                # Strategy 3: Look for list items
                if not news_items:
                    news_items = soup.find_all('li', class_=re.compile('post|item|entry'))
                    print(f"Strategy 3 (li.post/item): Found {len(news_items)} items")
                
                # Strategy 4: Look for any container with title/headline
                if not news_items:
                    news_items = soup.find_all(['div', 'section'], class_=re.compile('card|story|news'))
                    print(f"Strategy 4 (card/story/news): Found {len(news_items)} items")
                
                # Strategy 5: Find all links with headlines (last resort)
                if not news_items:
                    # Look for all h2, h3, h4 elements that might be headlines
                    headlines = soup.find_all(['h2', 'h3', 'h4'])
                    print(f"Strategy 5 (headline tags): Found {len(headlines)} potential headlines")
                    
                    for headline_elem in headlines[:50]:
                        try:
                            headline = headline_elem.get_text(strip=True)
                            if len(headline) < 10:
                                continue
                            
                            # Find parent container
                            parent = headline_elem.find_parent(['div', 'article', 'section', 'li'])
                            if parent:
                                news_items.append(parent)
                        except:
                            continue
                
                print(f"Total items to process: {len(news_items)}")
                
                duplicates_skipped = 0
                
                for idx, item in enumerate(news_items[:50]):
                    try:
                        # Find headline - try multiple strategies
                        headline_elem = (
                            item.find('h1') or 
                            item.find('h2') or 
                            item.find('h3') or 
                            item.find('h4') or
                            item.find('a', class_=re.compile('title|headline|link'))
                        )
                        
                        if not headline_elem:
                            continue
                        
                        headline = headline_elem.get_text(strip=True)
                        
                        # Skip if headline is too short
                        if not headline or len(headline) < 10:
                            continue
                        
                        # Find link
                        link = ""
                        link_elem = headline_elem.find('a') if headline_elem.name != 'a' else headline_elem
                        if not link_elem:
                            link_elem = item.find('a', href=True)
                        
                        if link_elem and link_elem.get('href'):
                            link = link_elem.get('href', '')
                            # Handle relative URLs
                            if link and not link.startswith('http'):
                                if link.startswith('/'):
                                    link = f"https://pulse.zerodha.com{link}"
                                elif link.startswith('#') or not link:
                                    link = url
                                else:
                                    link = f"https://pulse.zerodha.com/{link}"
                        else:
                            link = url
                        
                        # Check for duplicates
                        if self._is_duplicate(headline, link):
                            duplicates_skipped += 1
                            continue
                        
                        print(f"Article {idx+1}: {headline[:60]}...")
                        
                        # Find date/time - try multiple approaches
                        date_str = ""
                        date_elem = item.find('time')
                        if date_elem:
                            date_str = date_elem.get('datetime', '') or date_elem.get_text(strip=True)
                        
                        if not date_str:
                            date_elem = item.find(['span', 'div', 'p'], class_=re.compile('date|time|timestamp|published|meta'))
                            if date_elem:
                                date_str = date_elem.get_text(strip=True)
                        
                        # Get article content/summary
                        content = ""
                        content_elem = item.find(['p', 'div'], class_=re.compile('summary|excerpt|content|description|text|body'))
                        if content_elem:
                            content = content_elem.get_text(strip=True)[:500]
                        else:
                            # Get all paragraphs
                            paragraphs = item.find_all('p')
                            if paragraphs:
                                content = ' '.join([p.get_text(strip=True) for p in paragraphs[:3]])[:500]
                            else:
                                # Get all text from item, exclude headline
                                all_text = item.get_text(strip=True)
                                content = all_text.replace(headline, '', 1)[:500]
                        
                        # Parse date
                        article_date = datetime.now().strftime("%Y-%m-%d")
                        article_time = datetime.now().strftime("%H:%M:%S")
                        
                        if date_str:
                            try:
                                parsed_date = parser.parse(date_str, fuzzy=True)
                                article_date = parsed_date.strftime("%Y-%m-%d")
                                article_time = parsed_date.strftime("%H:%M:%S")
                            except:
                                pass
                        
                        articles.append(NewsArticle(
                            headline=headline,
                            link=link,
                            date=article_date,
                            time_str=article_time,
                            content=content
                        ))
                        
                    except Exception as e:
                        print(f"Error parsing article {idx+1}: {e}")
                        continue
                
                # Close browser
                browser.close()
                
                print(f"Successfully scraped {len(articles)} articles from Zerodha Pulse")
                if duplicates_skipped > 0:
                    print(f"Skipped {duplicates_skipped} duplicate articles")
                    
        except Exception as e:
            print(f"Error scraping Zerodha Pulse with Playwright: {e}")
            import traceback
            traceback.print_exc()
            print("Tip: Ensure Playwright is installed. Run: pip install playwright && playwright install chromium")
        
        return articles
    
    def scrape_moneycontrol(self, url):
        """Scrape news from MoneyControl"""
        articles = []
        duplicates_skipped = 0
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # MoneyControl has multiple possible selectors
            news_items = []
            
            # Strategy 1: Look for list items with clearfix
            news_items = soup.find_all('li', class_=re.compile('clearfix'))
            print(f"MoneyControl Strategy 1: Found {len(news_items)} items")
            
            # Strategy 2: Look for article containers
            if not news_items:
                news_items = soup.find_all(['div', 'article'], class_=re.compile('news|article|story'))
                print(f"MoneyControl Strategy 2: Found {len(news_items)} items")
            
            # Strategy 3: Look for news list items
            if not news_items:
                news_items = soup.find_all('li', class_=re.compile('item|post'))
                print(f"MoneyControl Strategy 3: Found {len(news_items)} items")
            
            for item in news_items[:50]:
                try:
                    headline_elem = item.find('h2') or item.find('h3') or item.find('a')
                    if not headline_elem:
                        continue
                    
                    headline = headline_elem.get_text(strip=True)
                    
                    if not headline or len(headline) < 10:
                        continue
                    
                    link_elem = item.find('a', href=True)
                    link = link_elem['href'] if link_elem else ""
                    
                    if link and not link.startswith('http'):
                        link = f"https://www.moneycontrol.com{link}"
                    
                    if not link:
                        link = url
                    
                    # Check for duplicates
                    if self._is_duplicate(headline, link):
                        duplicates_skipped += 1
                        continue
                    
                    # Find date
                    date_elem = item.find(['span', 'time', 'div'], class_=re.compile('date|time|timestamp'))
                    date_str = date_elem.get_text(strip=True) if date_elem else ""
                    
                    # Parse date
                    article_date = datetime.now().strftime("%Y-%m-%d")
                    article_time = datetime.now().strftime("%H:%M:%S")
                    
                    if date_str:
                        try:
                            parsed_date = parser.parse(date_str, fuzzy=True)
                            article_date = parsed_date.strftime("%Y-%m-%d")
                            article_time = parsed_date.strftime("%H:%M:%S")
                        except:
                            pass
                    
                    # Get content
                    content_elem = item.find('p')
                    content = content_elem.get_text(strip=True)[:500] if content_elem else item.get_text(strip=True)[:500]
                    
                    articles.append(NewsArticle(
                        headline=headline,
                        link=link,
                        date=article_date,
                        time_str=article_time,
                        content=content
                    ))
                except Exception as e:
                    continue
            
            print(f"Successfully scraped {len(articles)} articles from MoneyControl")
            if duplicates_skipped > 0:
                print(f"Skipped {duplicates_skipped} duplicate articles from MoneyControl")
                    
        except Exception as e:
            print(f"Error scraping MoneyControl: {e}")
            import traceback
            traceback.print_exc()
        
        return articles
    
    def scrape_ndtvprofit(self, url):
        """Scrape news from NDTV Profit"""
        articles = []
        duplicates_skipped = 0
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # NDTV Profit selectors
            news_items = soup.find_all(['article', 'div'], class_=re.compile('story|news|article|card'))
            
            print(f"NDTV Profit: Found {len(news_items)} items")
            
            for item in news_items[:50]:
                try:
                    headline_elem = item.find(['h1', 'h2', 'h3', 'h4'])
                    if not headline_elem:
                        continue
                    
                    headline = headline_elem.get_text(strip=True)
                    
                    if not headline or len(headline) < 10:
                        continue
                    
                    link_elem = headline_elem.find('a') or item.find('a', href=True)
                    link = link_elem['href'] if link_elem else ""
                    
                    if link and not link.startswith('http'):
                        if link.startswith('/'):
                            link = f"https://www.ndtvprofit.com{link}"
                        else:
                            link = f"https://www.ndtvprofit.com/{link}"
                    
                    if not link:
                        link = url
                    
                    # Check for duplicates
                    if self._is_duplicate(headline, link):
                        duplicates_skipped += 1
                        continue
                    
                    # Find date
                    date_elem = item.find(['span', 'time', 'div'], class_=re.compile('date|time|timestamp'))
                    date_str = date_elem.get_text(strip=True) if date_elem else ""
                    
                    # Parse date
                    article_date = datetime.now().strftime("%Y-%m-%d")
                    article_time = datetime.now().strftime("%H:%M:%S")
                    
                    if date_str:
                        try:
                            parsed_date = parser.parse(date_str, fuzzy=True)
                            article_date = parsed_date.strftime("%Y-%m-%d")
                            article_time = parsed_date.strftime("%H:%M:%S")
                        except:
                            pass
                    
                    # Get content
                    content_elem = item.find('p')
                    content = content_elem.get_text(strip=True)[:500] if content_elem else item.get_text(strip=True)[:500]
                    
                    articles.append(NewsArticle(
                        headline=headline,
                        link=link,
                        date=article_date,
                        time_str=article_time,
                        content=content
                    ))
                except Exception as e:
                    continue
            
            print(f"Successfully scraped {len(articles)} articles from NDTV Profit")
            if duplicates_skipped > 0:
                print(f"Skipped {duplicates_skipped} duplicate articles")
                    
        except Exception as e:
            print(f"Error scraping NDTV Profit: {e}")
        
        return articles
    
    def scrape_economictimes(self, url):
        """Scrape news from Economic Times"""
        articles = []
        duplicates_skipped = 0
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Economic Times selectors
            news_items = soup.find_all(['article', 'div'], class_=re.compile('story|news|article|eachStory'))
            
            print(f"Economic Times: Found {len(news_items)} items")
            
            for item in news_items[:50]:
                try:
                    headline_elem = item.find(['h1', 'h2', 'h3', 'h4'])
                    if not headline_elem:
                        continue
                    
                    headline = headline_elem.get_text(strip=True)
                    
                    if not headline or len(headline) < 10:
                        continue
                    
                    link_elem = headline_elem.find('a') or item.find('a', href=True)
                    link = link_elem['href'] if link_elem else ""
                    
                    if link and not link.startswith('http'):
                        if link.startswith('/'):
                            link = f"https://economictimes.indiatimes.com{link}"
                        else:
                            link = f"https://economictimes.indiatimes.com/{link}"
                    
                    if not link:
                        link = url
                    
                    # Check for duplicates
                    if self._is_duplicate(headline, link):
                        duplicates_skipped += 1
                        continue
                    
                    # Find date
                    date_elem = item.find(['span', 'time', 'div'], class_=re.compile('date|time|timestamp'))
                    date_str = date_elem.get_text(strip=True) if date_elem else ""
                    
                    # Parse date
                    article_date = datetime.now().strftime("%Y-%m-%d")
                    article_time = datetime.now().strftime("%H:%M:%S")
                    
                    if date_str:
                        try:
                            parsed_date = parser.parse(date_str, fuzzy=True)
                            article_date = parsed_date.strftime("%Y-%m-%d")
                            article_time = parsed_date.strftime("%H:%M:%S")
                        except:
                            pass
                    
                    # Get content
                    content_elem = item.find('p')
                    content = content_elem.get_text(strip=True)[:500] if content_elem else item.get_text(strip=True)[:500]
                    
                    articles.append(NewsArticle(
                        headline=headline,
                        link=link,
                        date=article_date,
                        time_str=article_time,
                        content=content
                    ))
                except Exception as e:
                    continue
            
            print(f"Successfully scraped {len(articles)} articles from Economic Times")
            if duplicates_skipped > 0:
                print(f"Skipped {duplicates_skipped} duplicate articles")
                    
        except Exception as e:
            print(f"Error scraping Economic Times: {e}")
        
        return articles
    
    def scrape_all(self):
        """Scrape all configured news sources"""
        all_articles = []
        
        for source in self.sources:
            print(f"\n{'='*60}")
            print(f"Scraping: {source}")
            print(f"{'='*60}")
            
            articles = []
            
            if 'zerodha' in source.lower() or 'pulse' in source.lower():
                articles = self.scrape_zerodha_pulse(source)
            elif 'moneycontrol' in source.lower():
                articles = self.scrape_moneycontrol(source)
            elif 'ndtvprofit' in source.lower() or 'ndtv' in source.lower():
                articles = self.scrape_ndtvprofit(source)
            elif 'economictimes' in source.lower():
                articles = self.scrape_economictimes(source)
            else:
                print(f"Warning: Unknown source format: {source}")
                print("Attempting generic scraping...")
                # Try generic scraping as fallback
                try:
                    articles = self._scrape_generic(source)
                except Exception as e:
                    print(f"Generic scraping failed: {e}")
                    continue
            
            all_articles.extend(articles)
            print(f"Total articles from this source: {len(articles)}")
            time.sleep(2)  # Be respectful to servers
        
        print(f"\n{'='*60}")
        print(f"SUMMARY: Total articles scraped: {len(all_articles)}")
        print(f"Unique articles after deduplication: {len(all_articles)}")
        print(f"{'='*60}\n")
        
        return all_articles
    
    def _scrape_generic(self, url):
        """Generic scraper for unknown sources"""
        articles = []
        duplicates_skipped = 0
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try to find articles using common patterns
            news_items = soup.find_all(['article', 'div'], class_=re.compile('story|news|article|post|item'))
            
            for item in news_items[:50]:
                try:
                    headline_elem = item.find(['h1', 'h2', 'h3', 'h4'])
                    if not headline_elem:
                        continue
                    
                    headline = headline_elem.get_text(strip=True)
                    
                    if not headline or len(headline) < 10:
                        continue
                    
                    link_elem = headline_elem.find('a') or item.find('a', href=True)
                    link = link_elem['href'] if link_elem else url
                    
                    if link and not link.startswith('http'):
                        base_url = '/'.join(url.split('/')[:3])
                        if link.startswith('/'):
                            link = f"{base_url}{link}"
                        else:
                            link = f"{base_url}/{link}"
                    
                    # Check for duplicates
                    if self._is_duplicate(headline, link):
                        duplicates_skipped += 1
                        continue
                    
                    content = item.get_text(strip=True)[:500]
                    
                    articles.append(NewsArticle(
                        headline=headline,
                        link=link,
                        content=content
                    ))
                except Exception as e:
                    continue
            
            print(f"Generic scraper found {len(articles)} articles")
            if duplicates_skipped > 0:
                print(f"Skipped {duplicates_skipped} duplicates")
                
        except Exception as e:
            print(f"Error in generic scraping: {e}")
        
        return articles
    
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
