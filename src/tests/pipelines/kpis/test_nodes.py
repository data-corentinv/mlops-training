import pytest
import pandas as pd
import numpy as np
from colibrimmo.pipelines.kpis.nodes import normalize_measure, aggregate, format_kpis

input_dict = {
    'group': [1, 1, 2, 1],
    'measure': [9*2, 9*3, 19*4, 12*5],
    'norm_col': [2, 3, 4, 5]
}
input_df = pd.DataFrame(input_dict)

normalized_dict = {'normalized': [9.0, 9.0, 19.0, 12.0]}
normalized_dict = {**input_dict, **normalized_dict}
expected_normalized_df = pd.DataFrame(normalized_dict)

fake_normalized_dict = {'fake_normalized': [20, 30, 80, 65]}
fake_normalized_dict = {**input_dict, **fake_normalized_dict}
fake_expected_normalized_df = pd.DataFrame(fake_normalized_dict)

median_std_dict = {
    'group': [1, 2],
    'median': [9.0, 19.0],
    'std': [1.732051, np.nan]
    }
median_std_df = pd.DataFrame(median_std_dict).set_index('group')

count_mean_dict = {
    'group': [1, 2],
    'count': [3, 1],
    'mean': [10.0, 19.0]
    }
count_mean_df = pd.DataFrame(count_mean_dict).set_index('group')

@pytest.mark.parametrize(
    "df,formula,normalized,expected_df",
    [
        (input_df, 'measure / norm_col', 'normalized', expected_normalized_df),
        (input_df, 'measure + norm_col', 'fake_normalized', fake_expected_normalized_df),
    ])
def test_normalize_measure(df, formula, normalized, expected_df):
    normalized_output = normalize_measure(df, formula, normalized)
    pd.testing.assert_frame_equal(normalized_output, expected_df)


@pytest.mark.parametrize(
    "df,normalized,aggs,granularity,expected_df",
    [
        (expected_normalized_df, 'normalized', ['median', 'std'], 'group', median_std_df),
        (expected_normalized_df, 'normalized', ['count', 'mean'], 'group', count_mean_df),
    ])
def test_aggregate_measure(df, normalized, aggs, granularity, expected_df):
    aggregated_output = aggregate(df, normalized, aggs, granularity)
    pd.testing.assert_frame_equal(aggregated_output, expected_df)

formatted_median_std_dict = {
    'group': [1, 2],
    'normalized_median': [9.0, 19.0],
    'normalized_std': [1.732051, 0.0]
    }
formatted_median_std_df = pd.DataFrame(formatted_median_std_dict)

formatted_count_mean_dict = {
    'group': [1, 2],
    'user_colname': [3, 1],
    'normalized_mean': [10.0, 19.0]
    }
formatted_count_mean_df = pd.DataFrame(formatted_count_mean_dict)

@pytest.mark.parametrize(
    "df,col_measure,aggs,user_rename_map,fillna,expected_df",
    [
        (median_std_df, 'normalized', ['median', 'std'], {}, {'std': 0}, formatted_median_std_df),
        (count_mean_df, 'normalized', ['count', 'mean'], {'count': 'user_colname'}, {}, formatted_count_mean_df)
    ]
)
def test_format_kpis(df, col_measure, aggs, user_rename_map, fillna, expected_df):
    formatted_output = format_kpis(df, col_measure, aggs, user_rename_map, fillna)
    pd.testing.assert_frame_equal(formatted_output, expected_df)
