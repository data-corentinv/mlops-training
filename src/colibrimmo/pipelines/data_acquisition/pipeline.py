from kedro.pipeline import Pipeline, node

from .nodes import update_tables


def create_pipeline(**kwargs):
    return Pipeline(
        [
            node(
                update_tables,
                "ads",
                "sql-ads"
            ),
            node(
                update_tables,
                "zones-cities",
                "sql-zones-cities"
            ),
            node(
                update_tables,
                "zones-departments",
                "sql-zones-departments"
            ),
            node(
                update_tables,
                "zones-insee",
                "sql-zones-insee"
            ),
            node(
                update_tables,
                "zones-postal-codes",
                "sql-zones-postal-codes"
            ),
            node(
                update_tables,
                "zones-regions",
                "sql-regions"
            ),
            node(
                update_tables,
                "zones-iris",
                "sql-iris"
            ),
        ]
    )
