"""Application entry point."""
import mlflow
import pandas as pd
import json
from pathlib import Path
from flask import Flask, jsonify, render_template, request
from google.cloud import storage


from kedro.framework.context import load_context
from src.colibrimmo.domain.service_utils import get_row


app = Flask(__name__)
CLOUD_STORAGE_BUCKET = 'yotta-mlops-group-1-artifacts'

@app.before_first_request
def load_model_to_app():
    app.context = load_context('./')
    app.kpis_per_region = app.context.catalog.load('kpis_per_region').set_index('region_insee_code')
    app.kpis_per_department = app.context.catalog.load('kpis_per_department').set_index('department_insee_code')
    app.kpis_per_postal_code = app.context.catalog.load('kpis_per_postal_code').set_index('postal_code')
    app.kpis_per_cities = app.context.catalog.load('kpis_per_city').set_index('city_insee_code')
    app.kpis_per_iris = app.context.catalog.load('kpis_per_iris').set_index('iris_insee_code')
    model_name = "simple model"
    model_version = 'staging'
    app.model = mlflow.sklearn.load_model(
        model_uri=f"models:/{model_name}/{model_version}"
    )

# @app.route("/apartments/price")
# def index():
#     return render_template('index.html', pred=0)

# @app.route("/")
# def hello_world():
#     return 'hello world'

# @app.route("/data_doc")
# def data_doc():
#     return render_template("data_docs/local_site/index.html")

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

@app.route("/apartments/price/prediction", methods=['POST'])
def predict():
    jsonfile = request.get_json()
    data = pd.read_json(json.dumps(jsonfile),orient='index')
    data = data.replace({'false': False, 'true': True}).T
    data = data.astype({'construction_year': 'float64', 'carrez_surface': 'float64', 
    'n_bedrooms': 'float64', 'has_balcony': 'bool', 'has_garden': 'bool', 'is_duplex': 'bool'})
    pred = app.model.predict(data)
    return {
        'price_prediction': pred[0]
    }   #render_template('index.html', pred=mean)

@app.route("/apartments/price/prediction/model/performances")
def link_mlflow_ui():
    return {
        'url': 'https://mlflow/dashboard/run....'
        }

@app.route('/', defaults={'path': 'index.html'})
@app.route('/<path:path>')
def index(path):
    gcs = storage.Client()
    bucket = gcs.get_bucket(CLOUD_STORAGE_BUCKET)
    try:
        blob = bucket.get_blob(path)
        content = blob.download_as_string()
        if blob.content_encoding:
            resource = content.decode(blob.content_encoding)
        else:
            resource = content
    except Exception as e:
        logging.exception("couldn't get blob")
        resource = "<p></p>"
    return resource
@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500



if __name__ == "__main__":
    # run_rest_api()
    app.run(host='0.0.0.0')
