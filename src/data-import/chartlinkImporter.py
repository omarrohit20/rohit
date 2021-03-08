from urllib.request import urlopen
import yfinance as yf
from datetime import date
import pandas as pd
import json
from bson import json_util
import datetime
import time
import sys
import csv
from pymongo import MongoClient

import pycurl
import StringIO
connection = MongoClient('localhost', 27017)
db = connection.Nsedata







 
if __name__ == "__main__":
    response = StringIO.StringIO()
    c = pycurl.Curl()
    c.setopt(c.URL, 'https://chartink.com/backtest/process')
    c.setopt(c.WRITEFUNCTION, response.write)
    c.setopt(c.HTTPHEADER, ['Content-Type: application/json','Accept-Charset: UTF-8',
                            'authority: chartink.com'
                            'accept: application/json, text/plain, */*',
                            'x-xsrf-token: eyJpdiI6Inh0UndsVTBZeEMxQ0hIa1RCcVoyRWc9PSIsInZhbHVlIjoiN3BoaWFXRFUycWNRV0NXNkpPaFVZNktvR1hNTmRjVEczc21Xcmx6V2pzTWlzTTQ4c2ZWR040SG1nQ2hNdzdtbyIsIm1hYyI6IjJhMWVhNDZkY2QxYjc2MTFkYWE0MTdjOWZmYmE1OWJhNThkOTFhZDlmYzkzZWEwZjdmODQ5MzFhYmZlNjM2N2EifQ==',
                            'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36 OPR/74.0.3911.107',
                            'content-type: application/x-www-form-urlencoded',
                            'origin: https://chartink.com',
                            'sec-fetch-site: same-origin',
                            'sec-fetch-mode: cors',
                            'sec-fetch-dest: empty',
                            'referer: https://chartink.com/screener/buy-dayconsolidation-breakout',
                            'accept-language: en-US,en;q=0.9',
'cookie: _ga=GA1.2.484368436.1612078327; bafp=6f0e3b60-6396-11eb-89a8-398e7f0c266b; __utmc=102564947; bfp_sn_rf_8b2087b102c9e3e5ffed1c1478ed8b78=Direct; PHPSESSID=a467271108a46f4c6a7904b9170ae91a; __qca=P0-1841628798-1613403071513; bfp_sn_rt_8b2087b102c9e3e5ffed1c1478ed8b78=1613490111421; hbcm_sd=2%7C1613490109962; remember_web_59ba36addc2b2f9401580f014c7f58ea4e30989d=eyJpdiI6IlwvTU8xRSsreHpSVlwva0FlVTBNR3RoUT09IiwidmFsdWUiOiJsTjFwd05NMXRsR21CMXNcL3hqTnpMS2xDM2dNQ2UwMzgxXC9IaDFYNTVGV0FhSDlwNnZ1S25ocWhMMkxnOGxaVlFMK2dJV1Jzc2JjY3VqR1FyQk54OHllUVZBbXV5TnZCRDFGZUpQRmVlaE9ibGhMUXZacVpuR3d3TldNa1RJZ3RZWGFRTWRCbzBWcjdWMDJSV0ZXbE9WaU1BczNqRUF0MWJLS1VrXC9sbDN1Y0RKelNMNjl3Y0Zuekx3TkdQVlUwR2ciLCJtYWMiOiIyMjNjYzJlNWNmODQ2YTk1MDVhMDJjZGRkZWViNDVjZTViNTczOGZlYzY4MWEyMTNkYjJhNmYwMmE1NGU2YzkyIn0%3D; __gads=ID=4b3dee565a5cf9af-224b79459cc6005d:T=1613490691:RT=1613490691:S=ALNI_MaRrm_lGs2IBbMwqfo8uNe36iJ0pw; _gid=GA1.2.358377505.1613965641; __utma=102564947.484368436.1612078327.1613490346.1614005639.6; __utmz=102564947.1614005639.6.2.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); __utmb=102564947.4.10.1614005639; _gat=1; XSRF-TOKEN=eyJpdiI6Inh0UndsVTBZeEMxQ0hIa1RCcVoyRWc9PSIsInZhbHVlIjoiN3BoaWFXRFUycWNRV0NXNkpPaFVZNktvR1hNTmRjVEczc21Xcmx6V2pzTWlzTTQ4c2ZWR040SG1nQ2hNdzdtbyIsIm1hYyI6IjJhMWVhNDZkY2QxYjc2MTFkYWE0MTdjOWZmYmE1OWJhNThkOTFhZDlmYzkzZWEwZjdmODQ5MzFhYmZlNjM2N2EifQ%3D%3D; ci_session=eyJpdiI6InlScUMrMHZzY3JWclJHdkxXTGFCOXc9PSIsInZhbHVlIjoiSFpkSzNjM3FvTkpLMHdEXC93TVwvTGRZZFBONkxTRmJzelc2QTdhcUdhU1VEaFRjNjQ3cHdkSWNYdXJ3d0dhaHEzIiwibWFjIjoiMDEyNWEwZGM3N2Y4NzQ3MDdlYmZkNWI1YzJiNTAxOGVhYjVlZDZiZjFmZjQxZGFhMjE1YzFhNjM5OGMyNjQ4MyJ9',
  --data-raw 'max_rows=160&scan_clause=(%20%7B57960%7D%20(%20latest%20%22close%20-%201%20candle%20ago%20close%20%2F%201%20candle%20ago%20close%20*%20100%22%20%3E%201%20and%20%5B0%5D%201%20hour%20high%20%3E%20%5B%3D1%5D%202%20hour%20high%20and%20%5B%3D1%5D%205%20minute%20close%20%3E%20%5B%3D1%5D%205%20minute%20open%20and(%20(%20%5B0%5D%2015%20minute%20vwap%20-%20%5B-6%5D%2015%20minute%20vwap%20)%20*%20100%20)%20%2F%20%5B-6%5D%2015%20minute%20vwap%20%3C%200.05%20and(%20(%20%5B-4%5D%2015%20minute%20vwap%20-%20%5B-8%5D%2015%20minute%20vwap%20)%20*%20100%20)%20%2F%20%5B-8%5D%2015%20minute%20vwap%20%3C%200.05%20and(%20(%20%5B0%5D%2015%20minute%20vwap%20-%20%5B-6%5D%2015%20minute%20vwap%20)%20*%20100%20)%20%2F%20%5B-6%5D%2015%20minute%20vwap%20%3E%20-0.05%20and(%20(%20%5B-4%5D%2015%20minute%20vwap%20-%20%5B-8%5D%2015%20minute%20vwap%20)%20*%20100%20)%20%2F%20%5B-8%5D%2015%20minute%20vwap%20%3E%20-0.05%20and(%20(%20%5B0%5D%2015%20minute%20high%20-%20%5B-4%5D%2015%20minute%20high%20)%20*%20100%20)%20%2F%20%5B-4%5D%2015%20minute%20high%20%3C%201%20and(%20(%20%5B-4%5D%2015%20minute%20high%20-%20%5B-8%5D%2015%20minute%20high%20)%20*%20100%20)%20%2F%20%5B-8%5D%2015%20minute%20high%20%3C%201%20and(%20(%20%5B0%5D%2015%20minute%20high%20-%20%5B-4%5D%2015%20minute%20high%20)%20*%20100%20)%20%2F%20%5B-4%5D%2015%20minute%20high%20%3E%20-1%20and(%20(%20%5B-4%5D%2015%20minute%20high%20-%20%5B-8%5D%2015%20minute%20high%20)%20*%20100%20)%20%2F%20%5B-8%5D%2015%20minute%20high%20%3E%20-1%20)%20)%20'
                            ])
    c.setopt(c.POSTFIELDS, '@request.json')
    c.perform()
    c.close()
    print (response.getvalue())
    response.close()  
    
    
