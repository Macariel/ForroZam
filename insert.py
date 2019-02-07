#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import json
import os

from tinydb import TinyDB, where, Query, JSONStorage
from tinydb.middlewares import CachingMiddleware
from src.utils import create_echoprint, update_index
from src.index import Index

if len(sys.argv) != 2:
    print("Not enough arguments")
    exit(1)

index = Index()

db_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data", "db.json")
db = TinyDB(db_path, storage=CachingMiddleware(JSONStorage))

already = set(map(lambda x: x["metadata"]["filename"].encode("utf-8"), db.all()))
files = set(map(lambda x: x.strip(), open(sys.argv[1]).readlines())) - already

problems = open("problems", "a+")

length = len(db)

print("Current length %s" % str(length))
try:
    for idx, path in enumerate(files):
        path = path.strip()
        print("(%s/%s) Adding %s" % (str(idx + 1), len(files), path))

        try:
            echoprint = json.loads(create_echoprint(path))[0]
        except ValueError as e:
            problems.write("ValueError: %s\n" % str(path))
            continue

        if not "code" in echoprint or echoprint["code"] == u'':
            problems.write("%s\n" % str(path))
            continue

        echoprint["index"] = str(length + idx)
        db.insert(echoprint)

    #print("Saving and creating index")
    #update_index(db, index)
finally:
    db.close()
    problems.close()


