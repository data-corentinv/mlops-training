"""
This is a boilerplate pipeline 'model_training'
"""

from kedro.pipeline import Pipeline, node
from .nodes import create_price_per_m2_feature, dropna_price_per_m2, fillna_price_per_m2


def create_pipeline(**kwargs):
    return Pipeline(
        [
            node(
                create_price_per_m2_feature,
                [
                    "sql-ads",
                    "sql-departments",
                    "kpis_per_city",
                    "kpis_per_department",
                    "kpis_per_postal_code",
                    "kpis_per_region",
                    "params:preprocessing",
                ],
                "sql-inputs-model-tmp",
            ),
            node(fillna_price_per_m2, ["sql-inputs-model-tmp"], "sql-inputs-model")
            # node(dropna_price_per_m2, ["sql-inputs-model-tmp"], "sql-inputs-model")  #
        ]
    )
