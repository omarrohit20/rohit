import csv
from pathlib import Path

from pymongo import MongoClient

_BASE = Path(__file__).resolve().parent / "nselist"

connection = MongoClient("localhost", 27017)
db = connection.Nsedata
db.drop_collection("scrip")


def _parse_mcap(raw):
    if raw is None:
        return None
    text = str(raw).strip().replace(",", "")
    if not text:
        return None
    try:
        value = float(text)
    except ValueError:
        return None
    return value if value > 0 else None


def _mcap_doc(value):
    mcap = _parse_mcap(value)
    if mcap is None:
        return {}
    return {"marketcap": mcap}


# F&O universe kept in-memory; futures flag lives on `scrip` (no scrip_futures table).
futures_scrips = {}  # scrip -> {company, marketcap}

with (_BASE / "ind_niftyfuturelist.csv").open(newline="", encoding="utf-8") as csvfile:
    for row in csv.DictReader(csvfile):
        symbol = (row.get("Symbol") or "").strip()
        if not symbol:
            continue
        futures_scrips[symbol] = {
            "company": (row.get("Stock Name") or "").strip(),
            "marketcap": _parse_mcap(row.get("Marketcap")),
        }
print(f"futures list: {len(futures_scrips)}")

count = 0
with (_BASE / "ind_nifty500list.csv").open(newline="", encoding="utf-8") as csvfile:
    for row in csv.DictReader(csvfile):
        try:
            scrip = (row.get("Symbol") or "").strip()
            if not scrip:
                continue
            print(row.get("Company Name"))
            if scrip in futures_scrips:
                futures = "Yes"
                index = "futures"
            else:
                futures = "No"
                index = "nifty500"
            record = {
                "company": (row.get("Company Name") or "").strip(),
                "industry": (row.get("Industry") or "").strip(),
                "scrip": scrip,
                "futures": futures,
                "index": index,
                **_mcap_doc(row.get("Marketcap")),
            }
            db.scrip.insert_one(record)
            count += 1
        except Exception:
            pass
print(f"nifty500: {count}")

count = 0
with (_BASE / "ind_niftycash.csv").open(newline="", encoding="utf-8") as csvfile:
    for row in csv.DictReader(csvfile):
        try:
            scrip = (row.get("Symbol") or "").strip()
            if not scrip:
                continue
            print(row.get("Stock Name"))
            if db.scrip.find_one({"scrip": scrip}) is None:
                db.scrip.insert_one(
                    {
                        "company": (row.get("Stock Name") or "").strip(),
                        "industry": "",
                        "scrip": scrip,
                        "futures": "No",
                        "index": "cash",
                        **_mcap_doc(row.get("Marketcap")),
                    }
                )
                count += 1
        except Exception:
            pass
print(f"cash added: {count}")

# Futures names not in nifty500/cash still belong in scrip with futures=Yes
for scrip, meta in futures_scrips.items():
    if db.scrip.find_one({"scrip": scrip}) is None:
        record = {
            "company": meta["company"],
            "industry": "",
            "scrip": scrip,
            "futures": "Yes",
            "index": "futures",
        }
        if meta.get("marketcap") is not None:
            record["marketcap"] = meta["marketcap"]
        db.scrip.insert_one(record)

connection.close()
