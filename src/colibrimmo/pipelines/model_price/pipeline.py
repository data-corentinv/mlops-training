"""
This is a boilerplate pipeline 'model_price'
generated using Kedro 0.16.5
"""

from kedro.pipeline import Pipeline, node
from .nodes import (
    fillna_inputs_model,
    train,
    validate,
    temporal_split,
    split_inputs_into_train_test,
)


def create_pipeline(**kwargs):
    return Pipeline(
        [
            node(
                fillna_inputs_model,
                [
                    "sql-ads",
                    "params:model.target",
                    "params:model.categories",
                    "params:model.numericals",
                    "params:model.boolean_features",
                ],
                "pre_processed_ads",
                name="fillna_strategy_imputation",
            ),
            node(
                temporal_split,  # split_inputs_into_train_test (random split) #temporal_split
                [
                    "pre_processed_ads",
                    "params:model.col_date",
                    "params:model.split_train",
                ],
                ["ads-train", "ads-test"],
                name="split",
            ),
            node(
                validate,
                ["sql-inputs-model", "ads-train", "ads-test", "params:model"],
                None,
                name="validate",
            ),
            node(
                train,
                ["sql-inputs-model", "pre_processed_ads", "params:model"],
                None,
                name="train",
            ),
        ]
    )
