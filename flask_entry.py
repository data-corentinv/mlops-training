"""Application entry point."""
from pathlib import Path
from flask import Flask, jsonify

from kedro.framework.context import load_context
from src.colibrimmo.domain.service_utils import get_row

app = Flask(__name__)


@app.before_first_request
def load_model_to_app():
    app.context = load_context('./')
    # app.predictor = load_model('./static/model/model.h5')
    app.kpis_per_region = app.context.catalog.load('kpis_per_region').set_index('region_insee_code')
    app.kpis_per_department = app.context.catalog.load('kpis_per_department').set_index('department_insee_code')
    app.kpis_per_postal_code = app.context.catalog.load('kpis_per_postal_code').set_index('postal_code')
    app.kpis_per_cities = app.context.catalog.load('kpis_per_city').set_index('city_insee_code')
    app.kpis_per_iris = app.context.catalog.load('kpis_per_iris').set_index('iris_insee_code')
    

# @app.route("/apartments/price")
# def index():
#     return render_template('index.html', pred=0)

@app.route("/")
def hello_world():
    return 'hello world'


@app.route("/regions/<region_insee_code>/price")
def kpis_regions(region_insee_code):
    kpi = get_row(app.kpis_per_region, region_insee_code, 'region_insee_code')
    return kpi

@app.route("/departments/<department_insee_code>/price")
def kpis_departments(department_insee_code):
    kpi = get_row(app.kpis_per_department, department_insee_code, 'department_insee_code')
    return kpi

@app.route("/postal_codes/<postal_code>/price")
def kpis_postal_codes(postal_code):
    kpi = get_row(app.kpis_per_postal_code, postal_code, 'postal_code')
    return kpi

@app.route("/cities/<city_insee_code>/price")
def kpis_cities(city_insee_code):
    kpi = get_row(app.kpis_per_cities, city_insee_code, 'city_insee_code')
    return kpi

@app.route("/iris/<iris_insee_code>/price")
def kpis_iris(iris_insee_code):
    kpi = get_row(app.kpis_per_iris, iris_insee_code, 'iris_insee_code')
    return kpi

@app.route("/apartments/price/prediction")
def predict():
    mean = app.kpis_per_iris['price_per_m2_mean'].mean()
    return {
        'price_per_m2_prediction': mean
    }   #render_template('index.html', pred=mean)

@app.route("/apartments/price/prediction/model/performances")
def link_mlflow_ui():
    return {
        'url': 'https://mlflow/dashboard/run....'
        }


if __name__ == "__main__":
    # run_rest_api()
    app.run(host='0.0.0.0')
