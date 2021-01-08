import warnings
import pandas as pd


def get_row(df: pd.DataFrame, key: str, col: str):
    """
    """
    try:
        return df.loc[key].to_dict()
    except KeyError:
        return {"error": f"{key} not founded in {col}"}


def merge_many_to_one(
    left: pd.DataFrame, right: pd.DataFrame, left_on: str, right_on: str
):
    """
    """
    merged = left.merge(
        right=right, left_on=left_on, right_on=right_on, validate="many_to_one"
    ).drop(columns=[right_on])

    len_right = len(right)
    len_left = len(left)
    len_merged = len(merged)
    len_mismatches = len_left - len_merged

    if len_left != len_merged:
        warnings.warn(
            UserWarning(
                f"some mismatches between the {len_left} left and the {len_right} right. Founded {len_mismatches} mismatches and {len_merged} matches"
            )
        )
    return merged
