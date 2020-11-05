from kedro.pipeline import Pipeline, node

from .nodes import update_ads


def create_pipeline(**kwargs):
    return Pipeline(
        [
            node(
                update_ads,
                ["ads"],
                "sql-ads"
            ),
        ]
    )
