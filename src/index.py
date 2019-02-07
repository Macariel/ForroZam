#!/usr/bin/env python

from __future__ import print_function
import os
import json

from echoprint_server import load_inverted_index, inverted_index_size, \
    decode_echoprint, create_inverted_index, query_inverted_index

from utils import create_echoprint

INDEX_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "index"))
INDEX_NAME = "inverted_index"


class Index:
    def __init__(self):
        self.index = self.load()

    def create_new_index_from_data(self, data):
        create_inverted_index(data, os.path.join(INDEX_DIR, INDEX_NAME))
        self.load()

    def load(self):
        indices = map(lambda x: os.path.join(INDEX_DIR, x), os.listdir(INDEX_DIR))
        self.index = load_inverted_index(indices)
        return self.index

    def size(self):
        return inverted_index_size(self.index)

    def query(self, echoprint):
        echoprint_code = str(json.loads(echoprint)[0]["code"])
        decoded = decode_echoprint(echoprint_code)[1]
        return query_inverted_index(decoded, self.index, "jaccard")

    def query_file(self, file_path):
        return self.query(create_echoprint(file_path))
