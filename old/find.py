#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import time

from old.inverted_index import Index
from tinydb import TinyDB, Query

index = Index()
start = time.time()
possibilities = index.query_file(sys.argv[1])
print("Index: %s" % str(time.time() - start))

db_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data", "metadata.json")
db = TinyDB(db_path)


start = time.time()
ids = map(lambda x: str(x["index"]), possibilities)
results = db.search(Query().index.one_of(ids))
print("DB: %s" % str(time.time() - start))

for i, entry in enumerate(possibilities):
    data = filter(lambda x: str(entry["index"]) == x["index"], results)[0]
    print("%s. %s (%s)" % (str(i+1).rjust(2, " "), data["filename"], str(entry["score"])))
