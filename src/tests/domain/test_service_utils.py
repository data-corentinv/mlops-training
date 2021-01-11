import pytest
import pandas as pd

from colibrimmo.domain.service_utils import get_row, merge_many_to_one


df = pd.DataFrame(
    {"key": ["known1", "known2"], "value": ["value1", "value2"]}
).set_index("key")


@pytest.mark.parametrize(
    "df,key,col,expected_value",
    [
        (df, "known1", "key", {"value": "value1"}),
        (df, "known2", "key", {"value": "value2"}),
        (df, "unknown", "key", {"error": "unknown not founded in key"}),
    ],
)
def test_get_row(df, key, col, expected_value):
    row = get_row(df, key, col)
    assert row == expected_value


left_mismatch = pd.DataFrame({"key": ["known1", "known1", "known2", "unknown"]})
left = pd.DataFrame({"key": ["known1", "known1", "known2"]})
right = pd.DataFrame(
    {"key_r": ["known1", "known2", "known3"], "value": ["value1", "value2", "value3"]}
)
expected_dict = {
    "key": ["known1", "known1", "known2"],
    "value": ["value1", "value1", "value2"],
}
expected = pd.DataFrame(expected_dict)


def test_with_warn_mismatches():
    with pytest.warns(Warning) as record:
        merged = merge_many_to_one(left_mismatch, right, "key", "key_r")
        if not record:
            pytest.fail("Expected a warning because of mismatches")
    pd.testing.assert_frame_equal(merged, expected)


def test_with_no_warn_mismatches():
    with pytest.warns(None) as record:
        merged = merge_many_to_one(left, right, "key", "key_r")
    assert len(record) == 0
    pd.testing.assert_frame_equal(merged, expected)
