import pandas as pd


def merge_ads_with_kpis_price(
    ads: pd.DataFrame,
    departments: pd.DataFrame,
    kpis_city: pd.DataFrame,
    kpis_dep: pd.DataFrame,
    kpis_postal: pd.DataFrame,
    kpis_regions: pd.DataFrame,
    price_method: str,
) -> pd.DataFrame:
    """ merge ads with kpis computed (except iris) and select price_per_m2 feature. At the moment iris kpis is not computed but could be an improvment.

    Parameters
    ----------
    ads: pd.DataFrame
    departments: pd.DataFrame
    kpis_city: pd.DataFrame
    kpis_dep: pd.DataFrame
    kpis_postal: pd.DataFrame
    kpis:regions: pd.DataFrame
    price_method: str
        price feature to keep (median or mean)

    Return
    ------
    ads: pd.DataFrame

    """

    # define department_insee_code
    ads = ads.assign(
        department_insee_code=ads.postal_code.astype(str).map(lambda x: x[:2])
    )

    # check price_per_m2 city granulometry
    ads = pd.merge(
        ads,
        kpis_city.filter(items=["city_insee_code", f"price_per_m2_{price_method}"]),
        how="left",
        on="city_insee_code",
    )
    ads.rename(
        columns={f"price_per_m2_{price_method}": f"price_per_m2_{price_method}_city"},
        inplace=True,
    )

    # check price_per_m2 postal code granulometry
    ads = pd.merge(
        ads,
        kpis_postal.filter(items=["postal_code", f"price_per_m2_{price_method}"]),
        how="left",
        on="postal_code",
    )
    ads.rename(
        columns={
            f"price_per_m2_{price_method}": f"price_per_m2_{price_method}_postal_code"
        },
        inplace=True,
    )

    # check price_per_m2 department granulometry
    ads = pd.merge(
        ads,
        kpis_dep.filter(
            items=["department_insee_code", f"price_per_m2_{price_method}"]
        ),
        how="left",
        on="department_insee_code",
    )
    ads.rename(
        columns={
            f"price_per_m2_{price_method}": f"price_per_m2_{price_method}_department"
        },
        inplace=True,
    )

    # check price_per_m2 regions granulometry
    ads = pd.merge(
        ads,
        departments.filter(items=["insee_code", "region_insee_code"]),
        how="left",
        left_on="department_insee_code",
        right_on="insee_code",
    )
    ads = pd.merge(
        ads,
        kpis_regions.filter(
            items=["region_insee_code", f"price_per_m2_{price_method}"]
        ),
        how="left",
        on="region_insee_code",
    )
    ads.rename(
        columns={
            f"price_per_m2_{price_method}": f"price_per_m2_{price_method}_regions"
        },
        inplace=True,
    )

    return ads
