import requests
import pandas as pd
from datetime import datetime
from typing import Optional


class MoneyControlAPI:
    """
    Generic class to download stock data from MoneyControl Price API
    """
    
    BASE_URL = "https://priceapi.moneycontrol.com/techCharts/indianMarket/stock/history"
    
    def __init__(self):
        self.session = requests.Session()
    
    @staticmethod
    def convert_to_timestamp(date_str: str) -> int:
        """
        Convert date string (YYYY-MM-DD) to Unix timestamp
        
        Args:
            date_str: Date in format YYYY-MM-DD
            
        Returns:
            Unix timestamp
        """
        dt = datetime.strptime(date_str, '%Y-%m-%d')
        return int(dt.timestamp())
    
    def fetch_stock_data(
        self,
        symbol: str,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        from_timestamp: Optional[int] = None,
        to_timestamp: Optional[int] = None,
        resolution: str = "1D",
        currency_code: str = "INR",
        countback: int = 1524
    ) -> pd.DataFrame:
        """
        Fetch stock data from MoneyControl API and return as DataFrame
        
        Args:
            symbol: Stock symbol (e.g., 'ITC', 'RELIANCE')
            from_date: Start date in format 'YYYY-MM-DD' (optional)
            to_date: End date in format 'YYYY-MM-DD' (optional)
            from_timestamp: Start timestamp (Unix epoch) - overrides from_date
            to_timestamp: End timestamp (Unix epoch) - overrides to_date
            resolution: Time resolution ('1D', '1W', '1M', etc.)
            currency_code: Currency code (default: 'INR')
            countback: Number of bars to fetch
            
        Returns:
            pandas DataFrame with columns: timestamp, datetime, open, high, low, close, volume
        """
        
        # Prepare timestamps
        if from_timestamp is None and from_date:
            from_timestamp = self.convert_to_timestamp(from_date)
        if to_timestamp is None and to_date:
            to_timestamp = self.convert_to_timestamp(to_date)
        
        # Prepare request parameters
        params = {
            'symbol': symbol,
            'resolution': resolution,
            'currencyCode': currency_code,
            'countback': countback
        }
        
        if from_timestamp:
            params['from'] = from_timestamp
        if to_timestamp:
            params['to'] = to_timestamp
        
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
                'open': data.get('o', []),
                'high': data.get('h', []),
                'low': data.get('l', []),
                'close': data.get('c', []),
                'volume': data.get('v', [])
            })
            
            # Convert timestamp to datetime
            if not df.empty and 'timestamp' in df.columns:
                df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
                # Reorder columns
                df = df[['timestamp', 'datetime', 'open', 'high', 'low', 'close', 'volume']]
            
            return df
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error fetching data from API: {str(e)}")
        except (KeyError, ValueError) as e:
            raise Exception(f"Error parsing API response: {str(e)}")
    
    def fetch_multiple_symbols(
        self,
        symbols: list,
        **kwargs
    ) -> dict:
        """
        Fetch data for multiple symbols
        
        Args:
            symbols: List of stock symbols
            **kwargs: Additional arguments to pass to fetch_stock_data
            
        Returns:
            Dictionary with symbol as key and DataFrame as value
        """
        results = {}
        for symbol in symbols:
            try:
                print(f"Fetching data for {symbol}...")
                df = self.fetch_stock_data(symbol, **kwargs)
                results[symbol] = df
                print(f"Successfully fetched {len(df)} records for {symbol}")
            except Exception as e:
                print(f"Error fetching {symbol}: {str(e)}")
                results[symbol] = None
        
        return results


def main():
    """
    Example usage of MoneyControlAPI
    """
    # Initialize API client
    api = MoneyControlAPI()
    
    # # Example 1: Fetch data for ITC with timestamps
    # print("Example 1: Fetching ITC data with timestamps")
    # print("-" * 50)
    # df_itc = api.fetch_stock_data(
    #     symbol='ITC',
    #     from_timestamp=1583884800,
    #     to_timestamp=1768176000,
    #     resolution='1D',
    #     countback=1524
    # )
    # print(f"\nFetched {len(df_itc)} records")
    # print(df_itc.head())
    # print(f"\nDate range: {df_itc['datetime'].min()} to {df_itc['datetime'].max()}")
    
    # Example 2: Fetch data with date strings
    print("\n\nExample 2: Fetching RELIANCE data with date strings")
    print("-" * 50)
    df_reliance = api.fetch_stock_data(
        symbol='RELIANCE',
        from_date='2024-01-01',
        to_date='2026-01-10',
        resolution='1D'
    )
    print(f"\nFetched {len(df_reliance)} records")
    print(df_reliance.head())
    
    # # Example 3: Fetch data for multiple symbols
    # print("\n\nExample 3: Fetching data for multiple symbols")
    # print("-" * 50)
    # symbols = ['ITC', 'RELIANCE', 'TCS']
    # results = api.fetch_multiple_symbols(
    #     symbols=symbols,
    #     from_date='2025-01-01',
    #     to_date='2026-01-10',
    #     resolution='1D'
    # )
    
    # Display summary
    print("\nSummary:")
    for symbol, df in results.items():
        if df is not None:
            print(f"{symbol}: {len(df)} records")
        else:
            print(f"{symbol}: Failed to fetch")
    
    # Example 4: Save to CSV
    print("\n\nExample 4: Saving data to CSV")
    print("-" * 50)
    df_itc.to_csv('itc_stock_data.csv', index=False)
    print("Data saved to itc_stock_data.csv")


if __name__ == "__main__":
    main()
