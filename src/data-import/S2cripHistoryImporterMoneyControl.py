import requests
import pandas as pd
from datetime import datetime, date, timedelta
import json
from bson import json_util
import time
import sys
from pymongo import MongoClient

connection = MongoClient('localhost', 27017)
db = connection.Nsedata


class MoneyControlAPI:
    """
    Generic class to download stock data from MoneyControl Price API
    """
    
    BASE_URL = "https://priceapi.moneycontrol.com/techCharts/indianMarket/stock/history"
    
    def __init__(self):
        self.session = requests.Session()
    
    @staticmethod
    def convert_to_timestamp(date_obj: date) -> int:
        """
        Convert date object to Unix timestamp
        
        Args:
            date_obj: Date object
            
        Returns:
            Unix timestamp
        """
        dt = datetime.combine(date_obj, datetime.min.time())
        return int(dt.timestamp())
    
    def fetch_stock_data(
        self,
        symbol: str,
        from_date: date,
        to_date: date,
        resolution: str = "1D",
        currency_code: str = "INR",
        countback: int = 5000
    ) -> pd.DataFrame:
        """
        Fetch stock data from MoneyControl API and return as DataFrame
        
        Args:
            symbol: Stock symbol (e.g., 'ITC', 'RELIANCE')
            from_date: Start date object
            to_date: End date object
            resolution: Time resolution ('1D', '1W', '1M', etc.)
            currency_code: Currency code (default: 'INR')
            countback: Number of bars to fetch
            
        Returns:
            pandas DataFrame with columns: Date, Open, High, Low, Close, Volume
        """
        
        # Convert dates to timestamps
        from_timestamp = self.convert_to_timestamp(from_date)
        to_timestamp = self.convert_to_timestamp(to_date)
        
        # Prepare request parameters
        params = {
            'symbol': symbol,
            'resolution': resolution,
            'currencyCode': currency_code,
            'countback': countback,
            'from': from_timestamp,
            'to': to_timestamp
        }
        
        # Prepare headers to mimic browser request
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-GB,en;q=0.9,en-US;q=0.8,en-IN;q=0.7',
            'cache-control': 'max-age=0',
            'priority': 'u=0, i',
            'sec-ch-ua': '"Microsoft Edge";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36 Edg/143.0.0.0'
        }
        
        try:
            # Make API request with headers
            response = self.session.get(self.BASE_URL, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Parse JSON response
            data = response.json()
            
            # Check if data is valid
            if data.get('s') != 'ok':
                raise ValueError(f"API returned error status: {data.get('s')}")
            
            # Create DataFrame
            df = pd.DataFrame({
                'timestamp': data.get('t', []),
                'Open': data.get('o', []),
                'High': data.get('h', []),
                'Low': data.get('l', []),
                'Close': data.get('c', []),
                'Volume': data.get('v', [])
            })
            
            # Convert timestamp to datetime and set as index
            if not df.empty and 'timestamp' in df.columns:
                df['Date'] = pd.to_datetime(df['timestamp'], unit='s')
                df = df.set_index('Date')
                df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
                
                # Add Last column (same as Close for compatibility)
                df['Last'] = df['Close']
                # Add Turnover column (calculated as Close * Volume)
                df['Turnover'] = df['Close'] * df['Volume']
                
                # Reorder columns to match NSE format
                df = df[['Open', 'High', 'Low', 'Last', 'Close', 'Volume', 'Turnover']]
            
            return df
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error fetching data from API: {str(e)}")
        except (KeyError, ValueError) as e:
            raise Exception(f"Error parsing API response: {str(e)}")


def historical_data(scrip, start_date, end_date, api):
    """
    Fetch historical data from MoneyControl API
    
    Args:
        scrip: Stock symbol
        start_date: Start date
        end_date: End date
        api: MoneyControlAPI instance
        
    Returns:
        DataFrame with historical data
    """
    stock_data = api.fetch_stock_data(
        symbol=scrip,
        from_date=start_date,
        to_date=end_date,
        resolution='1D'
    )
    return stock_data


def insert_scripdata(scrip, data, futures):
    """
    Insert historical data into MongoDB
    
    Args:
        scrip: Stock symbol
        data: DataFrame with historical data
        futures: Futures indicator
    """
    if data.empty == False:
        record = {}
        record['dataset_code'] = scrip
        record['name'] = scrip
        
        # Reverse the data to have oldest first
        data = data.iloc[::-1]
        temp = data[['Open', 'High', 'Low', 'Last', 'Close', 'Volume', 'Turnover']]
        temp['Date'] = data.index.astype(str)
        df = temp[['Date', 'Open', 'High', 'Low', 'Last', 'Close', 'Volume', 'Turnover']]
        
        record['end_date'] = data.index.astype(str)[0]
        record['data'] = df.values.tolist()
        record['column_names'] = df.columns.tolist()
        record['futures'] = futures
        record['source'] = 'MoneyControl'
        
        json_data = json.loads(json.dumps(record, default=json_util.default))
        db.history.insert_one(json_data)
        time.sleep(0.5)


if __name__ == "__main__":
    # Initialize MoneyControl API
    api = MoneyControlAPI()
    
    # Check if update mode
    if len(sys.argv) > 1 and sys.argv[1] != 'update':
        db.drop_collection('history')
    
    # Set date range
    end_date = date.today() + timedelta(days=1)
    start_date = date.today() - timedelta(days=5000)
    print(f"Date range: {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}")
    
    # Process each scrip from database
    for data in db.scrip.find({'futures': sys.argv[2]}):
        futures = data['futures']
        # scrip = data['scrip'].replace('&','').replace('-','_')
        scrip = data['scrip']
        
        try:
            # Check if data already exists
            existing_data = db.history.find_one({'dataset_code': scrip})
            if existing_data is None:
                print(f"Fetching {scrip}...")
                data = historical_data(scrip, start_date, end_date, api)
                insert_scripdata(scrip, data, futures)
                print(f"✓ {scrip}")
            else:
                print(f"⊙ {scrip} (already exists)")
        except Exception as e:
            # Retry once after a delay
            time.sleep(2)
            try:
                print(f"Retrying {scrip}...")
                data = historical_data(scrip, start_date, end_date, api)
                insert_scripdata(scrip, data, futures)
                print(f"✓ {scrip} (retry)")
            except Exception as e2:
                print(f"✗ Failed: {scrip} - {str(e2)}")
                pass
        
        # Small delay to avoid rate limiting
        

connection.close()
print('\nDone: MoneyControl History Import')
