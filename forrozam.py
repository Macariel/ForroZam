#!/usr/bin/env python
from __future__ import print_function
import sqlite3
import json
import subprocess
import time
import os
import argparse
import sys

from echoprint_server import decode_echoprint, create_inverted_index, load_inverted_index, query_inverted_index

DIR_NAME = os.path.dirname(__file__)
DB_PATH = os.path.join(DIR_NAME, "data/sqlite.db")
TEST_DATA = os.path.join(DIR_NAME, "data/all_titles.txt")
INDEX_PATH = os.path.join(DIR_NAME, "data/inverted_index")
DB_PROBLEMS = os.path.join(DIR_NAME, "data/db_problems")
INDEX_PROBLEMS = os.path.join(DIR_NAME, "data/index_problems")
ECHOPRINT_BIN = os.path.join(DIR_NAME, "bin/echoprint-codegen")


def main():
    storage = Storage(DB_PATH)
    args = parse_arguments()

    if args.cmd == "find":
        suggestions = storage.find(args.file)

        print("Suggestions:")
        print("{:^16}{}".format("Confidence", "File Name"))
        for s in suggestions:
            print("{:^16.4f}{}".format(s[1], s[0].encode("UTF-8")))

    if args.cmd == "insert":
        storage.insert(args.file)

    if args.cmd == "insert_all":
        storage.insert_from_file(args.file)

    if args.cmd == "create_index":
        storage.create_index()


def parse_arguments():
    parser = argparse.ArgumentParser(description="ForroZam")
    subparsers = parser.add_subparsers(dest="cmd")
    find = subparsers.add_parser("find", help="Looking for matches for the given audio files")
    find.add_argument("file", type=str, help="Audio file for which you want to fetch possible matches")

    insert = subparsers.add_parser("insert", help="Inserting audio files into the database")
    insert.add_argument("file", type=str, help="Audio file which should be added to the database")

    insert_all = subparsers.add_parser("insert_all", help="Insert multiple audio files with a txt containing paths to "
                                                          "the different audio files")
    insert_all.add_argument("file", type=str, help="File containing an absolute path to an audio file, which should be "
                                                   "added to the database, per line")

    subparsers.add_parser("create_index", help="Create the inverted index new from the database")

    if len(sys.argv) < 2:
        parser.print_help()
        exit(0)

    return parser.parse_args()


def create_echoprint(file_path):
    result = subprocess.Popen([ECHOPRINT_BIN, file_path], stdout=subprocess.PIPE)
    return result.communicate()[0]


class Storage:
    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.setup()

    def setup(self):
        c = self.conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS data "
                  "(code TEXT UNIQUE, filename TEXT UNIQUE, artist TEXT, title TEXT, duration INTEGER)")
        self.conn.commit()

    def find(self, file_path):
        index = load_inverted_index([INDEX_PATH])

        code = str(json.loads(str(create_echoprint(file_path)))[0]["code"])
        decoded = decode_echoprint(code)[1]

        suggestions = query_inverted_index(decoded, index, "jaccard")
        return map(lambda x: (self.get_by_id(x["index"]), x["score"]), suggestions)

    def get_by_id(self, id):
        c = self.conn.cursor()
        c.execute("SELECT filename FROM data WHERE rowid=?", (str(id),))
        return c.fetchone()[0]

    def create_index(self):
        with open(INDEX_PROBLEMS, "w+") as f:
            c = self.conn.cursor()

            print("Fetching codes from database...", end="")
            start = time.time()
            c.execute("SELECT rowid, code FROM data ORDER BY rowid ASC")
            rows = c.fetchall()
            print(str(time.time() - start))

            print("Decoding...", end="")
            start = time.time()
            decoded = []
            for rowid, code in rows:
                try:
                    decoded.append(decode_echoprint(str(code))[1])
                except KeyboardInterrupt:
                    raise
                except Exception as e:
                    f.write(str(rowid))
            print(str(time.time() - start))

            print("Creating inverted index...", end="")
            start = time.time()
            create_inverted_index(decoded, INDEX_PATH)
            print(str(time.time() - start))

    def insert_from_file(self, file_path):
        start = time.time()
        with open(file_path) as f:
            lines = f.readlines()
            max = len(lines)
            problems = open(DB_PROBLEMS, "w+")

            for i, line in enumerate(lines):
                line = line.strip()
                print("(%s/%s) Adding %s" % (i + 1, max, line))
                try:
                    self.insert(line)
                except KeyboardInterrupt:
                    raise
                except sqlite3.IntegrityError as e:
                    print("%s already in DB: %s" % (line, e))
                except:
                    problems.write("%s\n" % line)

            problems.flush()
            problems.close()
        print("Done in {}s".format(str(time.time() - start)))

    def insert(self, file_path):
        try:
            output = json.loads(create_echoprint(file_path.decode("UTF-8")))[0]
            metadata = output["metadata"]

            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO data (code, filename, artist, title, duration) VALUES (?, ?, ?, ?, ?)",
                           (output["code"], file_path.decode(encoding='UTF-8'), metadata["artist"], metadata["title"],
                            metadata["duration"]))
            self.conn.commit()
        except ValueError as e:
            print("ValueError: %s" % str(file_path))
            raise e
        except sqlite3.IntegrityError as e:
            print("[WARN] %s" % e)
            raise e


if __name__ == '__main__':
    main()
