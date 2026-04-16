"""
NSE Options Data Fetcher
Complete guide to fetch NSE options chain data for equity stocks
"""

import pandas as pd
import requests
import json
from datetime import datetime
import warnings
import sys
import time
from pymongo import MongoClient
from bson import json_util

warnings.filterwarnings('ignore')

# connect to MongoDB (assumes local instance)
connection = MongoClient('localhost', 27017)
db = connection.Nsedata

# ============================================================================
# METHOD 1: Using NSE India Official API (Recommended)
# ============================================================================

def fetch_nse_options_data(symbol):
    """
    Fetch options chain data directly from NSE India website
    
    Parameters:
    symbol (str): Stock symbol (e.g., 'RELIANCE', 'TCS', 'INFY')
    
    Returns:
    pd.DataFrame: Options chain data. The underlying stock price is stored in
                  the DataFrame's attrs under the key 'underlying'.
    """

# NSE uses bot protection; requests must mimic a real browser.
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/117.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://www.nseindia.com/option-chain',
        'Origin': 'https://www.nseindia.com',
        'Connection': 'keep-alive',
        # additional headers sometimes required by strict CORS policies
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
    }

    session = requests.Session()

    try:
        # initial visit to set cookies; second visit to the option-chain page
        session.get('https://www.nseindia.com', headers=headers, timeout=10)
        session.get('https://www.nseindia.com/option-chain', headers=headers, timeout=10)

        options_url = f'https://www.nseindia.com/api/option-chain-equities?symbol={symbol}'
        response = session.get(options_url, headers=headers, timeout=10)

        if response.status_code != 200:
            print(f"Error: Status code {response.status_code}")
            return None

        # guard against empty json (site may block requests)
        try:
            data = response.json()
        except ValueError:
            print("Error: response not JSON")
            return None

        if not data or data == {}:
            print(f"Blank data returned for {symbol}; check headers or rate-limit")
            return None

        records = data.get('records', {}).get('data', [])

        calls_data = []
        puts_data = []

        for record in records:
            strike_price = record.get('strikePrice')
            expiry_date = record.get('expiryDate')

            if 'CE' in record:
                ce = record['CE']
                calls_data.append({
                    'Strike': strike_price,
                    'Expiry': expiry_date,
                    'Call_OI': ce.get('openInterest', 0),
                    'Call_OI_Change': ce.get('changeinOpenInterest', 0),
                    'Call_Volume': ce.get('totalTradedVolume', 0),
                    'Call_IV': ce.get('impliedVolatility', 0),
                    'Call_LTP': ce.get('lastPrice', 0),
                    'Call_Change': ce.get('change', 0),
                    'Call_Bid_Qty': ce.get('bidQty', 0),
                    'Call_Bid_Price': ce.get('bidprice', 0),
                    'Call_Ask_Price': ce.get('askPrice', 0),
                    'Call_Ask_Qty': ce.get('askQty', 0),
                })

            if 'PE' in record:
                pe = record['PE']
                puts_data.append({
                    'Strike': strike_price,
                    'Expiry': expiry_date,
                    'Put_OI': pe.get('openInterest', 0),
                    'Put_OI_Change': pe.get('changeinOpenInterest', 0),
                    'Put_Volume': pe.get('totalTradedVolume', 0),
                    'Put_IV': pe.get('impliedVolatility', 0),
                    'Put_LTP': pe.get('lastPrice', 0),
                    'Put_Change': pe.get('change', 0),
                    'Put_Bid_Qty': pe.get('bidQty', 0),
                    'Put_Bid_Price': pe.get('bidprice', 0),
                    'Put_Ask_Price': pe.get('askPrice', 0),
                    'Put_Ask_Qty': pe.get('askQty', 0),
                })

        calls_df = pd.DataFrame(calls_data)
        puts_df = pd.DataFrame(puts_data)
        options_df = pd.merge(calls_df, puts_df, on=['Strike', 'Expiry'], how='outer')

        underlying_value = data.get('records', {}).get('underlyingValue')
        if underlying_value is not None:
            options_df.attrs['underlying'] = underlying_value
            print(f"\n{symbol} Current Price: ₹{underlying_value}")
        print(f"Total Records: {len(options_df)}")

        return options_df

    except Exception as e:
        print(f"Error fetching data: {e}")
        return None


