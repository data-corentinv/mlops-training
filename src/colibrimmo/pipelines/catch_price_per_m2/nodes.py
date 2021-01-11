import pandas as pd
import math

import logging.config
from sklearn.model_selection import train_test_split
from .utils import merge_ads_with_kpis_price


def create_price_per_m2_feature(
    ads: pd.DataFrame,
    departments: pd.DataFrame,
    kpis_city: pd.DataFrame,
    kpis_dep: pd.DataFrame,
    kpis_postal: pd.DataFrame,
    kpis_regions: pd.DataFrame,
    preprocessing_params: dict,
) -> pd.DataFrame:
    """ This function preparing features for modeling. Here we create price per m2 feature (median or mean) from kpis computed. This function select from city_insee_code : 
        - if insee_city_code exist : price_per_m2_cities  
        - elif insee_department_code exist : price_per_m2_department  
        - else (if value doesnot exist) lines are dropped 

    Parameters
    ----------
    ads: pd.DataFrame
        sql-ads table
    kpis_city: pd.DataFrame
        kpis based on city (kpis_per_city table)
    kpis_dep: pd.DataFrame
        kpis base on departments (kpis_per_department table)
    kpis_postal: pd.DataFrame
        kpis base on postal code (kpis_per_postal_code)
    preprocessing_params: dict
        dictionnary containing parameters for preprocessing (price_method:['mean', 'median'], boolean_features, categories, numericals, target, keys)

    Return
    ------
    ads: pd.DataFrame

    """
    init_shape = ads.shape[0]
    price_method = preprocessing_params["price_method"]

    ads = merge_ads_with_kpis_price(
        ads, departments, kpis_city, kpis_dep, kpis_postal, kpis_regions, price_method
    )

    def price_nan_replacing_strategy(x):
        """ missing values strategy for price per m2 feature 
        TODO rewrite with coalesce
        """
        if math.isnan(x[f"price_per_m2_{price_method}_city"]):
            if not math.isnan(x[f"price_per_m2_{price_method}_postal_code"]):
                return x[f"price_per_m2_{price_method}_postal_code"]
            elif not math.isnan(x[f"price_per_m2_{price_method}_department"]):
                return x[f"price_per_m2_{price_method}_department"]
            else:
                return x[f"price_per_m2_{price_method}_regions"]
        else:
            return x[f"price_per_m2_{price_method}_city"]

    # missing value imputation
    ads = ads.assign(price_per_m2=ads.apply(price_nan_replacing_strategy, axis=1))

    final_shape = ads.shape[0]
    assert init_shape == final_shape

    return ads


def dropna_price_per_m2(ads: pd.DataFrame):
    """ drop rows when price per m2 is missing (not founds in KPIs)
    """
    return ads.dropna(subset=["price_per_m2"])


def fillna_price_per_m2(ads: pd.DataFrame):
    """ fillna price_per_m2 with mean price_per_m2
    """
    init_shape = ads.shape[0]

    mean_price_per_m2 = ads.price_per_m2.mean()
    ads.price_per_m2.fillna(mean_price_per_m2, inplace=True)

    final_shape = ads.shape[0]
    assert init_shape == final_shape

    return ads  # .filter
