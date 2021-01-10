"""Application entry point."""
import logging
import mlflow
import pandas as pd
import json
from pathlib import Path
from os.path import join
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
    model_version = app.context.params['model']['mlflow_environment']
    model_name = app.context.params['model']['mlflow_model_name']
    app.model = mlflow.sklearn.load_model(
        model_uri=f"models:/{model_name}/{model_version}"
    )

# @app.route("/apartments/price")
# def index():
#     return render_template('index.html', pred=0)

@app.route("/")
def hello_world():
    return 'hello world'

# @app.route("/data_doc")
# def data_doc():
#     return render_template("data_docs/local_site/index.html")

@app.route("/regions/<region_insee_code>/price")
def kpis_regions(region_insee_code):
    kpi = get_row(app.kpis_per_region, region_insee_code, 'region_insee_code')
    return jsonify(kpi)

@app.route("/departments/<department_insee_code>/price")
def kpis_departments(department_insee_code):
    kpi = get_row(app.kpis_per_department, department_insee_code, 'department_insee_code')
    return jsonify(kpi)

@app.route("/postal_codes/<postal_code>/price")
def kpis_postal_codes(postal_code):
    kpi = get_row(app.kpis_per_postal_code, postal_code, 'postal_code')
    return jsonify(kpi)

@app.route("/cities/<city_insee_code>/price")
def kpis_cities(city_insee_code):
    kpi = get_row(app.kpis_per_cities, city_insee_code, 'city_insee_code')
    return jsonify(kpi)

@app.route("/iris/<iris_insee_code>/price")
def kpis_iris(iris_insee_code):
    kpi = get_row(app.kpis_per_iris, iris_insee_code, 'iris_insee_code')
    return jsonify(kpi)

@app.route("/apartments/price/prediction", methods=['POST'])
def predict():
    jsonfile = request.get_json()
    data = pd.read_json(json.dumps(jsonfile),orient='index')
    data = data.replace({'false': False, 'true': True}).T
    data = data.astype({'city_insee_code': 'str', 'carrez_surface': 'float64', 
    "has_terrace": "bool", "has_swimming_pool": "bool", "has_chimney": "bool", 
    "has_elevator": "bool", "is_duplex": "bool", "apartment_type": "str",
    "energetic_performance_diagnostic_code": "str","city_insee_code": "str"})
    pred = app.model.predict(data)
    return {
        'price_prediction': pred[0]
    }   #render_template('index.html', pred=mean)

@app.route("/apartments/price/prediction/model/performances")
def link_mlflow_ui():
    return {
        'url': 'https://mlflow/dashboard/run....'
        }

@app.route('/datadoc', defaults={'path': 'index.html'}, endpoint="")
@app.route('/expectations/<path:path>', endpoint='expectations')
@app.route('/validations/<path:path>', endpoint='validations')
# @app.route('/static/<path:path>', endpoint='static')
def index(path):
    gcs = storage.Client()
    bucket = gcs.get_bucket(CLOUD_STORAGE_BUCKET)
    try:
        # import ipdb; ipdb.set_trace()
        folder = request.endpoint
        # path = path.lstrip('/')
        blob = bucket.get_blob(join(folder, path))
        content = blob.download_as_string()
        if blob.content_encoding:
            resource = content.decode(blob.content_encoding)
        else:
            resource = content
    except Exception as e:
        # logging.exception("couldn't get blob")
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