# ============================================================================
# METHOD 2: Using nsepython Library (Easiest)
# ============================================================================

def fetch_nse_options_data(symbol):
    """
    Fetch options data using nsepython library
    Install: pip install nsepython
    
    Parameters:
    symbol (str): Stock symbol
    
    Returns:
    pd.DataFrame: Options chain data
    """
    try:
        from nsepython import nse_optionchain_scrapper
        
        # Fetch options chain
        options_data = nse_optionchain_scrapper(symbol)
        
        # Convert to DataFrame
        df = pd.DataFrame(options_data)
        
        return df
        
    except ImportError:
        print("nsepython not installed. Install using: pip install nsepython")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None


# ============================================================================
# METHOD 3: Get Options Data with Filtering
# ============================================================================

def get_atm_options(symbol, range_percent=5):
    """
    Get ATM (At The Money) options with specified range
    
    Parameters:
    symbol (str): Stock symbol
    range_percent (float): Percentage range from current price
    
    Returns:
    pd.DataFrame: Filtered options data
    """
    
    df = fetch_nse_options_data(symbol)
    
    if df is not None and not df.empty:
        # Get current price (approximate from middle strikes)
        current_price = df['Strike'].median()
        
        # Calculate range
        lower_bound = current_price * (1 - range_percent/100)
        upper_bound = current_price * (1 + range_percent/100)
        
        # Filter ATM options
        atm_df = df[(df['Strike'] >= lower_bound) & (df['Strike'] <= upper_bound)]
        
        return atm_df
    
    return None


# ============================================================================
# METHOD 4: Get Options Data for Specific Expiry
# ============================================================================

def get_options_by_expiry(symbol, expiry_date=None):
    """
    Get options data for specific expiry date
    
    Parameters:
    symbol (str): Stock symbol
    expiry_date (str): Expiry date in 'DD-MMM-YYYY' format (e.g., '28-Dec-2024')
                      If None, returns nearest expiry
    
    Returns:
    pd.DataFrame: Options data for specific expiry
    """
    
    df = fetch_nse_options_data(symbol)
    
    if df is not None and not df.empty:
        if expiry_date:
            # Filter by specific expiry
            expiry_df = df[df['Expiry'] == expiry_date]
        else:
            # Get nearest expiry
            unique_expiries = df['Expiry'].unique()
            nearest_expiry = sorted(unique_expiries)[0]
            expiry_df = df[df['Expiry'] == nearest_expiry]
            print(f"Nearest Expiry: {nearest_expiry}")
        
        return expiry_df
    
    return None


# ============================================================================
# METHOD 5: Calculate Option Greeks and Indicators
# ============================================================================

def analyze_options_data(df):
    """
    Add analysis columns to options data
    
    Parameters:
    df (pd.DataFrame): Options data
    
    Returns:
    pd.DataFrame: Enhanced options data with analysis
    """
    
    if df is not None and not df.empty:
        # Calculate Put-Call Ratio
        df['PCR_OI'] = df['Put_OI'] / df['Call_OI']
        df['PCR_Volume'] = df['Put_Volume'] / df['Call_Volume']
        
        # Calculate total OI change
        df['Total_OI_Change'] = df['Call_OI_Change'] + df['Put_OI_Change']
        
        # Identify support and resistance levels
        df['Support_Level'] = df['Put_OI'] > df['Call_OI']
        df['Resistance_Level'] = df['Call_OI'] > df['Put_OI']
        
        # Mark ITM/OTM (approximate based on position)
        median_strike = df['Strike'].median()
        df['Call_ITM'] = df['Strike'] < median_strike
        df['Put_ITM'] = df['Strike'] > median_strike
        
        return df
    
    return None


# ============================================================================
# METHOD 6: Visualize Options Chain
# ============================================================================