curl 'https://chartink.com/backtest/process' \
  -H 'authority: chartink.com' \
  -H 'accept: application/json, text/plain, */*' \
  -H 'x-xsrf-token: eyJpdiI6Inh0UndsVTBZeEMxQ0hIa1RCcVoyRWc9PSIsInZhbHVlIjoiN3BoaWFXRFUycWNRV0NXNkpPaFVZNktvR1hNTmRjVEczc21Xcmx6V2pzTWlzTTQ4c2ZWR040SG1nQ2hNdzdtbyIsIm1hYyI6IjJhMWVhNDZkY2QxYjc2MTFkYWE0MTdjOWZmYmE1OWJhNThkOTFhZDlmYzkzZWEwZjdmODQ5MzFhYmZlNjM2N2EifQ==' \
  -H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36 OPR/74.0.3911.107' \
  -H 'content-type: application/x-www-form-urlencoded' \
  -H 'origin: https://chartink.com' \
  -H 'sec-fetch-site: same-origin' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-dest: empty' \
  -H 'referer: https://chartink.com/screener/buy-dayconsolidation-breakout' \
  -H 'accept-language: en-US,en;q=0.9' \
  -H 'cookie: XSRF-TOKEN=eyJpdiI6Inh0UndsVTBZeEMxQ0hIa1RCcVoyRWc9PSIsInZhbHVlIjoiN3BoaWFXRFUycWNRV0NXNkpPaFVZNktvR1hNTmRjVEczc21Xcmx6V2pzTWlzTTQ4c2ZWR040SG1nQ2hNdzdtbyIsIm1hYyI6IjJhMWVhNDZkY2QxYjc2MTFkYWE0MTdjOWZmYmE1OWJhNThkOTFhZDlmYzkzZWEwZjdmODQ5MzFhYmZlNjM2N2EifQ%3D%3D; ci_session=eyJpdiI6InlScUMrMHZzY3JWclJHdkxXTGFCOXc9PSIsInZhbHVlIjoiSFpkSzNjM3FvTkpLMHdEXC93TVwvTGRZZFBONkxTRmJzelc2QTdhcUdhU1VEaFRjNjQ3cHdkSWNYdXJ3d0dhaHEzIiwibWFjIjoiMDEyNWEwZGM3N2Y4NzQ3MDdlYmZkNWI1YzJiNTAxOGVhYjVlZDZiZjFmZjQxZGFhMjE1YzFhNjM5OGMyNjQ4MyJ9' \
  --data-raw 'max_rows=80&scan_clause=(%20%7B57960%7D%20(%20latest%20%22close%20-%201%20candle%20ago%20close%20%2F%201%20candle%20ago%20close%20*%20100%22%20%3E%201%20and%20%5B0%5D%201%20hour%20high%20%3E%20%5B%3D1%5D%202%20hour%20high%20and%20%5B%3D1%5D%205%20minute%20close%20%3E%20%5B%3D1%5D%205%20minute%20open%20and(%20(%20%5B0%5D%2015%20minute%20vwap%20-%20%5B-6%5D%2015%20minute%20vwap%20)%20*%20100%20)%20%2F%20%5B-6%5D%2015%20minute%20vwap%20%3C%200.05%20and(%20(%20%5B-4%5D%2015%20minute%20vwap%20-%20%5B-8%5D%2015%20minute%20vwap%20)%20*%20100%20)%20%2F%20%5B-8%5D%2015%20minute%20vwap%20%3C%200.05%20and(%20(%20%5B0%5D%2015%20minute%20vwap%20-%20%5B-6%5D%2015%20minute%20vwap%20)%20*%20100%20)%20%2F%20%5B-6%5D%2015%20minute%20vwap%20%3E%20-0.05%20and(%20(%20%5B-4%5D%2015%20minute%20vwap%20-%20%5B-8%5D%2015%20minute%20vwap%20)%20*%20100%20)%20%2F%20%5B-8%5D%2015%20minute%20vwap%20%3E%20-0.05%20and(%20(%20%5B0%5D%2015%20minute%20high%20-%20%5B-4%5D%2015%20minute%20high%20)%20*%20100%20)%20%2F%20%5B-4%5D%2015%20minute%20high%20%3C%201%20and(%20(%20%5B-4%5D%2015%20minute%20high%20-%20%5B-8%5D%2015%20minute%20high%20)%20*%20100%20)%20%2F%20%5B-8%5D%2015%20minute%20high%20%3C%201%20and(%20(%20%5B0%5D%2015%20minute%20high%20-%20%5B-4%5D%2015%20minute%20high%20)%20*%20100%20)%20%2F%20%5B-4%5D%2015%20minute%20high%20%3E%20-1%20and(%20(%20%5B-4%5D%2015%20minute%20high%20-%20%5B-8%5D%2015%20minute%20high%20)%20*%20100%20)%20%2F%20%5B-8%5D%2015%20minute%20high%20%3E%20-1%20)%20)%20'       
            
                
connection.close()
print('Done OIimport')