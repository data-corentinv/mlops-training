import pytest
import pandas as pd
import numpy as np

from colibrimmo.pipelines.catch_price_per_m2.nodes import create_price_per_m2_feature

ads_in = pd.DataFrame(
    {
        "id": {0: 95, 1: 634705, 2: 1205876},
        "iris_insee_code": {0: 593500104, 1: 840350102, 2: 661240000},
        "city_insee_code": {0: "A1014", 1: "A1015", 2: "A1016"},
        "postal_code": {0: 59800, 1: 62145, 2: 75019},
    }
)

kpis_city = pd.DataFrame(
    {
        "city_insee_code": {0: "A1014", 1: "A1015", 2: "A1016"},
        "price_per_m2_median": {0: 1000.0, 1: np.nan, 2: np.nan},
        "price_per_m2_mean": {0: 1000.0, 1: np.nan, 2: np.nan},
    }
)

kpis_dep = pd.DataFrame(
    {
        "department_insee_code": {0: "59", 1: "62"},
        "price_per_m2_median": {0: 4562.5, 1: 1731.8796296296296},
        "price_per_m2_mean": {0: 4351.445574984067, 1: 1702.5436113403516},
    }
)

kpis_postal = pd.DataFrame(
    {
        "postal_code": {0: 59800, 1: 62145},
        "price_per_m2_median": {0: 1000.0, 1: 1773.7938596491226},
        "price_per_m2_mean": {0: 1000.0, 1: 1728.637377168457},
    }
)

departments = pd.DataFrame(
    {
        "insee_code": {0: "75", 1: "59", 2: "62"},
        "region_insee_code": {0: "4", 1: "3", 2: "2"},
    }
)

kpis_regions = pd.DataFrame(
    {
        "region_insee_code": {0: "4", 1: "3", 2: "2"},
        "price_per_m2_median": {
            0: 3879.953679876479,
            1: 1983.7684481216454,
            2: 1940.84207896052,
        },
        "price_per_m2_mean": {
            0: 6929.353749182469,
            1: 2929.7537491824687,
            2: 1929.6537491824688,
        },
    }
)

ads_expected_types = {
    "id": int,
    "iris_insee_code": int,
    "city_insee_code": str,
    "postal_code": int,
    "department_insee_code": str,
    "price_per_m2_median_city": float,
    "price_per_m2_median_postal_code": float,
    "price_per_m2_median_department": float,
    "insee_code": str,
    "region_insee_code": str,
    "price_per_m2_median_regions": float,
    "price_per_m2": float,
}

preprocessing_params = {
    "price_method": "median",
    "boolean_features": [
        "has_terrace",
        "has_swimming_pool",
        "has_chimney",
        "has_elevator",
    ],
    "categories": ["apartment_type"],
    "numericals": ["price_per_m2", "carrez_surface"],
    "target": "price",
    "keys": ["id", "city_insee_code"],
}

ads_expected = pd.DataFrame(
    {
        "id": {0: 95, 1: 634705, 2: 1205876},
        "iris_insee_code": {0: 593500104, 1: 840350102, 2: 661240000},
        "city_insee_code": {0: "A1014", 1: "A1015", 2: "A1016"},
        "postal_code": {0: 59800, 1: 62145, 2: 75019},
        "department_insee_code": {0: "59", 1: "62", 2: "75"},
        "price_per_m2_median_city": {0: 1000.0, 1: np.nan, 2: np.nan},
        "price_per_m2_median_postal_code": {
            0: 1000.0,
            1: 1773.7938596491226,
            2: np.nan,
        },
        "price_per_m2_median_department": {0: 4562.5, 1: 1731.8796296296296, 2: np.nan},
        "insee_code": {0: "59", 1: "62", 2: "75"},
        "region_insee_code": {0: "3", 1: "2", 2: "4"},
        "price_per_m2_median_regions": {
            0: 1983.7684481216454,
            1: 1940.84207896052,
            2: 3879.953679876479,
        },
        "price_per_m2": {0: 1000.0, 1: 1773.7938596491226, 2: 3879.953679876479},
    }
)


@pytest.mark.parametrize(
    "ads_in, departments, kpis_city, kpis_dep, kpis_postal, kpis_regions, preprocessing_params, ads_expected",
    [
        (
            ads_in,
            departments,
            kpis_city,
            kpis_dep,
            kpis_postal,
            kpis_regions,
            preprocessing_params,
            ads_expected,
        ),
    ],
)
def test_create_price_per_m2_feature(
    ads_in,
    departments,
    kpis_city,
    kpis_dep,
    kpis_postal,
    kpis_regions,
    preprocessing_params,
    ads_expected,
):
    output = create_price_per_m2_feature(
        ads_in,
        departments,
        kpis_city,
        kpis_dep,
        kpis_postal,
        kpis_regions,
        preprocessing_params,
    )
    pd.testing.assert_frame_equal(output, ads_expected)
