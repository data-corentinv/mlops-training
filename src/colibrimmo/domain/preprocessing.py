import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
import logging.config


class Preprocessing(BaseEstimator, TransformerMixin):
    """ Preprocessing

    Parameters
    ----------
        df_inputs_price_per_m2: pd.DataFrame
            dataframe containing city_insse_code and price_per_m2
        categories: list(str)
            list of categorical features
        numericals: list(str)
            list of numerical features
        boolean_features: list(str)
            list of boolean features
        target: str
            name of target to predict

    Attributes
    ----------
        price_per_m2: dict 
            matching between city_insee_code and price_per_m2 computed in pipeline catch_price_per_m2
        apartment_type_encoding: dict
            dictionnary to encode apartment tyoe categrical feature
        orientation_encoding: dict
            dictionnary to encode orientation categorical feature (warning: feature not used in modeling)
        energetic_performance_diagnostic_code_encoding
            dictionnary to encode diagnostic code categorial feature
        categories: list(str)
            list of categorical features
        numericals: list(str)
            list of numerical features
        boolean_features: list(str)
            list of boolean features
        target: str
            name of target to predict
    """

    def __init__(
        self,
        df_inputs_price_per_m2,
        categories=None,
        numericals=None,
        boolean_features=None,
        target=None,
    ):
        self.price_per_m2 = (
            df_inputs_price_per_m2.set_index("city_insee_code")
            .filter(["price_per_m2"])
            .to_dict()["price_per_m2"]
        )
        self.apartment_type_encoding = {
            "studio-T1": 0,
            "T2": 1,
            "T3": 2,
            "T4": 3,
            "T5-or-higher": 4,
            "building": 5,
            "platform": 6,
        }
        self.orientation_encoding = {
            "Nord": 0,
            " Nord-Est": 1,
            " Nord-Ouest": 2,
            " Ouest": 3,
            " Est": 4,
            " Nord": 5,
            "Sud": 6,
        }
        self.energetic_performance_diagnostic_code_encoding = {
            "A": 6,
            "B": 5,
            "C": 4,
            "D": 3,
            "E": 2,
            "F": 1,
            "G": 0,
            "NAN": -1,
        }

        self.categories = categories
        self.numericals = numericals
        self.boolean_features = boolean_features
        self.target = target

    def fit(self, X=None, y=None):
        return self

    def transform(self, X, y=None):
        """ transform X by
            - encoding categorial features
            - create price_per_m2 feature
            - cast boolean features
        """

        city_insee_code_unknown = set(X.city_insee_code.unique()) - set(
            self.price_per_m2.keys()
        )

        X = X.assign(
            **{
                "price_per_m2": lambda df: df["city_insee_code"].map(
                    self.price_per_m2,
                ),
                "apartment_type": lambda df: df["apartment_type"].map(
                    self.apartment_type_encoding
                ),
                "energetic_performance_diagnostic_code": lambda df: df[
                    "energetic_performance_diagnostic_code"
                ].map(self.energetic_performance_diagnostic_code_encoding),
            }
        )

        X = pd.concat(
            [
                X.filter(items=self.boolean_features + self.categories).astype(int),
                # pd.get_dummies(X.filter(items=self.categories)),
                X.filter(items=self.numericals),
            ],
            axis=1,
        )

        # > log is city_insee_code_unknown
        if len(city_insee_code_unknown) > 0:
            logging.info(
                f"{len(city_insee_code_unknown)} city_insee_code donot have price_per_m2 value: {city_insee_code_unknown}"
            )
            logging.warning(
                f"Some city_insee_code in inputs are unknown (transform method in preprocessing)"
            )
            logging.info("fillna of price_per_m2 with mean price_per_m2")
            X = X.assign(price_per_m2=X.price_per_m2.fillna(X.price_per_m2.mean()))

        return X

    def predict(self, X=None, y=None):
        return self
