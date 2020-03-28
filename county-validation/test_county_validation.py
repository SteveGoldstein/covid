import county_validation as cv
import pdb

def test_get_agg():
    (cases, deaths) = cv.get_wide_df_from_1p3a()
    cases_agg = cv.get_agg(cases)




