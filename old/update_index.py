#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from tinydb import TinyDB
from old.inverted_index import Index
from old.utils import update_index

index = Index()
db_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data", "db.json")
db = TinyDB(db_path)

update_index(db, index)
