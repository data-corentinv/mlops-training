from kedro.pipeline import Pipeline, node

from .nodes import compute_kpis


def create_pipeline(**kwargs):
    return Pipeline([node(compute_kpis, ["sql-ads",], "kpis",)])
