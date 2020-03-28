""" Problem: 
* Turn cases.csv into wide format
467,2020-03-10,WA,Island,1,0
702,2020-03-12,WA,Island,2,0
958,2020-03-13,WA,Island,3,0
1677,2020-03-16,WA,Island,1,0
2015,2020-03-17,WA,Island,7,0
2445,2020-03-18,WA,Island,2,0

County, State, 2020-03-10, 2020-03-11, 2020-03-12, 2020-03-13, 2020-03-14, 2020-03-15, 2020-03-16, 2020-03-17, 2020-03-18
Island, WA, 1, 1, 3, 6, 6, 6, 7, 14, 16

* Repeat for FactsUSA and Coronavirus scraper

* generate Valid tags
* Write cases_wide.csv
* Write cases_valid.cs

"""
import time
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
from itertools import accumulate
import pdb

here = Path(__file__).parent

CASES_FROM_1P3A = Path(here / "../data/cases.csv")
out_path = Path(here / "../data/validation")


def add_missing_date_cols(df, start="2020-01-21", end=None):
    fmt = "%Y-%m-%d"
    start = datetime.strptime(start, fmt)
    last_date_w_data = datetime.date(datetime.strptime(df.columns[-1], fmt))
    if end:
        end = datetime.strptime(end, fmt)
    else:
        end = datetime.now()
    for d_i, dt in enumerate(
        pd.date_range(datetime.date(start), datetime.date(end))
    ):
        dt_str = dt.strftime(fmt)
        if dt_str not in df.columns:
            df.insert(d_i, dt_str, np.nan)
        if dt < pd.to_datetime(last_date_w_data):
            df[dt_str].fillna(0, inplace=True)


def get_wide_df_from_1p3a():
    # Read csv:, i, state, county, date, cases, deaths
    # create df with (state,county,date) as index
    narrow = pd.read_csv(
        CASES_FROM_1P3A, index_col=[1, 2, 0], usecols=[1, 2, 3, 4, 5]
    )

    # multiple vals for same date, so we want to sum:
    narrow = (
        narrow.groupby(narrow.index)["confirmed_count", "death_count"]
        .sum()
        .reset_index()
    )

    # pivot, but first get date back & reset index
    narrow["date"] = narrow["index"].apply(lambda x: x[2])
    narrow["index"] = narrow["index"].apply(lambda x: x[:2])
    narrow = narrow.set_index("index")
    cases = narrow.pivot(columns="date", values="confirmed_count")
    deaths = narrow.pivot(columns="date", values="death_count")

    # make sure we're not missing any cols, NANs -> 0
    # take advantage of df mutability
    for df in cases, deaths:
        add_missing_date_cols(df)

    return (cases, deaths)

def get_agg(df):
    return df.cumsum(axis=1, skipna=False)

def do_validation(ip3a, factsusa, cv_scraper):
    """
    * make sure we have matching columns - add dates if we need to 
    * write (ip3a_cases - local_cases == 0).to_csv() to VALIDATION_OUT
    """
    pass


def main():
    while True:
        (ip3a_cases, _) = get_wide_df_from_1p3a()
        ip3a_cases_agg = get_agg(ip3a_cases)

        (ip3a_cases_2, _) = get_wide_df_from_1p3a()
        ip3a_cases_2.iloc[0,0] = ip3a_cases_2.iloc[0,0] + 1
        ip3a_cases_2_agg = get_agg(ip3a_cases_2)

        (ip3a_cases_3, _) = get_wide_df_from_1p3a()
        ip3a_cases_3.iloc[0,1] = ip3a_cases_2.iloc[0,1] + 1
        ip3a_cases_3.iloc[0,2] = ip3a_cases_2.iloc[0,2] + 1
        ip3a_cases_3_agg = get_agg(ip3a_cases_3)

        do_validation(ip3a_cases, ip3a_cases_2, ip3a_cases_3)

        time.sleep(3600)


if __name__ == "__main__":
    main()
