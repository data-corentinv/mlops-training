import pytest
import pandas as pd
import numpy as np

from colibrimmo.pipelines.data_correction.nodes import (
    drop_price_extreme_values,
    drop_carrez_surface_extreme_values,
)


median_std_dict = {"group": [1, 2], "median": [9.0, 19.0], "std": [1.732051, np.nan]}
median_std_df = pd.DataFrame(median_std_dict).set_index("group")

ads_in_dict = {
    "id": {0: 95, 1: 634705},
    "parution_date": {0: "2020-05-01 16:41:31.807845", 1: "2020-06-27 03:52:51.491283"},
    "iris_insee_code": {0: "593500104", 1: "840350102"},
    "city_insee_code": {0: "59350", 1: "84035"},
    "postal_code": {0: "59800", 1: "84300"},
    "price": {0: 2279000.0, 1: 86000.0},
    "price_without_agency_fees": {0: 2200000.0, 1: 86000.0},
}

ads_expected_dict = {
    "id": {1: 634705},
    "parution_date": {1: "2020-06-27 03:52:51.491283"},
    "iris_insee_code": {1: "840350102"},
    "city_insee_code": {1: "84035"},
    "postal_code": {1: "84300"},
    "price": {1: 86000.0},
    "price_without_agency_fees": {1: 86000.0},
}

ads_in = pd.DataFrame(ads_in_dict)
ads_expected = pd.DataFrame(ads_expected_dict)


@pytest.mark.parametrize(
    "ads, value, expected", [(ads_in, 1e5, ads_expected),],
)
def test_drop_price_extreme_values(ads, value, expected):
    result = drop_price_extreme_values(ads, value)
    pd.testing.assert_frame_equal(expected, result)


input_dict = {
    "id": {
        0: 95,
        1: 634705,
        2: 1205876,
        3: 791463,
        4: 728838,
        5: 635047,
        6: 635048,
        7: 634769,
        8: 635059,
        9: 357696,
    },
    "carrez_surface": {
        0: 425.0,
        1: 38.0,
        2: 50.0,
        3: 58.0,
        4: 80.0,
        5: 37.3,
        6: 92.0,
        7: 52.4,
        8: 64.0,
        9: 120.65,
    },
    "apartment_type": {
        0: "T5-or-higher",
        1: "T2",
        2: "T2",
        3: "T4",
        4: "T3",
        5: "studio-T1",
        6: "T4",
        7: "T2",
        8: "T2",
        9: "T5-or-higher",
    },
}
df_input = pd.DataFrame(input_dict)
expected_dict = {
    "id": {
        1: 634705,
        2: 1205876,
        7: 634769,
        8: 635059,
        3: 791463,
        6: 635048,
        0: 95,
        9: 357696,
    },
    "carrez_surface": {
        1: 38.0,
        2: 50.0,
        7: 52.4,
        8: 64.0,
        3: 58.0,
        6: 92.0,
        0: 425.0,
        9: 120.65,
    },
    "apartment_type": {
        1: "T2",
        2: "T2",
        7: "T2",
        8: "T2",
        3: "T4",
        6: "T4",
        0: "T5-or-higher",
        9: "T5-or-higher",
    },
}
df_expected = pd.DataFrame(expected_dict)


@pytest.mark.parametrize(
    "ads, nb_std, expected", [(df_input, 3, df_expected)],
)
def test_drop_carrez_surface_extreme_values(ads, nb_std, expected):
    result = drop_carrez_surface_extreme_values(ads, nb_std)
    pd.testing.assert_frame_equal(expected, result)
