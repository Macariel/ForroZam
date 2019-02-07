import subprocess
import os
from echoprint_server import decode_echoprint

real_path = os.path.dirname(os.path.realpath(__file__))


def create_echoprint(file_path):
    path = "%s/echoprint-codegen" % real_path
    result = subprocess.Popen([path, file_path], stdout=subprocess.PIPE)
    return result.communicate()[0]


def adjust_indices(db):
    update = db.all()
    for idx, entry in enumerate(update):
        entry["index"] = str(idx)
    db.write_back(update)


def update_index(db, index):
    print("Updating indices ...")
    adjust_indices(db)

    print("Decoding echoprints ...")
    all_codes = list(map(lambda x: decode_echoprint(str(x["code"]))[1], db.all()))

    print("Creating Index ...")
    index.create_new_index_from_data(all_codes)