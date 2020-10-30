import pandas as pd


def compute_kpis(ads: pd.DataFrame) -> pd.DataFrame:
    ads = ads.reset_index()
    stats_by_iris = ads\
        .pivot_table(index="iris_insee_code", values='price', aggfunc=['count', 'mean', 'median'])
    return stats_by_iris
    