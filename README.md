# Colibrimmo
## Setup
Git clone this repository. The dependencies are declared in src/reqirements.txt you can install them using
```bash
kedro install
```

The configuration is divided into folders (one per environment : local, base, prod, ...). By default the pipeline will use local coniguration but you can specify configurations by environments. The priority will be given to the configuration from your environment over the local configuration.
```
conf
└───local
└───base
└───prod
```
Create a credentials.yml in local folder
```
# credentials.yml
cloud_sql:
  username: <POSTGRESQL USERNAME>
  password: <POSTGRESQL PASSWORD>

gcp_service_account:
  token: conf/local/service_account.json

db_admin:
  con: postgresql://postgres:postgres@localhost:5432
  database: <NAME OF YOUR POSTGRESQL DATABASE>
```

Download a JSON key token from GCP service accounts (IAM) and copy it in conf/local as service_account.json. You can name it as you wish while the name is coherent with 

## Proxy to Cloud SQL instance
Download proxy at 
https://cloud.google.com/sql/docs/postgres/sql-proxy
```
$ /cloud_sql_proxy -instances=yotta-mlops:europe-west1:group-1=tcp:5432
```

> *Note:* In *Kubernetes* the proxy is running as a sidecar
docker image : gcr.io/cloudsql-docker/gce-proxy (see deployment/pod.yml)   

## Secret and configmaps creation
```
$ kubectl create secret generic secret-group-1 --from-file=service_account.json=conf/local/service_account.json

$kubectl create configmap conf-group-1 --from-file=conf/base/catalog.yml --from-file=conf/base/parameters.yml --from-file=conf/base/logging.yml --from-file=conf/base/credentials.yml
```

## Build docker image

```
kedro docker build
docker tag colibrimmo-group-1:latest eu.gcr.io/yotta-mlops/colibrimmo-group-1:latest
docker push eu.gcr.io/yotta-mlops/colibrimmo-group-1:latest
```

```
kubectl apply -f deployment/pod.yml
kubectl exec -it colibrimmo-group-1 --container pipeline -- /bin/bash
```
## How to run your Kedro pipeline

You can run your Kedro project with:

```
# local environment
kedro run
# prod environment
kedro run --env prod
```

## How to test your Kedro project

Have a look at the file `src/tests/test_run.py` for instructions on how to write your tests. You can run your tests as follows:

```
kedro test
```

To configure the coverage threshold, go to the `.coveragerc` file.

## Project dependencies

To generate or update the dependency requirements for your project:

```
kedro build-reqs
```

This will copy the contents of `src/requirements.txt` into a new file `src/requirements.in` which will be used as the source for `pip-compile`. You can see the output of the resolution by opening `src/requirements.txt`.

After this, if you'd like to update your project requirements, please update `src/requirements.in` and re-run `kedro build-reqs`.

[Further information about project dependencies](https://kedro.readthedocs.io/en/stable/04_kedro_project_setup/01_dependencies.html#project-specific-dependencies)

## How to work with Kedro and notebooks

> Note: Using `kedro jupyter` or `kedro ipython` to run your notebook provides these variables in scope: `context`, `catalog`, and `startup_error`.
>
> Jupyter, JupyterLab, and IPython are already included in the project requirements by default, so once you have run `kedro install` you will not need to take any extra steps before you use them.

### Jupyter
To use Jupyter notebooks in your Kedro project, you need to install Jupyter:

```
pip install jupyter
```

After installing Jupyter, you can start a local notebook server:

```
kedro jupyter notebook
```

### JupyterLab
To use JupyterLab, you need to install it:

```
pip install jupyterlab
```

You can also start JupyterLab:

```
kedro jupyter lab
```

### IPython
And if you want to run an IPython session:

```
kedro ipython
```

### How to convert notebook cells to nodes in a Kedro project
You can move notebook code over into a Kedro project structure using a mixture of [cell tagging](https://jupyter-notebook.readthedocs.io/en/stable/changelog.html#cell-tags) and Kedro CLI commands.

By adding the `node` tag to a cell and running the command below, the cell's source code will be copied over to a Python file within `src/<package_name>/nodes/`:

```
kedro jupyter convert <filepath_to_my_notebook>
```
> *Note:* The name of the Python file matches the name of the original notebook.

Alternatively, you may want to transform all your notebooks in one go. Run the following command to convert all notebook files found in the project root directory and under any of its sub-folders:

```
kedro jupyter convert --all
```

### How to ignore notebook output cells in `git`
To automatically strip out all output cell contents before committing to `git`, you can run `kedro activate-nbstripout`. This will add a hook in `.git/config` which will run `nbstripout` before anything is committed to `git`.

> *Note:* Your output cells will be retained locally.

## Package your Kedro project

[Further information about building project documentation and packaging your project](https://kedro.readthedocs.io/en/stable/03_tutorial/05_package_a_project.html)
