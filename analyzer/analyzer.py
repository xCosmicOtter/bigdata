import pandas as pd
import numpy as np
import time
import os
import multiprocessing
from glob import glob
from datetime import datetime
from logzero import logger
from tqdm import tqdm
from collections import defaultdict

import timescaledb_model as tsdb

db = tsdb.TimescaleStockMarketModel('bourse', 'ricou', 'db', 'monmdp')        # inside docker
#db = tsdb.TimescaleStockMarketModel('bourse', 'ricou', 'localhost', 'monmdp') # outside docker

# ---- Utils functions ---- #
def parse_filename(filename: str) -> datetime:
    return datetime.strptime(filename[-30:-4], "%Y-%m-%d %H:%M:%S.%f")

def erase_c(df: pd.DataFrame) -> pd.DataFrame:
    df['last'] = df['last'].astype(str)
    df['last'] = df['last'].str.replace('(c)', '')
    df['last'] = df['last'].str.replace('(s)', '')
    df['last'] = df['last'].str.replace(' ', '')
    df['last'] = df['last'].astype(float)
    return df

def custom_sort_key(file_path: str) -> str:
    return file_path[-22:-4]


# ---- SQL requests functions ---- #
def get_market_id(market_name: str) -> int:
    get_id = db.raw_query(f"SELECT id FROM markets WHERE alias = '{market_name}'")
    return int(get_id[0][0]) if len(get_id) != 0 else None

def get_companies_id():
    return db.df_query('SELECT id, symbol FROM companies', chunksize=None)


# ---- SQL requests functions ---- #
companies_dict = defaultdict(set)

def compute_companies(df: pd.DataFrame, stock_name: str, market_id: int, market_name: str) -> None:
    companies_df = df[['name','symbol']].copy().drop_duplicates()
    companies_df.reset_index(drop=True, inplace=True)
    companies_df['mid'] = market_id

    companies_df['pea'] = market_name == "peapme"
    companies_df['boursorama'] = stock_name == "boursorama"
    companies_df.loc[:, ["symbol_nf", "isin", "reuters", "sector"]] = None

    grouped = set(zip(companies_df["symbol"], companies_df["name"]))

    if market_name == "peapme":
        keys = "('" + "', '".join([symbol for symbol, _ in grouped]) + "')"
        db.execute(f"UPDATE companies SET pea = True WHERE symbol in {keys};")

    before_filter = len(companies_df.symbol)

    # Create the filter
    filter_list = []
    for symbol, name in grouped:
        if symbol in companies_dict:
            filter_list.append((symbol, name))

        companies_dict[symbol].add(name)

    # Applying the filter
    companies_df["tmp_filter"] = list(zip(companies_df["symbol"], companies_df["name"]))
    companies_df = companies_df[~companies_df["tmp_filter"].isin(filter_list)]
    companies_df.drop(columns=["tmp_filter"], inplace=True)

    # Write inside table
    logger.debug(f"Applying filter -> before: {before_filter} elts && after: {len(companies_df.symbol)} elts")
    db.df_write(companies_df, "companies", commit=True, index=False)

def compute_stocks(df: pd.DataFrame, compagnies_df: pd.DataFrame) -> None:
    stock_df = df[['symbol', 'last', 'volume']].copy().drop_duplicates()
    stock_df.reset_index(names='date', inplace=True)

    # Merge stock_df with compagnies_df to get the cid
    stock_df = stock_df.merge(compagnies_df, left_on='symbol', right_on='symbol', how='left')
    stock_df.drop(columns=['symbol'], inplace=True)
    stock_df.rename(columns={'last': 'value', 'id': 'cid'}, inplace=True)
    stock_df['cid'] = stock_df['cid'].fillna(0)

    # Write inside table
    db.df_write(stock_df, 'stocks', commit=True, index=False)

def compute_daystocks(df: pd.DataFrame, compagnies_df: pd.DataFrame) -> None: #TODO: Drop duplicate??
    daystocks_df = df.copy()

    daystocks_df.reset_index(names="timestamp", inplace=True)
    grouped = daystocks_df.groupby(['symbol', daystocks_df['timestamp'].dt.date])

    # Apply aggregations
    daystocks_df = grouped.agg({
        'last': ['last', 'first', "min", "max"],
        'volume': "first",
    })
    daystocks_df.reset_index(inplace=True)

    # Rename columns for better clarity
    daystocks_df.columns = ['symbol', 'date', 'open', 'close', 'low', 'high', 'volume']

    # Merge daystocks_df with compagnies_df to get the cid
    daystocks_df = daystocks_df.merge(compagnies_df, left_on='symbol', right_on='symbol', how='left')
    daystocks_df.drop(columns=['symbol'], inplace=True)
    daystocks_df.rename(columns={'id': 'cid'}, inplace=True)

    # Fill daystocks_df without cid with 0
    daystocks_df['cid'] = daystocks_df['cid'].fillna(0)

    # Write inside table
    db.df_write(daystocks_df, "daystocks", commit=True, index=False)


