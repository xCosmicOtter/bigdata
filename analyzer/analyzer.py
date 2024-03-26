import pandas as pd
import numpy as np
import time
from glob import glob
from datetime import datetime
# TODO: import logging

import timescaledb_model as tsdb

db = tsdb.TimescaleStockMarketModel('bourse', 'ricou', 'db', 'monmdp')        # inside docker
#db = tsdb.TimescaleStockMarketModel('bourse', 'ricou', 'localhost', 'monmdp') # outside docker

def parse_filename(filename):
    timestamp_str = filename[21:-4].split()[1:3]
    timestamp_str = ' '.join(timestamp_str)
    return datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S.%f")

def store_file(files, website):
    if website.lower() != "boursorama":
        return
    #  if not db.is_file_done(filename) # Desactivated cz useless for now

    data = {parse_filename(filename): pd.read_pickle(filename) for filename in files}
    df = pd.concat(data).reset_index(level=1, drop=True)
    print(df.head(100))

    # db.df_write(df, 'test1') # To write inside database
    # Write the current file as "stored in the database"
    # We should probably use the "db" instance

if __name__ == '__main__':
    available_years = [2019] #np.arange(2019, 2024)
    markets = ["compA"] #np.array(["amsterdam", "compA", "compB", "peapme"])
    count = 0

    print(f"Work in progress...")
    for year in available_years:
        for market in markets:
            starting_time = time.time()
            path_pattern = f"data/boursorama/{year}/{market}*"

            available_files = np.array(glob(path_pattern))
            for i in range(0, len(available_files), 1000):
                print(f"Batch: {i//1000} of 1K elements")
                store_file(available_files[i:i+1000], "boursorama")

            count += len(available_files)
            print(f"{year}-{market} done on {len(available_files)} files in {time.time() - starting_time} seconds.")

    print(f"Work done on {count} files, in {time.time() - starting_time} seconds.")