import logging
from colibrimmo.domain.ads import Ad
from typing import Any, Dict
import pandas as pd


def update_ads(data: pd.DataFrame) -> Ad:
    """ Node for create an appartement in the code and in the PostgreSQL database.
    The paramters will be loaded and provided to your function
    automatically when the pipeline is executed and it is time to run this node.
    """
    one_ad = data.iloc[0]

    ad1 = Ad(
        iris_insee_code=one_ad["iris_insee_code"],
        parution_date=one_ad["parution_date"],
        price=one_ad["price"],
    )

    another_ad = data.iloc[1]

    ad2 = Ad(
        iris_insee_code=another_ad["iris_insee_code"],
        parution_date=another_ad["parution_date"],
        price=another_ad["price"],
    )

    return [ad1, ad2]
