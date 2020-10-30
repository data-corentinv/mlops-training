from kedro.pipeline import Pipeline, node

from .nodes import create_fake_appartement, update_ads


def create_pipeline(**kwargs):
    return Pipeline(
        [
            node(
                update_ads,
                ["ads", "params:env"],
                "sql-ads"
            ),
            # node(
            #     create_fake_appartement,
            #     ["params:iris_code", "params:parution_date", "params:description"],
            #     "status",
            # )
        ]
    )
