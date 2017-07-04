from nsetools import Nse
import csv

nse = Nse()

with open('temp/nse.csv') as csvfile:
    fieldnames = ['scrip', 'company']
    reader = csv.DictReader(csvfile, fieldnames=fieldnames)
    
    count = 0
    for row in reader:
        print(row['scrip'], row['company'])
        try:
            stock = nse.get_quote(row['scrip'])
            if stock is not None:
                count += 1
                
                from pprint import pprint # just for neatness of display
                pprint(stock)
        except:
            pass        
    print count