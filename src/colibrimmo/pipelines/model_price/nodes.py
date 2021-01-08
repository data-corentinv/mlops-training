"""
This is a boilerplate pipeline 'model_price'
generated using Kedro 0.16.5
"""

import logging
import mlflow
import pandas as pd
from os.path import join
from typing import List, Dict, Any
from mlflow.utils import mlflow_tags
from sklearn.model_selection import TimeSeriesSplit
from colibrimmo.domain.model import Colibrimmodel
from colibrimmo.domain.mlflow_utils import (
    get_run,
    mlflow_log_figure,
    mlflow_log_plotly,
    mlflow_log_pandas,
)
from sklearn.model_selection import train_test_split


def temporal_split(ads: pd.DataFrame, col_date: str, split_train: float):
    """ temporal split
    """
    with mlflow.start_run(run_name="split") as run:
        mlflow.set_tag("entry_point", "split")
        ads = ads.sort_values(by=[col_date])
        N = len(ads)
        split = int(split_train * N)
        ads_train = ads.iloc[:split]
        ads_test = ads.iloc[split:]
        mlflow_log_pandas(ads_train, "training_set", "ads_train.csv")
        mlflow_log_pandas(ads_test, "testing_set", "ads_test.csv")
        mlflow.log_param("split_train", str(split_train))
    return ads_train, ads_test


def fillna_inputs_model(
    ads: pd.DataFrame,
    target: str,
    categories: list,
    numericals: list,
    boolean_features: list,
):
    """ strategy imputation of missing value of features 
    """
    strategy_imputation_na = {
        "has_terrace": False,
        "has_swimming_pool": False,
        "has_chimney": False,
        "has_elevator": False,
        "carrez_surface": 66,  # mean value of carrez_surface
        "apartment_type": "T3",  # most ads are T3
        "energetic_performance_diagnostic_code": "NAN",
        "is_duplex": False,
    }

    ads = ads.dropna(subset=[target])
    ads = ads.fillna(strategy_imputation_na)

    features_missing = list(
        set(categories + numericals + boolean_features)
        - set(strategy_imputation_na.keys())
    )
    if len(features_missing) > 0:
        logging.warning(
            f"no imputation strategy develop for this features : {features_missing}"
        )

    return ads


def validate(
    inputs_price_per_m2: pd.DataFrame,
    ads_train: pd.DataFrame,
    ads_test: pd.DataFrame,
    model_parameters: Dict[str, Any],
) -> None:
    """ training model on train set and evaluate perfornace on test set

    Parameters
    ----------
        inputs_price_per_m2: pd.DataFrame
            dataframe containing matching between price_per_m2 and city_insee_code
        ads-train: pd.DataFrame
            dataframe of ads (train set)
        ads-test: pd.DataFrame
            dataframe of ads (test set)
        model_parameters: Dict[str, Any]
            dictionnary of Preprocessing and Colibrimmodel's parameters

    """
    features = (
        model_parameters["boolean_features"]
        + model_parameters["categories"]
        + model_parameters["numericals"]
        + ["city_insee_code"]
    )
    target = model_parameters["target"]

    mlflow_client = mlflow.tracking.MlflowClient()

    with mlflow.start_run(run_name="validate") as run:
        logging.info(f"Start mlflow run - validate - id = {run.info.run_id}")
        git_commit = run.data.tags.get(mlflow_tags.MLFLOW_GIT_COMMIT)
        mlflow.set_tag("entry_point", "validate")

        x_train = ads_train.filter(features)
        y_train = ads_train[target]
        model = Colibrimmodel(inputs_price_per_m2, **model_parameters)

        mlflow.log_params(model_parameters)

        model.fit(x_train, y_train)

        logging.info("evaluate performance (mae) of model on train set")
        score = model.score(x_train, y_train)
        logging.info(f"mae value train set : {round(score,2)}")
        mlflow.log_metric("mae-train-set", score)

        logging.info("plot feature importance and save graph in mlflow")
        fig = model.feature_importances_figure()
        mlflow_log_plotly(fig, "plots", "feature_importance.html")
        mlflow.sklearn.log_model(artifact_path="price_model", sk_model=model)

        mlflow.shap.log_explanation(
            model.reg.predict, model.preprocessing.transform(x_train).head(20)
        )
        logging.info(f"list of features used {model.features_names}")

        logging.info("plot partial dependance plot of all features")
        for var in model.features_names:
            fig = model.pdp_plot(x_train, var)  # exemple
            mlflow_log_figure(fig, "plots", f"pdp_{var}.png")

        y_test = ads_test[target]
        x_test = ads_test.filter(features)
        y_pred = model.predict(x_test)

        logging.info("evaluate performance (mae) of model on test set")
        score = model.score(x_test, y_test)
        logging.info(f"mae value test set : {round(score,2)}")
        mlflow.log_metric("mae-test-set", score)

        logging.info("save prediction into mlflow")
        mlflow_log_pandas(pd.DataFrame(y_pred), "predictions", "y_pred.csv")
        mlflow_log_pandas(
            pd.DataFrame({"features": model.features_names}), "features", "features.csv"
        )