def visualize_options_chain(df, symbol):
    """
    Create visualization of options chain data
    
    Parameters:
    df (pd.DataFrame): Options data
    symbol (str): Stock symbol
    """
    try:
        import matplotlib.pyplot as plt
        
        if df is not None and not df.empty:
            fig, axes = plt.subplots(2, 2, figsize=(15, 10))
            fig.suptitle(f'{symbol} Options Chain Analysis', fontsize=16)
            
            # Plot 1: OI by Strike
            axes[0, 0].bar(df['Strike'], df['Call_OI'], alpha=0.7, label='Call OI', color='green')
            axes[0, 0].bar(df['Strike'], -df['Put_OI'], alpha=0.7, label='Put OI', color='red')
            axes[0, 0].set_xlabel('Strike Price')
            axes[0, 0].set_ylabel('Open Interest')
            axes[0, 0].set_title('Open Interest Distribution')
            axes[0, 0].legend()
            axes[0, 0].grid(True, alpha=0.3)
            
            # Plot 2: Volume by Strike
            axes[0, 1].bar(df['Strike'], df['Call_Volume'], alpha=0.7, label='Call Volume', color='lightgreen')
            axes[0, 1].bar(df['Strike'], -df['Put_Volume'], alpha=0.7, label='Put Volume', color='lightcoral')
            axes[0, 1].set_xlabel('Strike Price')
            axes[0, 1].set_ylabel('Volume')
            axes[0, 1].set_title('Volume Distribution')
            axes[0, 1].legend()
            axes[0, 1].grid(True, alpha=0.3)
            
            # Plot 3: IV by Strike
            axes[1, 0].plot(df['Strike'], df['Call_IV'], marker='o', label='Call IV', color='blue')
            axes[1, 0].plot(df['Strike'], df['Put_IV'], marker='o', label='Put IV', color='orange')
            axes[1, 0].set_xlabel('Strike Price')
            axes[1, 0].set_ylabel('Implied Volatility (%)')
            axes[1, 0].set_title('Implied Volatility Smile')
            axes[1, 0].legend()
            axes[1, 0].grid(True, alpha=0.3)
            
            # Plot 4: OI Change
            axes[1, 1].bar(df['Strike'], df['Call_OI_Change'], alpha=0.7, label='Call OI Change', color='darkgreen')
            axes[1, 1].bar(df['Strike'], -df['Put_OI_Change'], alpha=0.7, label='Put OI Change', color='darkred')
            axes[1, 1].set_xlabel('Strike Price')
            axes[1, 1].set_ylabel('OI Change')
            axes[1, 1].set_title('Open Interest Change')
            axes[1, 1].legend()
            axes[1, 1].grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.show()
            
    except ImportError:
        print("matplotlib not installed. Install using: pip install matplotlib")
    except Exception as e:
        print(f"Error creating visualization: {e}")


# ============================================================================
# METHOD 7: Export to Excel with Formatting
# ============================================================================

def export_to_excel(df, symbol, filename=None):
    """
    Export options data to Excel with formatting
    
    Parameters:
    df (pd.DataFrame): Options data
    symbol (str): Stock symbol
    filename (str): Output filename
    """
    try:
        if filename is None:
            filename = f'{symbol}_options_chain_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Options Chain', index=False)
            
            # Get the worksheet
            worksheet = writer.sheets['Options Chain']
            
            # Auto-adjust column width
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(cell.value)
                    except:
                        pass
                adjusted_width = (max_length + 2)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        print(f"Data exported to {filename}")
        
    except Exception as e:
        print(f"Error exporting to Excel: {e}")


# ============================================================================
# HELPER: insert into MongoDB
# ============================================================================

def insert_options_data(symbol, df, futures=None):
    """Store options data in MongoDB as a list of records.

    The collection name will be `options` in the `Nsedata` database.  The
    document includes the symbol, timestamp, optional futures flag, column
    names, and the data itself.  Any underlying price scraped earlier is
    stored as a field if available.
    """
    if df is None or df.empty:
        return

    record = {
        'symbol': symbol,
        'futures': futures,
        'timestamp': datetime.utcnow(),
        'columns': df.columns.tolist(),
        'data': df.to_dict('records')
    }
    # add underlying if present
    if hasattr(df, 'attrs') and 'underlying' in df.attrs:
        record['underlying'] = df.attrs['underlying']

    json_data = json.loads(json.dumps(record, default=json_util.default))
    db.options.insert_one(json_data)


# ============================================================================
# EXAMPLE / CLI USAGE
# ============================================================================

