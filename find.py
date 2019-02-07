#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os

from src.index import Index
from tinydb import TinyDB, Query

import src.utils

index = Index()
possibilities = index.query_file(sys.argv[1])

db_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data", "db.json")
db = TinyDB(db_path)

#print(db.search(Query().metadata.filename.matches(".*Tony Martins.*Lamento.*"))[0]["index"])

ids = map(lambda x: str(x["index"]), possibilities)
results = db.search(Query().index.one_of(ids))

for i, entry in enumerate(possibilities):
    data = filter(lambda x: str(entry["index"]) == x["index"], results)[0]
    print("%s. %s (%s)" % (str(i+1).rjust(2, " "), data["metadata"]["filename"], str(entry["score"])))
