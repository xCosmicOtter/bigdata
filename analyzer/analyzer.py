import pandas as pd
import numpy as np
import time
import os
import multiprocessing
from glob import glob
from datetime import datetime
from collections import defaultdict

import timescaledb_model as tsdb

db = tsdb.TimescaleStockMarketModel('bourse', 'ricou', 'db', 'monmdp')        # inside docker
# db = tsdb.TimescaleStockMarketModel('bourse', 'ricou', 'localhost', 'monmdp') # outside docker

# ---- Utils functions ---- #
def parse_filename(filename: str) -> datetime:
    return datetime.strptime(filename[-30:-4], "%Y-%m-%d %H:%M:%S.%f")


def clean_values_volumes(df: pd.DataFrame) -> None:
    # Clean values
    df['last'] = df['last'].astype(str)
    df['last'] = df['last'].str.replace('(c)', '')
    df['last'] = df['last'].str.replace('(s)', '')
    df['last'] = df['last'].str.replace(' ', '')
    df['last'] = df['last'].astype(float)

    # Clean volumes
    overflow_mask = df['volume'] > 2147483647
    df.loc[overflow_mask, 'volume'] = np.iinfo(np.int32).max


def custom_sort_key(file_path: str) -> str:
    return file_path[-22:-4]


def count_files(directory: str) -> int:
    file_count = 0
    for _, _, files in os.walk(directory):
        file_count += len(files)
    return file_count


# ---- SQL requests functions ---- #
def get_market_id(market_name: str) -> int:
    get_id = db.raw_query(
        f"SELECT id FROM markets WHERE alias = '{market_name}'")
    return int(get_id[0][0]) if len(get_id) != 0 else None


def get_companies_id() -> pd.DataFrame:
    return db.df_query('SELECT id, symbol FROM companies', chunksize=None)


def get_files_done_count() -> int:
    query = """
            SELECT COUNT(DISTINCT name) AS num_elements
            FROM file_done;
            """
    get_id = db.raw_query(query)
    return int(get_id[0][0]) if len(get_id) != 0 else None


# ---- SQL requests functions ---- #
companies_dict = defaultdict(set)


def compute_companies(df: pd.DataFrame, stock_name: str, market_id: int, market_name: str) -> None:
    companies_df = df[['name', 'symbol']].copy().drop_duplicates()
    companies_df.reset_index(drop=True, inplace=True)

    # Fill companies_df without cid with 0 (peapme)
    companies_df['mid'] = market_id or 0

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
    companies_df["tmp_filter"] = list(
        zip(companies_df["symbol"], companies_df["name"]))
    companies_df = companies_df[~companies_df["tmp_filter"].isin(filter_list)]
    companies_df.drop(columns=["tmp_filter"], inplace=True)

    # Write inside table
    print(f"Filtering companies: Initial count = {before_filter}, Final count = {len(companies_df.symbol)}.")
    db.df_write(companies_df, "companies", commit=True, index=False)


def compute_stocks(df: pd.DataFrame, compagnies_df: pd.DataFrame, sdb: tsdb.TimescaleStockMarketModel) -> None:
    stock_df = df[['symbol', 'last', 'volume']].copy()

    # Apply deduplication
    stock_df = stock_df[~stock_df.duplicated(keep='first') | ~stock_df.duplicated(keep='last')]
    stock_df.reset_index(names='date', inplace=True)

    # Merge stock_df with compagnies_df to get the cid
    stock_df = stock_df.merge(
        compagnies_df, left_on='symbol', right_on='symbol', how='left')
    stock_df.drop(columns=['symbol'], inplace=True)
    stock_df.rename(columns={'last': 'value', 'id': 'cid'}, inplace=True)

    # Write inside tables
    sdb.df_write(stock_df, 'stocks', commit=True, index=False)


def compute_daystocks(df: pd.DataFrame, compagnies_df: pd.DataFrame, sdb: tsdb.TimescaleStockMarketModel) -> None:
    daystocks_df = df.copy()
    daystocks_df.reset_index(names="timestamp", inplace=True)

    # Apply aggregations
    daystocks_df = daystocks_df.groupby(['symbol', daystocks_df['timestamp'].dt.date]).agg({
        'last': ['first', 'last', "min", "max", "mean", "std"],
        'volume': "first",
    }).reset_index()

    # Rename columns for better clarity
    daystocks_df.columns = ['symbol', 'date', 'open', 'close',
                            'low', 'high', 'average', 'standard_deviation', 'volume']

    # Merge daystocks_df with compagnies_df to get the cid
    daystocks_df = daystocks_df.merge(
        compagnies_df, left_on='symbol', right_on='symbol', how='left')
    daystocks_df.drop(columns=['symbol'], inplace=True)
    daystocks_df.rename(columns={'id': 'cid'}, inplace=True)

    # Round average and standard_deviation values
    daystocks_df['average'] = daystocks_df['average'].round(3)
    daystocks_df['standard_deviation'] = daystocks_df['standard_deviation'].round(3)

    # Write inside tables
    sdb.df_write(daystocks_df, "daystocks", commit=True, index=False)