if __name__ == "__main__":
    # command‑line driven import from MongoDB cassette
    # usage: python nse_options_data_fetcher.py [update] [futures_flag]
    # if the first argument is "examples" or omitted, the built‑in demos run
    
    mode = sys.argv[1] if len(sys.argv) > 1 else 'examples'

    if mode != 'examples':
        # drop collection unless user explicitly passed "update"
        if mode != 'update':
            db.drop_collection('options')

        futures_filter = None
        if len(sys.argv) > 2:
            futures_filter = sys.argv[2]

        query = {'futures': futures_filter} if futures_filter else {}

        for doc in db.scrip.find(query):
            scrip = doc.get('scrip')
            futures_flag = doc.get('futures')
            try:
                if db.options.find_one({'symbol': scrip}) is None:
                    df = fetch_nse_options_data(scrip)
                    insert_options_data(scrip, df, futures_flag)
                print(f"Processed {scrip}")
            except Exception as exc:
                print(f"error fetching {scrip}: {exc}")
                time.sleep(2)

        connection.close()
        print('Done options import')

    else:
        # simple walkthrough examples for interactive use
        print("=" * 80)
        print("EXAMPLE 1: Fetch Complete Options Chain")
        print("=" * 80)

        symbol = "RELIANCE"
        df = fetch_nse_options_data(symbol)

        if df is not None:
            print(f"\nOptions Chain Data for {symbol}:")
            print(df.head(10))
            print(f"\nShape: {df.shape}")
            print(f"\nColumns: {df.columns.tolist()}")

        # Example 2: Get ATM options
        print("\n" + "=" * 80)
        print("EXAMPLE 2: Get ATM Options (±5% range)")
        print("=" * 80)

        atm_df = get_atm_options(symbol, range_percent=5)
        if atm_df is not None:
            print("\nATM Options:")
            print(atm_df[['Strike', 'Call_OI', 'Put_OI', 'Call_LTP', 'Put_LTP']])

        # Example 3: Get options for nearest expiry
        print("\n" + "=" * 80)
        print("EXAMPLE 3: Get Options for Nearest Expiry")
        print("=" * 80)

        expiry_df = get_options_by_expiry(symbol)
        if expiry_df is not None:
            print("\nNearest Expiry Options:")
            print(expiry_df.head())

        # Example 4: Analyze options data
        print("\n" + "=" * 80)
        print("EXAMPLE 4: Analyze Options Data")
        print("=" * 80)

        if df is not None:
            analyzed_df = analyze_options_data(df)
            if analyzed_df is not None:
                print("\nOptions Analysis:")
                print(analyzed_df[['Strike', 'PCR_OI', 'PCR_Volume', 'Total_OI_Change']].head(10))

                # Calculate overall PCR
                total_call_oi = analyzed_df['Call_OI'].sum()
                total_put_oi = analyzed_df['Put_OI'].sum()
                overall_pcr = total_put_oi / total_call_oi if total_call_oi > 0 else 0
                print(f"\nOverall Put-Call Ratio (OI): {overall_pcr:.2f}")

        # Example 5: Export to Excel
        print("\n" + "=" * 80)
        print("EXAMPLE 5: Export to Excel")
        print("=" * 80)

        if df is not None:
            export_to_excel(df, symbol)

        # Example 6: Visualize (uncomment to see plots)
        # print("\n" + "=" * 80)
        # print("EXAMPLE 6: Visualize Options Chain")
        # print("=" * 80)
        # 
        # if atm_df is not None:
        #     visualize_options_chain(atm_df, symbol)


# ============================================================================
# QUICK REFERENCE - OTHER POPULAR STOCKS
# ============================================================================

"""
Popular NSE stocks for options trading:

NIFTY Stocks:
- RELIANCE
- TCS
- HDFCBANK
- INFY
- ICICIBANK
- HINDUNILVR
- ITC
- SBIN
- BHARTIARTL
- KOTAKBANK
- LT
- BAJFINANCE
- ASIANPAINT
- MARUTI
- HCLTECH

Bank Nifty Stocks:
- HDFCBANK
- ICICIBANK
- SBIN
- KOTAKBANK
- AXISBANK
- INDUSINDBK
- BANKBARODA
- PNB
- FEDERALBNK
- IDFCFIRSTB

Usage:
df = fetch_nse_options_data('HDFCBANK')
df = fetch_nse_options_data('TCS')
"""
