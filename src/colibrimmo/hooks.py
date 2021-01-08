"""Project hooks."""
import os
from typing import Any, Dict, Iterable, Optional

from kedro.config import ConfigLoader
from kedro.config import TemplatedConfigLoader
from kedro.framework.hooks import hook_impl
from kedro.io import DataCatalog
from kedro.pipeline import Pipeline
from kedro.versioning import Journal
from colibrimmo.pipelines import data_acquisition as da
from colibrimmo.pipelines import data_correction as dc
from colibrimmo.pipelines import kpis as kp
from colibrimmo.pipelines import model_price as mp
from colibrimmo.pipelines import catch_price_per_m2 as catch


class ProjectHooks:
    @hook_impl
    def register_pipelines(self) -> Dict[str, Pipeline]:
        """Register the project's pipeline.

        Returns:
            A mapping from a pipeline name to a ``Pipeline`` object.

        """
        data_acquisition_pipeline = da.create_pipeline()
        data_correction_pipeline = dc.create_pipeline()
        kpis_computation_pipeline = kp.create_pipeline()
        model_pipeline = mp.create_pipeline()
        catch_feature_pipeline = catch.create_pipeline()
        return {
            "da": data_acquisition_pipeline,
            "dc": data_correction_pipeline,
            "kpis": kpis_computation_pipeline,
            "price_per_m2": catch_feature_pipeline,
            "model": model_pipeline,
            "data_eng": data_acquisition_pipeline + data_correction_pipeline,
            "data_science": catch_feature_pipeline + model_pipeline,
            "__default__": data_acquisition_pipeline
            + data_correction_pipeline
            + kpis_computation_pipeline
            + catch_feature_pipeline
            + model_pipeline,
        }

    @hook_impl
    def register_config_loader(self, conf_paths: Iterable[str]) -> ConfigLoader:
        return TemplatedConfigLoader(
            conf_paths, globals_pattern="*parameters.yml", globals_dict=os.environ
        )

    @hook_impl
    def register_catalog(
        self,
        catalog: Optional[Dict[str, Dict[str, Any]]],
        credentials: Dict[str, Dict[str, Any]],
        load_versions: Dict[str, str],
        save_version: str,
        journal: Journal,
    ) -> DataCatalog:
        return DataCatalog.from_config(
            catalog, credentials, load_versions, save_version, journal
        )


project_hooks = ProjectHooks()
