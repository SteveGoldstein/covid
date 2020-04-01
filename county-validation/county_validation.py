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
import urllib.request
import time
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from statistics import mode, median

UPDATE_FREQ = 72 * 3600

here = Path(__file__).parent
validation_out_dir = Path(here / "../data/validation")
raw_dir = validation_out_dir / "raw"

CASES_FROM_1P3A = validation_out_dir / "cases_1P3A.csv"
DEATHS_FROM_1P3A = validation_out_dir / "deaths_1P3A.csv"
RAW_1P3A = raw_dir / "raw_1P3A.csv"
URL_1P3A = "https://instant.1point3acres.com/v1/api/coronavirus/us/cases?token=PFl0dpfo"

CASES_FROM_USA_FACTS = validation_out_dir / "cases_usa_f.csv"
RAW_USA_F_CASES = raw_dir / "raw_usa_f_cases.csv"
URL_USA_FACTS_CASES = "https://usafactsstatic.blob.core.windows.net/public/data/covid-19/covid_confirmed_usafacts.csv"

DEATHS_FROM_USA_FACTS = validation_out_dir / "deaths_usa_f.csv"
RAW_USA_F_DEATHS = raw_dir / "raw_usa_f_deaths.csv"
URL_USA_FACTS_DEATHS = "https://usafactsstatic.blob.core.windows.net/public/data/covid-19/covid_deaths_usafacts.csv"


def is_data_too_old(path):
    return datetime.now() - datetime.fromtimestamp(
        path.stat().st_mtime
    ) > timedelta(seconds=UPDATE_FREQ)


def reload_data():
    for path in PATH_TO_URL:
        if not path.exists() or is_data_too_old(path):
            (url, raw, transform) = (
                PATH_TO_URL[path]["url"],
                PATH_TO_URL[path]["raw"],
                PATH_TO_URL[path]["transform"],
            )
            urllib.request.urlretrieve(url, raw)
            transform(raw, path)


def transform_usa_facts(in_path, out_path):
    data = pd.read_csv(in_path, index_col=[1, 2]).drop(
        columns=["countyFIPS", "stateFIPS"]
    )
    data.to_csv(out_path)


def transform_1p3a_narrow_to_wide(in_path, _):
    # Read csv:, i, state, county, date, cases, deaths
    # create df with (state,county,date) as index
    narrow = pd.read_csv(in_path, index_col=[1, 2, 0], usecols=[1, 2, 3, 4, 5])

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

    cases.to_csv(CASES_FROM_1P3A)
    deaths.to_csv(DEATHS_FROM_1P3A)


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


def get_agg(df):
    return df.cumsum(axis=1, skipna=False)


def get_mode_and_valid_score(*args):
    # all unique? use median. Else, use mode.
    if len(set(args)) == len(args):
        my_mode = median(args)
    else:
        my_mode = mode(args)
    valid_score = len([el for el in args if el == my_mode]) / len(args)
    return (my_mode, valid_score)


def do_validation(cases_collection):
    """stackoverflow.com/questions/42277400/apply-a-function-element-wise-to-two-dataframes

    m_and_v = np.vectorize(get_mode_and_valid_score)(cases_collection)
    cases = m_and_v.applymap(lambda x: x[0])
    valid_score = m_and_v.applymap(lambda x: x[1])

    Didn't work, likely because my function returns a tuple, not a float.
    Going the clunky route for now. 
    """
    shape = cases_collection[0].shape
    for df in cases_collection[1:]:
        assert df.shape == shape, "df not shaped same, missing date?"

    cases = pd.DataFrame(np.nan, index=df.index, columns=df.columns)
    valid_score = cases.copy()

    for i in range(shape[0]):
        for j in range(shape[1]):
            args = [el.iloc[i, j] for el in cases_collection]
            if np.nan not in args:
                (
                    cases.iloc[i, j],
                    valid_score.iloc[i, j],
                ) = get_mode_and_valid_score(*args)

    return (cases, valid_score)


PATH_TO_URL = {
    CASES_FROM_1P3A: {
        "raw": RAW_1P3A,
        "url": URL_1P3A,
        "transform": transform_1p3a_narrow_to_wide,
    },
    DEATHS_FROM_1P3A: {
        "raw": RAW_1P3A,
        "url": URL_1P3A,
        "transform": transform_1p3a_narrow_to_wide,
    },
    CASES_FROM_USA_FACTS: {
        "raw": RAW_USA_F_CASES,
        "url": URL_USA_FACTS_CASES,
        "transform": transform_usa_facts,
    },
    DEATHS_FROM_USA_FACTS: {
        "raw": RAW_USA_F_DEATHS,
        "url": URL_USA_FACTS_DEATHS,
        "transform": transform_usa_facts,
    },
}


def main():
    while True:
        reload_data()
        # do_validation(ip3a_cases, ip3a_cases_2, ip3a_cases_3)

        time.sleep(UPDATE_FREQ)


if __name__ == "__main__":
    main()
