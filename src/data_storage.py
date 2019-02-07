#!/usr/bin/env python
import os
import json

from echoprint_server import decode_echoprint

DATA_DIR = "data"
MAX_PER_FILE = 10

CODES_FILE = "codes_%s.data"
METADATA_FILE = "metadata_%s.json"


class DataStorage:
    def __init__(self):
        if not os.path.isdir(DATA_DIR):
            os.makedirs(DATA_DIR)
        self.metadata = self._load_data_file(METADATA_FILE)
        self.codes = self._load_data_file(CODES_FILE)

    def add(self, echoprint):
        data = json.loads(echoprint)[0]

        self.metadata.append(data["metadata"])
        self.codes.append(decode_echoprint(str(data["code"]))[1])

    def save(self):
        self._save_data_file(self.metadata, METADATA_FILE)
        self._save_data_file(self.codes, CODES_FILE)

    @staticmethod
    def _save_data_file(data, file_name, part="01"):
        with open(os.path.join(DATA_DIR, file_name % part), "w+") as f:
            f.write(json.dumps(data))
            f.flush()
            f.close()

    @staticmethod
    def _load_data_file(file_name, part="01"):
        content = open(os.path.join(DATA_DIR, file_name % part), "a+").read().strip()
        if content:
            return json.loads(content)
        return []

    def get_codes(self):
        # load all parts and concat
        return self.codes

    def get_metadata_for(self, index):
        assert 0 <= index < len(self.metadata)
        return self.metadata[index]
