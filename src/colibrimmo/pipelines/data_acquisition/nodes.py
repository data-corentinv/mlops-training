import logging
import pandas as pd


def update_ads(data: pd.DataFrame, env: str):
    df_adds = data.loc[0:100]
    return df_adds
