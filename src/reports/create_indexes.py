#!/usr/bin/env python
"""
Rebuild MongoDB indexes used by reports queries (rbase / chartlink / news).

Targets:
  chartlink.*  — systemtime regex counts, scrip lookups, yearLowChange filters
  Nsedata.scrip — futures=Yes lookups
  Nsedata.scrip_news — scrip, conviction, sentiment, insertion_date
"""

from pymongo import MongoClient, ASCENDING
from pymongo.errors import OperationFailure
import sys
from datetime import datetime

CHARTLINK_INDEXES = [
    [("systemtime", ASCENDING)],
    [("scrip", ASCENDING)],
    [("systemtime", ASCENDING), ("scrip", ASCENDING)],
    [("scrip", ASCENDING), ("yearLowChange", ASCENDING)],
]

NSEDATA_INDEXES = {
    "scrip": [
        [("scrip", ASCENDING)],
        [("futures", ASCENDING), ("scrip", ASCENDING)],
    ],
    "scrip_news": [
        [("scrip", ASCENDING)],
        [("insertion_date", ASCENDING)],
        [("updated_at", ASCENDING)],
        [("conviction", ASCENDING), ("overall_sentiment", ASCENDING), ("insertion_date", ASCENDING)],
    ],
}

SKIP_COLLECTIONS = {"system.profile"}


def _field_str(index_fields):
    return ", ".join(f"{name}" for name, _ in index_fields)


def _ensure_indexes(collection, index_list, rebuild):
    created = 0
    skipped = 0
    rebuilt = 0
    existing = {tuple(idx["key"].items()): idx for idx in collection.list_indexes()}

    for index_fields in index_list:
        key = tuple(index_fields)
        idx = existing.get(key)
        kwargs = {"background": True}
        if idx and idx.get("unique"):
            kwargs["unique"] = True
        try:
            if idx and rebuild and idx["name"] != "_id_":
                collection.drop_index(idx["name"])
                collection.create_index(index_fields, **kwargs)
                rebuilt += 1
                print(f"   Rebuilt: {_field_str(index_fields)}")
            else:
                collection.create_index(index_fields, **kwargs)
                if idx:
                    skipped += 1
                    print(f"   Exists:  {_field_str(index_fields)}")
                else:
                    created += 1
                    print(f"   Created: {_field_str(index_fields)}")
        except OperationFailure as e:
            msg = str(e).lower()
            if "already exists" in msg or "equivalent index" in msg:
                skipped += 1
                print(f"   Exists:  {_field_str(index_fields)}")
            else:
                print(f"   Failed:  {_field_str(index_fields)}: {e}")
                raise
    return created, skipped, rebuilt


def create_indexes(rebuild=True):
    try:
        print("Connecting to MongoDB at localhost:27017...")
        connection = MongoClient("localhost", 27017, serverSelectionTimeoutMS=5000)
        connection.server_info()
        print("Connected.\n")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        print("Make sure MongoDB is running on localhost:27017")
        sys.exit(1)

    dbcl = connection.chartlink
    dbnse = connection.Nsedata

    total_created = 0
    total_skipped = 0
    total_rebuilt = 0
    failed = []

    print("=" * 80)
    print("chartlink - reports query indexes")
    print("=" * 80)

    collections = [n for n in sorted(dbcl.list_collection_names()) if n not in SKIP_COLLECTIONS]
    if not collections:
        print("No collections found in chartlink.")
    for collection_name in collections:
        collection = dbcl[collection_name]
        print(f"\n[{collection_name}]  ({collection.estimated_document_count()} docs)")
        try:
            created, skipped, rebuilt = _ensure_indexes(collection, CHARTLINK_INDEXES, rebuild)
            total_created += created
            total_skipped += skipped
            total_rebuilt += rebuilt
        except Exception as e:
            print(f"   Error: {e}")
            failed.append((f"chartlink.{collection_name}", str(e)))

    print("\n" + "=" * 80)
    print("Nsedata - reports query indexes")
    print("=" * 80)

    nse_names = set(dbnse.list_collection_names())
    for collection_name, index_list in NSEDATA_INDEXES.items():
        if collection_name not in nse_names:
            print(f"\n[{collection_name}]  (missing - skipped)")
            continue
        collection = dbnse[collection_name]
        print(f"\n[{collection_name}]  ({collection.estimated_document_count()} docs)")
        try:
            created, skipped, rebuilt = _ensure_indexes(collection, index_list, rebuild)
            total_created += created
            total_skipped += skipped
            total_rebuilt += rebuilt
        except Exception as e:
            print(f"   Error: {e}")
            failed.append((f"Nsedata.{collection_name}", str(e)))

    print("\n" + "-" * 80)
    print("Summary")
    print(f"   Created: {total_created}")
    print(f"   Rebuilt: {total_rebuilt}")
    print(f"   Already present: {total_skipped}")
    print(f"   Errors: {len(failed)}")
    if failed:
        for name, error in failed:
            print(f"   - {name}: {error}")

    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    connection.close()
    return len(failed) == 0


if __name__ == "__main__":
    rebuild = "--no-rebuild" not in sys.argv
    success = create_indexes(rebuild=rebuild)
    sys.exit(0 if success else 1)