# ---- MultiProcessing file reading ---- #
num_processes = multiprocessing.cpu_count()


def read_file(filename_index_pair: tuple) -> tuple:
    index, filename = filename_index_pair
    return index, parse_filename(filename), pd.read_pickle(filename)


def read_files_multiprocessed(filenames_with_index: list) -> dict:
    data = {}

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
    return data


def process_data(args: tuple) -> None:
    day_df, compagnies_df = args
    sdb = tsdb.TimescaleStockMarketModel(
        'bourse', 'ricou', 'db', 'monmdp', is_sub=True)
    compute_stocks(day_df, compagnies_df, sdb)
    compute_daystocks(day_df, compagnies_df, sdb)


def compute_stocks_daystocks(df: pd.DataFrame, compagnies_df: pd.DataFrame) -> None:
    daily_infos = []
    for _, day_df in df.groupby(pd.Grouper(freq='D')):
        if day_df.empty:
            continue

        daily_infos.append((day_df, compagnies_df))

    pool = multiprocessing.Pool(processes=num_processes)
    pool.map(process_data, daily_infos)

    # Close and release resources
    pool.close()
    pool.join()


# ---- Store files ---- #
def store_file(files: list, website: str, market_name: str, market_id: int) -> None:
    if website.lower() != "boursorama":
        return

    # READ FILES DATA
    start = time.time()
    filenames_with_index = list(enumerate(files))
    data = read_files_multiprocessed(filenames_with_index)
    print(f"Reading files took {round(time.time() - start, 2)} seconds.")

    # CONCAT FINAL DATA
    start = time.time()
    df = pd.concat(data).reset_index(level=1, drop=True)
    print(f"Concatenating dataframes took {round(time.time() - start, 2)} seconds.")

    # CLEAN DATA
    df.index = pd.to_datetime(df.index)
    clean_values_volumes(df)

    # COMPUTE COMPANIES
    start = time.time()
    compute_companies(df, website, market_id, market_name)
    print(f"Computing companies took {round(time.time() - start, 2)} seconds.")

    compagnies_df = get_companies_id()

    # COMPUTE STOCKS and DAYSTOCKS
    start = time.time()
    compute_stocks_daystocks(df, compagnies_df)
    print(
        f"Computing stocks/daystocks took {round(time.time() - start, 2)} seconds.")

    # Check the files as processed
    start = time.time()
    db.df_write(pd.DataFrame({'name': files}),
                "file_done", commit=True, index=False)
    print(f"Saving processed files took {round(time.time() - start, 2)} seconds.\n")


# ---- Main loop ---- #
def main() -> None:
    # MAIN ARGS
    files_count = 0
    data_path = "data"

    # MAIN PROCESS
    print(f"Work in progress on {num_processes} CPU cores...\n")
    starting_time = time.time()
    for stock in os.listdir(data_path):
        stock_path = f"{data_path}/{stock}"

        for year in sorted(os.listdir(stock_path), reverse=True):
            starting_year_time = time.time()
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
                market_starting_time = time.time()

                market_id = get_market_id(market_name)
                for month, files_list in sorted(month_dict.items(), reverse=True):
                    files_count += len(files_list)
                    print(f"# Loading {len(files_list)} files for {stock}/{market_name} ({month}/{year}).")

                    store_file(files_list, stock, market_name, market_id)

                subprocessing_time = round(time.time() - market_starting_time, 3)
                print(f"# = Processing complete for {market_name} data in {year} in"
                             f" {subprocessing_time} seconds. = #\n")

            yearprocessing_time = round(time.time() - starting_year_time, 3)
            print(
                f"# === Processing complete for {year} in {yearprocessing_time} seconds. === #\n")

    rounded_processing_time = round(time.time() - starting_time, 3)
    print(
        f"Work done on {files_count} files, in {rounded_processing_time} seconds ({rounded_processing_time // 60} minutes)")


if __name__ == '__main__':
    data_directory = os.path.join(os.getcwd(), "data")
    files_processed = get_files_done_count()
    files_to_process = count_files(data_directory)

    if files_processed is None or files_processed == 0:
        main()
        print('Done.')
    elif files_processed == files_to_process:
        print(f'Already Done on {files_processed} files.')
    else:
        print(f"Files are missing: {files_to_process = } and {files_processed = }.\n",
               "-> If this is not normal, please delete the TimescaleDB database and relaunch the program.")
