import csv
from pymongo import MongoClient

connection = MongoClient('localhost', 27017)
db = connection.Nsedata
db.drop_collection('scrip')

# F&O universe kept in-memory; futures flag lives on `scrip` (no scrip_futures table).
futures_scrips = {}  # scrip -> company

count = 0
with open('nselist/ind_niftyfuturelist.csv') as csvfile:
    readCSV = csv.reader(csvfile, delimiter=',')
    for row in readCSV:
        try:
            if count != 0:
                print(row[0])
                futures_scrips[row[1]] = row[0]
            count = count + 1
        except Exception:
            pass
print(count)

count = 0
with open('nselist/ind_nifty500list.csv') as csvfile:
    readCSV = csv.reader(csvfile, delimiter=',')
    for row in readCSV:
        try:
            if count != 0:
                print(row[0])
                scrip = row[2]
                if scrip in futures_scrips:
                    futures = "Yes"
                    index = "futures"
                else:
                    futures = "No"
                    index = "nifty500"

                db.scrip.insert_one({
                    "company": row[0],
                    "industry": row[1],
                    "scrip": scrip,
                    "futures": futures,
                    "index": index,
                })
            count = count + 1
        except Exception:
            pass
print(count)

# count = 0
# with open('nselist/ind_niftycash.csv') as csvfile:
#     readCSV = csv.reader(csvfile, delimiter=',')
#     for row in readCSV:
#         try:
#             if count != 0:
#                 print(row[0])
#                 scrip = row[1]
#                 data = db.scrip.find_one({'scrip': scrip})
#                 if data is None:
#                     db.scrip.insert_one({
#                         "company": row[0],
#                         "industry": "",
#                         "scrip": scrip,
#                         "futures": "No",
#                         "index": "cash",
#                     })
#             count = count + 1
#         except Exception:
#             pass
# print(count)

# Futures names not in nifty500/cash still belong in scrip with futures=Yes
for scrip, company in futures_scrips.items():
    if db.scrip.find_one({'scrip': scrip}) is None:
        db.scrip.insert_one({
            "company": company,
            "industry": "",
            "scrip": scrip,
            "futures": "Yes",
            "index": "futures",
        })

connection.close()
