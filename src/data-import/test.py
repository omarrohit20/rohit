import requests
import pandas as pd
from bs4 import BeautifulSoup

def fetch_chartink_stock(symbol_url="https://chartink.com/stocks/rblbank.html"):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    r = requests.get(symbol_url, headers=headers)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

    # Chartink renders historical data in a table with id 'tblHistory'
    table = soup.find("table", {"id": "tblHistory"})
    rows = table.find_all("tr")

    data = []
    for row in rows[1:]:  # skip header
        cols = [col.text.strip() for col in row.find_all("td")]
        if cols:
            data.append(cols)

    # Convert to DataFrame
    df = pd.DataFrame(data, columns=["Date", "Open", "High", "Low", "Close", "Volume"])
    return df

df = fetch_chartink_stock()
print(df.head())
