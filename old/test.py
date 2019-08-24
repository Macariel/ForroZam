#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from tinydb import TinyDB, JSONStorage
from tinydb.middlewares import CachingMiddleware
from old.inverted_index import Index
from echoprint_server import decode_echoprint


def main():
    index = Index()
    db_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data", "db.json")
    db = TinyDB(db_path)

    #eliminate_duplicates(db.all(), db)
    #adjust_indices(db)
    #update_index(db, index)
    #create_metadata_db(db)
    db.close()


def eliminate_duplicates(all_entries, db):
    # Eliminate duplicates
    print("Size: %s" % str(len(all_entries)))

    seen = set()
    duplicates = set()
    print("Collecting duplicates")
    for entry in all_entries:
        code = str(entry["code"])

        if code in seen:
            duplicates.add(entry.doc_id)
        else:
            seen.add(code)

    print("Found %s duplicates" % str(len(duplicates)))

    print("Removing duplicates")
    db.remove(doc_ids=duplicates)


def set_all_codes(all_entries, db):
    print("Decoding every echoprint")
    for entry in all_entries:
        entry["code"] = decode_echoprint(str(entry["code"]))[1]
    db.write_back(all_entries)


def create_metadata_db(db):
    metadata = map(lambda x: {"index": x["index"], "filename": x["metadata"]["filename"]}, db.all())
    db_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data", "metadata.json")
    metadata_db = TinyDB(db_path, storage=CachingMiddleware(JSONStorage))
    metadata_db.insert_multiple(metadata)
    metadata_db.close()


if __name__ == '__main__':
    main()
