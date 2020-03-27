import pandas as pd

STATE_LOGS = "../../data/state_logs.csv"
LOCAL_PAGES = {"WI": "", "IL": "", "RI": ""}


class Local_page_scraper:
    pass


class WI_scraper(Local_page_scraper):
    pass


class IL_scraper(Local_page_scraper):
    pass


class RI_scraper(Local_page_scraper):
    pass


SCRAPER_MAP = {
    "WI": WI_scraper,
    "IL": IL_scraper,
    "RI": RI_scraper,
}


def log_states(state, scraper):
    """
    * get date
    * get data
    * for country in data:
         append county, state, date, data
    """


def get_wide_df_from_local():
    """ use CASES_FROM_1P3A"""
    wide = pd.DataFrame()
    return wide


"""
        for state, scraper in SCRAPER_MAP:
            log_states(state, scraper)
        local_cases = get_wide_df_from_local()
        """