def train(
    inputs_price_per_m2: pd.DataFrame,
    ads: pd.DataFrame,
    model_parameters: Dict[str, Any],
) -> None:
    """ train model on all dataset

    Parameters
    ----------
        inputs_price_per_m2: pd.DataFrame
            dataframe containing matching between price_per_m2 and city_insee_code
        ads: pd.DataFrame
            dataframe of ads
        model_parameters: Dict[str, Any]
            dictionnary of Preprocessing and Colibrimmodel's parameters
    """

    features = (
        model_parameters["boolean_features"]
        + model_parameters["categories"]
        + model_parameters["numericals"]
        + ["city_insee_code"]
    )
    target = model_parameters["target"]

    mlflow_client = mlflow.tracking.MlflowClient()

    with mlflow.start_run(run_name="train") as run:
        logging.info(f"Start mlflow run - train - id = {run.info.run_id}")
        git_commit = run.data.tags.get(mlflow_tags.MLFLOW_GIT_COMMIT)
        mlflow.set_tag("entry_point", "train")

        x = ads.filter(features)
        y = ads[target]
        mlflow.log_params(model_parameters)

        logging.info("define Colibrimmodel")
        model = Colibrimmodel(inputs_price_per_m2, **model_parameters)
        model.fit(x, y)

        logging.info("evaluate performance (mae) of model")
        score = model.score(x, y)
        logging.info(f"mae value all set : {round(score,2)}")
        mlflow.log_metric("mae", score)

        logging.info("plot feature importance and save graph in mlflow")
        fig = model.feature_importances_figure()
        mlflow_log_plotly(fig, "plots", "feature_importance.html")
        mlflow.sklearn.log_model(artifact_path="price_model", sk_model=model)

        mlflow.shap.log_explanation(
            model.reg.predict, model.preprocessing.transform(x).head(10)
        )

        logging.info("plot partial dependance plot of all features")
        for var in model.features_names:
            fig = model.pdp_plot(x, var)  # exemple
            mlflow_log_figure(fig, "plots", f"pdp_{var}.png")

        logging.info("make prediction on all dataset")
        y_pred = model.predict(x)

        logging.info("save prediction into mlflow")
        mlflow_log_pandas(pd.DataFrame(y_pred), "predictions", "y_pred.csv")
        mlflow_log_pandas(
            pd.DataFrame({"features": model.features_names}), "features", "features.csv"
        )


def split_inputs_into_train_test(inputs: pd.DataFrame, train_size: float):
    """ split inputs into train test sets containing target called price (based on train_test_split sklearn function)
    """
    return train_test_split(inputs, train_size=train_size)
