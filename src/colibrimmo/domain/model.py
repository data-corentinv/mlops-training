import logging
import os
import inspect
import pandas as pd
import numpy as np
from os.path import join
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.base import BaseEstimator, RegressorMixin
from sklearn.metrics import mean_absolute_error
from sklearn.pipeline import Pipeline
from sklearn.exceptions import NotFittedError
import mlflow
import mlflow.sklearn
import mlflow.tracking
from plotly import graph_objs as go
from mlflow.models.signature import infer_signature
from mlflow.utils import mlflow_tags
from mlflow.pyfunc import PythonModel

from colibrimmo.domain.preprocessing import Preprocessing
from pdpbox import pdp


class Colibrimmodel(PythonModel, BaseEstimator, RegressorMixin):
    """ Colibrimmodel

    Parameters
    ----------
        inputs_price_per_m2: pd.DataFrame
            dataframe containing city_insse_code and price_per_m2

    Attributes
    ----------
    parameters: dict 
        parameters of RandomForestRegressor or Preprocessing classes
    _reg_common_parameters: dict
        signature of RandomForestRegressor class
    _preprocessing_common_parameters: dict
        signature of Preprocessing class
    reg_parameters: dict
        RandomForest arguments contained in **kwargs
    preprocessing_parameters: dict
        Preprocessing arguments contained in **kwargs
    reg: RandonForestRegressor
    preprocessing: Preprocessing
    pipeline: Pipeline 
        sklearn Pipeline containing Preprocessing and RandomForestRegressor

    """

    def __init__(self, inputs_price_per_m2: pd.DataFrame, **kwargs) -> None:
        self.parameters = kwargs
        self._reg_common_parameters = list(
            inspect.signature(RandomForestRegressor).parameters.keys()
        )
        self._preprocessing_common_parameters = list(
            inspect.signature(Preprocessing).parameters.keys()
        )

        self.reg_parameters = {
            x: kwargs[x] for x in kwargs if x in self._reg_common_parameters
        }
        self.preprocessing_parameters = {
            x: kwargs[x] for x in kwargs if x in self._preprocessing_common_parameters
        }

        self.reg = RandomForestRegressor(**self.reg_parameters)

        self.preprocessing = Preprocessing(
            inputs_price_per_m2, **self.preprocessing_parameters
        )
        self.pipeline = Pipeline(
            steps=[("preprocessing", self.preprocessing), ("reg", self.reg)]
        )

    def get_params(self, deep=True):
        return {
            "reg_parameters": self.reg_parameters,
            "preprocessing_parameters": self.preprocessing_parameters,
        }

    def set_params(self, **parameters):
        for parameter, value in parameters.items():
            setattr(self, parameter, value)
        return self

    def fit(self, X: pd.DataFrame, y: pd.Series):
        """ fit model 
        """
        # X_transformed, y_transformed = self.preprocessing.transform(X, y)
        X_transformed = self.preprocessing.transform(X)
        self.reg.fit(X_transformed, y)
        self.features_names = list(X_transformed.columns)
        # self.signature = infer_signature(X, y)
        return self

    def predict(self, X: pd.DataFrame) -> pd.DataFrame:
        """ make prediction (sklearn pipeline containing preprocessing and RandomForestRegressor)
        """
        return self.pipeline.predict(X)

    def score(self, X: pd.DataFrame, y: pd.Series):
        """ compute score (mae: mean absolute error)
        """
        predictions = self.predict(X)
        return mean_absolute_error(y, predictions)  # y_transformed

    def pdp_plot(self, x, feature, num_grid_points=20, grid_type="percentile"):
        """ plot partial dependance plot with pdpbox python module

        Parameters
        ----------
        x: pd.DataFrame
            inputs
        feature: str
            feature to analyze
        num_grid_point: int
            pdpbox.plot_isolate method
        grid_type:  str
            pdpbox.plot_isolate method

        Return
        ------
        fig: pyplot Figure

        """
        x_transformed = self.preprocessing.transform(x)

        pdp_goals = pdp.pdp_isolate(
            model=self.reg,
            dataset=x_transformed,
            model_features=self.features_names,
            feature=feature,
            num_grid_points=num_grid_points,
            grid_type=grid_type,  # possible values: 'equal' or 'percentile'
        )
        fig, _ = pdp.pdp_plot(
            pdp_goals, feature, center=True
        )  # center arg center plots and compare each value to the first one
        return fig

    @property
    def feature_importances(self):
        """ compute feature importance
        """
        importances = self.reg.feature_importances_
        # indices = np.argsort(importances)
        if not self.features_names:
            raise NotFittedError("fit the model before to get the feature importance")

        feature_importances, feature_names = (
            list(x)
            for x in zip(*sorted(zip(importances, self.features_names), reverse=False))
        )
        return feature_names, feature_importances

    def feature_importances_figure(self):
        """ feature importance pyplot with pyplot (allow html output)
        """
        feature_names, feature_importances = self.feature_importances
        trace = go.Bar(
            x=feature_importances,
            y=feature_names,
            marker=dict(
                color=feature_importances, colorscale="Viridis", reversescale=True
            ),
            name="RandomForest Regressor Feature importance",
            orientation="h",
        )

        layout = dict(
            title="Barplot of Feature importances",
            width=900,
            height=2000,
            yaxis=dict(showgrid=False, showline=False, showticklabels=True,),
        )

        fig = go.Figure(data=[trace])
        fig["layout"].update(layout)
        return fig


if __name__ == "__main__":
    cities = catalog.datasets.sql__cities.load()
    features = catalog.datasets.params__model__features.load()
    target = catalog.datasets.params__model__target.load()
    ads = catalog.datasets.sql__ads.load()
    ads = ads.dropna(subset=[target])
    X = ads.filter(features)
    X = X.fillna(
        {
            "construction_year": 1980,
            "carrez_surface": 6,
            "n_bedrooms": 1,
            "apartment_type": "studio-T1",
            "has_balcony": False,
            "has_garden": False,
            "heating_type": "individual",
            "orientation": "Nord",
            "energetic_performance_diagnostic_code": "G",
            "is_duplex": False,
            "city_insee_code": "36030",
        }
    )
    X = X.filter(features)
    y = ads[target]
    c = Colibrimmodel(cities)
    c.fit(X, y)
    mlflow.sklearn.log_model(
        artifact_path="price_model",
        sk_model=c,
        # code_path=[join('src', 'colibrimmo', 'domain', 'model.py'),join('src', 'colibrimmo', 'domain', 'preprocessing.py'),],
        conda_env={
            "channels": ["defaults", "conda-forge"],
            "dependencies": [
                "mlflow=1.12.1",
                "numpy=1.19.3",
                "python=3.8.0",
                "scikit-learn=0.23.2",
                "cloudpickle==1.3.0",
            ],
            "name": "price-model-envs",
        },
    )
