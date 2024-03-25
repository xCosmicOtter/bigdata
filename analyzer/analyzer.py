import pandas as pd
import numpy as np
import sklearn
import time
import os
# TODO: import logging
from pathlib import Path

import timescaledb_model as tsdb

db = tsdb.TimescaleStockMarketModel('bourse', 'ricou', 'db', 'monmdp')        # inside docker
#db = tsdb.TimescaleStockMarketModel('bourse', 'ricou', 'localhost', 'monmdp') # outside docker

def store_file(name, website):
    if db.is_file_done(name):
        return
    if website.lower() != "boursorama":
        return

    """
    try:
        df = pd.read_pickle("bourse/data/boursorama/" + name)  # is this dir ok for you ?
    except:
        year = name.split()[1].split("-")[0]
        df = pd.read_pickle("bourse/data/boursorama/" + year + "/" + name)
    # to be finished
    """

    for file in filepaths: #TODO: update needed
        starting_time = time.time()
        df = pd.concat()

        print(f"-> {file} loaded in {time.time() - starting_time} seconds.")

        # Write the current file as "stored in the database"
        # We should probably use the "db" instance

if __name__ == '__main__':
    year = 2020
    directory_path = f"data/boursorama/{year}"
    starting_time = time.time()

    count = 0
    for _, _, filenames in os.walk(directory_path):
        for filename in filenames:
            count += 1
            store_file(filename, "boursorama")

    print(f"Work done on {count} files, in {time.time() - starting_time} seconds.")