# ---- MultiProcessing file reading ---- #
num_processes = multiprocessing.cpu_count()

def read_file(filename_index_pair):
    index, filename = filename_index_pair
    return index, parse_filename(filename), pd.read_pickle(filename)


# ---- Store files ---- #
def store_file(files: list, website: str, market_name: str, market_id: int) -> None:
    if website.lower() != "boursorama":
        return

    data = {}

    start = time.time()
    filenames_with_index = list(enumerate(files))

    pool = multiprocessing.Pool(processes=num_processes)
    results = pool.map(read_file, filenames_with_index)

    # Close and release resources
    pool.close()
    pool.join()

    # Sort the results by the original index
    sorted_results = sorted(results, key=lambda x: x[0])

    # Add the sorted results into the data dictionary
    for _, key, value in sorted_results:
        data[key] = value
    logger.debug(f"MULTITHREADING: Time taken to read files {time.time() - start}")

    """ # OLD PROCESS

    start = time.time()
    for filename in files:
        #if db.is_file_done(filename): # TODO: add when PC has low memory
        #    continue

        # Add in final fidctionary
        data[parse_filename(filename)] = pd.read_pickle(filename)
    logger.debug(f"Time taken to read files {time.time() - start}")

    """

    # CONCAT FINAL DATA
    start = time.time()
    df = pd.concat(data).reset_index(level=1, drop=True)
    logger.debug(f"Time taken to concat files {time.time() - start}")

    # CLEAN DATA
    df.drop_duplicates(inplace=True)
    df.index = pd.to_datetime(df.index)
    erase_c(df)
    overflow_mask = df['volume'] > 2147483647
    df.loc[overflow_mask, 'volume'] = np.iinfo(np.int32).max

    start = time.time()
    compute_companies(df, website, market_id, market_name)
    logger.debug(f"Time taken to compute companies {time.time() - start}")

    compagnies_df = get_companies_id()

    start = time.time()
    compute_stocks(df, compagnies_df)
    logger.debug(f"Time taken to compute stocks {time.time() - start}")

    start = time.time()
    compute_daystocks(df, compagnies_df)
    logger.debug(f"Time taken to compute daystocks {time.time() - start}")

    # Write the files as processed
    start = time.time()
    db.df_write(pd.DataFrame({'name': files}), "file_done", commit=True, index=False)
    logger.debug(f"Time taken to save done files {time.time() - start}")


# ---- Main loop ---- #
def main() -> None:
    # MAIN ARGS
    files_count = 0
    data_path = "data"

    # MAIN PROCESS
    logger.debug(f"Work in progress...")
    starting_time = time.time()
    for stock in os.listdir(data_path):
        stock_path = f"{data_path}/{stock}"

        for year in sorted(os.listdir(stock_path), reverse=True):
            market_pattern = f"{data_path}/{stock}/{year}/*"

            available_files = glob(market_pattern)
            available_files = sorted(available_files, key=custom_sort_key)

            market_files = defaultdict(lambda: defaultdict(list))

            # Organize files into separate lists based on the market name
            for file_path in available_files:
                market_name, date, _ = os.path.basename(file_path[:-4]).split()
                month = date.split('-')[1]
                market_files[market_name][month].append(file_path)

            # Sort days inside month dicts
            for market_name, month_dict in market_files.items():
                for file_list in month_dict.values():
                    file_list.sort(reverse=True, key=custom_sort_key)

            # Work on the data with batches (represented by month)
            for market_name, month_dict in sorted(market_files.items()):
                logger.debug(f"Loading {market_name} ({year}) data for {stock}.")
                market_starting_time = time.time()

                market_id = get_market_id(market_name)
                for month, files_list in sorted(month_dict.items(), reverse=True):
                    files_count += len(files_list)

                    store_file(files_list, stock, market_name, market_id)

                subprocessing_time = round(time.time() - market_starting_time, 3)
                logger.debug(f"Processing complete for {market_name} data in {year} in"
                            f" {subprocessing_time} seconds.")

    rounded_processing_time = round(time.time() - starting_time, 3)
    logger.debug(f"Work done on {files_count} files, in {rounded_processing_time} seconds.")

if __name__ == '__main__':
    main()
