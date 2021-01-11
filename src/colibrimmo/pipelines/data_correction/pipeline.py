"""
This is a boilerplate pipeline 'data_correction'
generated using Kedro 0.16.5
"""

from kedro.pipeline import Pipeline, node
from .nodes import (
    drop_price_extreme_values,
    drop_carrez_surface_extreme_values,
)


def create_pipeline(**kwargs):
    """ pipeline for data correction
    """
    return Pipeline(
        [
            node(
                drop_price_extreme_values,
                ["sql-ads-raw", "params:ads_cleaning.price_extrem_value"],
                "sql-ads-correction-1",
            ),
            node(
                drop_carrez_surface_extreme_values,
                ["sql-ads-correction-1", "params:ads_cleaning.nb_std"],
                "sql-ads",
            ),
        ]
    )
