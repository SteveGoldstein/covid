import county_validation as cv
import pdb


def test_my_mode():
    assert cv.get_mode_and_valid_score(3, 1, 2)[0] == 2
    assert cv.get_mode_and_valid_score(3, 2, 2)[0] == 2


def test_do_validation():
    cv.reload_data()
    cases_1 = cv.pd.read_csv(cv.CASES_FROM_1P3A, index_col = 0)

    cases_2 = cases_1.copy()
    cases_2.iloc[0, 0] = cases_2.iloc[0, 0] + 1
    cases_3 = cases_2.copy()
    cases_3.iloc[0, 1] = cases_3.iloc[0, 1] + 1

    cases, cases_valid = cv.do_validation([cases_1, cases_2, cases_3])

    assert cases_2.iloc[0, 0] != cases_1.iloc[0, 0]

    assert cases.iloc[0, 0] == cases_2.iloc[0, 0]
    assert cases.iloc[0, 1] == cases_2.iloc[0, 1]

    assert cases_valid.iloc[0, 0] == 2 / 3
    assert cases_valid.iloc[0, 1] == 2 / 3
    assert cases_valid.iloc[0, 2] == 1


def test_reload_data():
    cv.reload_data()
    for pth in [cv.CASES_FROM_1P3A, cv.DEATHS_FROM_USA_FACTS]:
        assert pth.exists()
        assert cv.timedelta(seconds=cv.UPDATE_FREQ) > (
            cv.datetime.now() - cv.datetime.fromtimestamp(pth.stat().st_mtime)
        )
