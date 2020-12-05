import logging
import os
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_val_score
import mlflow
import mlflow.sklearn
import mlflow.tracking
from mlflow.utils import mlflow_tags


def split(df: pd.DataFrame):
    # TODO parameters feature list and target in parameters.yml
    df = df.dropna(subset=['price'])
    X = df.filter(["has_terrace", "has_box", 'has_balcony', 'has_garden', 'has_parking', 'carrez_surface']).fillna(False)
    Y = df.filter(["price"])
    X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2, random_state=42)
    return X_train, X_test, y_train, y_test


def validate(X_train: pd.DataFrame, Y_train: pd.DataFrame, n_estimators: int) -> None:
    mlflow_client = mlflow.tracking.MlflowClient()
    with mlflow.start_run(run_name='validate') as run:
        logging.info(f"Start mlflow run - validate - id = {run.info.run_id}")
        mlflow.set_tag('entry_point', 'validate')
        mlflow.log_params(
            {
                'n_estimators': n_estimators,
            }
        )
        git_commit = run.data.tags.get(mlflow_tags.MLFLOW_GIT_COMMIT)
        model = RandomForestRegressor(n_estimators=n_estimators, random_state=42)

        r2 = cross_val_score(model, X_train, Y_train, cv=5, scoring='r2')

        # mlflow_log_plotly(fig, 'plots', 'validation.html')
        mlflow.log_metric('R2_MIN', r2.min(), step=0)
        mlflow.log_metric('R2_MAX', r2.max(), step=0)
        mlflow.log_metric('R2_AVG', r2.mean(), step=0)
        mlflow.log_metric('R2_STD', r2.std(), step=0)
        logging.info(f'mlflow.log_metric:\n{r2}')


def train(X_train: pd.DataFrame, Y_train: pd.DataFrame, n_estimators: int) -> None:
    mlflow_client = mlflow.tracking.MlflowClient()
    with mlflow.start_run(run_name='train') as run:
        logging.info(f"Start mlflow run - train - id = {run.info.run_id}")
        mlflow.set_tag('entry_point', 'train')
        mlflow.log_params(
            {
                'n_estimators': n_estimators,
            }
        )
        git_commit = run.data.tags.get(mlflow_tags.MLFLOW_GIT_COMMIT)
        model = RandomForestRegressor(n_estimators=n_estimators, random_state=42)
        model.fit(X_train, Y_train)
        mlflow.sklearn.log_model(
            sk_model=model,
            artifact_path='simple_model',
        )
        logging.info(f'mlflow.sklearn.log_model:\n{model}')

if __name__ == '__main__':  # pragma: no cover
    df = catalog.datasets.sql__ads.load()
    X_train, X_test, y_train, y_test = split(df)
    validate(X_train, y_train, 40)
    train(X_train, y_train, 45)
