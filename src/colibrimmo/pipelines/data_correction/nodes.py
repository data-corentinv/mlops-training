"""
Nodes of ads data correction
generated using Kedro 0.16.5
"""
import pandas as pd
import logging.config


def drop_price_extreme_values(ads: pd.DataFrame, value: float) -> pd.DataFrame:
    """ drop price higher than {value} in euros 

    Parameters
    ----------
    ads: pd.DataFrame
    value: float
        drop price of ads > value

    Return
    ------
    ads: pd.DataFrame
         
    """
    res = ads.query(f"price < {value}")
    logging.warning(
        f"shape before droping outliers (>{value}) of price surface {ads.shape[0]} and after {res.shape[0]}"
    )
    return res


def drop_carrez_surface_extreme_values(ads: pd.DataFrame, nb_std: int) -> pd.DataFrame:
    """ keep ads with carrez_surface between mean - nb_std * std and mean + nb_std * std base on apartment type

    Parameters
    ----------
    ads: pd.DataFrame
    nb_std: int

    Return
    ------
    ads: pd.DataFrame         
    """

    res = pd.DataFrame()
    res = res.append(ads.query("apartment_type in ['platform', 'building']"))

    for i in ["studio-T1", "T3", "T2", "T4", "T5-or-higher"]:
        tmp = ads.query(f"apartment_type.str.contains('{i}')")

        value_max = tmp.carrez_surface.mean() + nb_std * tmp.carrez_surface.std()
        value_min = tmp.carrez_surface.mean() - nb_std * tmp.carrez_surface.std()

        res = res.append(
            tmp[(tmp.carrez_surface < value_max) & (tmp.carrez_surface > value_min)]
        )

    res.drop_duplicates(inplace=True)
    logging.warning(
        f"shape before droping ouliers of carrez surface {ads.shape[0]} and after {res.shape[0]}"
    )

    return res
