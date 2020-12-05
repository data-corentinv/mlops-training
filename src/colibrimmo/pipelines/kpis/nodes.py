import logging
import pandas as pd
import datetime as dt

from typing import List
from colibrimmo.domain.service_utils import merge_many_to_one


def merge_zone_ads(
    ads: pd.DataFrame,
    cities: pd.DataFrame,
    postalcodes: pd.DataFrame,
    insee: pd.DataFrame,
    departements: pd.DataFrame,
    regions: pd.DataFrame,
) -> pd.DataFrame:
    """
    """
    regions = regions.filter(["insee_code", "name"]).rename(
        columns={"insee_code": "region_insee_code_r", "name": "region_name"}
    )
    departements = departements.filter(
        ["insee_code", "name", "region_insee_code"]
    ).rename(
        columns={"insee_code": "department_insee_code_r", "name": "department_name"}
    )
    postalcodes = postalcodes.rename(columns={"postal_code": "postal_code_r"})
    cities = cities.filter(["insee_code", "name", "department_insee_code"]).rename(
        columns={"name": "city_name"}
    )
    insee = insee.filter(["city_insee_code", "postal_code"])

    departements = merge_many_to_one(
        departements, regions, "region_insee_code", "region_insee_code_r"
    )
    cities = merge_many_to_one(
        cities, departements, "department_insee_code", "department_insee_code_r"
    )
    ads = merge_many_to_one(ads, cities, "city_insee_code", "insee_code")
    ads = merge_many_to_one(ads, postalcodes, "postal_code", "postal_code_r")
    # TODO : sanitycheck : in ads table, are postal_code and city_insee_code and iris_insee_codes coherents ? check using joins
    return ads


def normalize_measure(df: pd.DataFrame, formula: str, normalized: str) -> pd.DataFrame:
    """
    """
    df = df.eval(f"{normalized} = {formula}")
    return df


def aggregate(
    df: pd.DataFrame, col_measure: str, aggs: List, granularity: str
) -> pd.DataFrame:
    """
    """
    aggregated_df = df.groupby(by=granularity).agg({col_measure: aggs})[col_measure]
    return aggregated_df


def compute_datetime(df: pd.DataFrame, col_date: str) -> pd.DataFrame:
    """
    """
    kwargs = {col_date: lambda df: dt.datetime.now(dt.timezone.utc)}
    return df.assign(**kwargs)


def format_kpis(
    df: pd.DataFrame, col_measure: str, aggs: List, user_rename_map={}, fillna={}
) -> pd.DataFrame:
    """
    """
    rename_map = {agg: f"{col_measure}_{agg}" for agg in aggs}
    rename_map.update(user_rename_map)
    df = df.fillna(fillna).rename(columns=rename_map).reset_index()
    return df
