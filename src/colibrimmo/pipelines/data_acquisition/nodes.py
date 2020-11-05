import logging
from typing import Any, Dict
from datetime import datetime

import pandas as pd


def update_ads(data: pd.DataFrame) -> pd.DataFrame:
    df_adds = data.loc[0:100]
    return df_adds
