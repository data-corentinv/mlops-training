import pandas as pd
import pytest
from colibrimmo.pipelines.catch_price_per_m2.utils import merge_ads_with_kpis_price

types = {
    "id": int,
    "parution_date": str,
    "iris_insee_code": int,
    "city_insee_code": str,
    "postal_code": int,
    "price": float,
    "price_without_agency_fees": float,
    "via_agency": bool,
    "buyer_pays_fees": bool,
    "seller_pays_fees": bool,
    "condominium_fees": float,
    "land_fees": float,
    "tenant_in_place": bool,
    "is_under_1948_law": bool,
    "is_auction": bool,
    "construction_year": float,
    "habitation_type": str,
    "total_surface": float,
    "carrez_surface": float,
    "terrace_surface": float,
    "balcony_surface": float,
    "garden_surface": float,
    "cellar_surface": float,
    "n_rooms": int,
    "n_bedrooms": float,
    "n_bathrooms": float,
    "n_wcs": float,
    "n_service_rooms": float,
    "has_terrace": bool,
    "has_balcony": bool,
    "has_garden": float,
    "has_parking": bool,
    "has_cellar": bool,
    "has_box": bool,
    "has_elevator": bool,
    "has_swimming_pool": bool,
    "has_intercom": bool,
    "has_chimney": bool,
    "heating_type": str,
    "heating_nature": str,
    "kitchen_nature": str,
    "has_equipped_kitchen": bool,
    "has_double_glazing": float,
    "orientation": float,
    "has_great_view": float,
    "energetic_performance_diagnostic_code": str,
    "greenhouse_gaz_diagnostic_code": str,
    "energetic_performance_diagnostic_value": float,
    "greenhouse_gaz_diagnostic_value": float,
    "is_senior_residence": bool,
    "is_student_residence": float,
    "is_historical_monument": float,
    "condition": float,
    "is_platform": float,
    "is_building": float,
    "apartment_type": str,
    "has_caretaker": bool,
    "floor": float,
    "n_floors_building": float,
    "is_duplex": bool,
    "is_souplex": bool,
    "department_insee_code": str,
    "price_per_m2_median_city": float,
    "price_per_m2_median_postal_code": float,
    "price_per_m2_median_department": float,
    "insee_code": str,
    "region_insee_code": str,
    "price_per_m2_median_regions": float,
}

ads_in = pd.read_csv("./src/tests/pipelines/catch_price_per_m2/data/ads.csv")
kpis_city = pd.read_csv(
    "./src/tests/pipelines/catch_price_per_m2/data/kpis_per_city.csv"
)
kpis_dep = pd.read_csv(
    "./src/tests/pipelines/catch_price_per_m2/data/kpis_per_department.csv",
    dtype={"department_insee_code": str},
)
kpis_postal = pd.read_csv(
    "./src/tests/pipelines/catch_price_per_m2/data/kpis_per_postal_code.csv"
)
departments = pd.read_csv(
    "./src/tests/pipelines/catch_price_per_m2/data/departments.csv",
    dtype={"insee_code": str, "region_insee_code": str},
)
kpis_regions = pd.read_csv(
    "./src/tests/pipelines/catch_price_per_m2/data/kpis_per_region.csv",
    dtype={"region_insee_code": str},
)
ads_out_median = pd.read_csv(
    "./src/tests/pipelines/catch_price_per_m2/data/ads_out_median.csv", dtype=types
)
ads_out_mean = pd.read_csv(
    "./src/tests/pipelines/catch_price_per_m2/data/ads_out_mean.csv", dtype=types
)


@pytest.mark.parametrize(
    "ads_in, departments, kpis_city, kpis_dep, kpis_postal, kpis_regions, price_method, ads_expected",
    [
        (
            ads_in,
            departments,
            kpis_city,
            kpis_dep,
            kpis_postal,
            kpis_regions,
            "median",
            ads_out_median,
        ),
        (
            ads_in,
            departments,
            kpis_city,
            kpis_dep,
            kpis_postal,
            kpis_regions,
            "mean",
            ads_out_mean,
        ),
    ],
)
def test_merge_ads_with_kpis_price(
    ads_in,
    departments,
    kpis_city,
    kpis_dep,
    kpis_postal,
    kpis_regions,
    price_method,
    ads_expected,
):
    output = merge_ads_with_kpis_price(
        ads_in,
        departments,
        kpis_city,
        kpis_dep,
        kpis_postal,
        kpis_regions,
        price_method,
    )
    pd.testing.assert_frame_equal(output, ads_expected)
