from kedro.pipeline import Pipeline, node

from .nodes import normalize_measure, format_kpis, aggregate, merge_zone_ads


def create_pipeline(**kwargs):
    return Pipeline(
        [
            node(
                merge_zone_ads,
                ['sql-ads', 'sql-cities', 'sql-postalcodes', 'sql-insee', 'sql-departments', 'sql-regions'],
                'merged_ads'
            ),
            node(
                normalize_measure,
                ['merged_ads', 'params:kpis.formula', 'params:kpis.col_normalized'],
                'prices_per_m2'
            ),
            node(
                aggregate,
                ['prices_per_m2', 'params:kpis.col_normalized', 'params:kpis.aggs', 'params:region'],
                'price_per_region'
            ),
            node(
                format_kpis,
                ['price_per_region', 'params:kpis.col_normalized', 'params:kpis.aggs', 'params:kpis.user_rename_map', 'params:kpis.fillna'],
                'kpis_per_region'
            ),
            node(
                aggregate,
                ['prices_per_m2', 'params:kpis.col_normalized', 'params:kpis.aggs', 'params:department'],
                'price_per_department'
            ),
            node(
                format_kpis,
                ['price_per_department', 'params:kpis.col_normalized', 'params:kpis.aggs', 'params:kpis.user_rename_map', 'params:kpis.fillna'],
                'kpis_per_department'
            ),
            node(
                aggregate,
                ['prices_per_m2', 'params:kpis.col_normalized', 'params:kpis.aggs', 'params:postal_code'],
                'price_per_postal_code'
            ),
            node(
                format_kpis,
                ['price_per_postal_code', 'params:kpis.col_normalized', 'params:kpis.aggs', 'params:kpis.user_rename_map', 'params:kpis.fillna'],
                'kpis_per_postal_code'
            ),
            node(
                aggregate,
                ['prices_per_m2', 'params:kpis.col_normalized', 'params:kpis.aggs', 'params:city'],
                'price_per_city'
            ),
            node(
                format_kpis,
                ['price_per_city', 'params:kpis.col_normalized', 'params:kpis.aggs', 'params:kpis.user_rename_map', 'params:kpis.fillna'],
                'kpis_per_city'
            ),
            node(
                aggregate,
                ['prices_per_m2', 'params:kpis.col_normalized', 'params:kpis.aggs', 'params:iris'],
                'price_per_iris'
            ),
            node(
                format_kpis,
                ['price_per_iris', 'params:kpis.col_normalized', 'params:kpis.aggs', 'params:kpis.user_rename_map', 'params:kpis.fillna'],
                'kpis_per_iris'
            ),
        ]
    )
