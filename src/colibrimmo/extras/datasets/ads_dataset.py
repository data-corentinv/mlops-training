from typing import List, Dict, Any
from kedro.io import AbstractDataSet
from sqlalchemy import create_engine

from colibrimmo.infra.database import session_scope, create_postgres_namespace
from colibrimmo.domain.ads import Ad


class AdsDataSet(AbstractDataSet):
    """``AdsDataSet`` loads / save ads from the postgreSQL database.

    Example:
    ::

        >>> AdsDataSet(credentials='db_admin', schema='local')
    """

    def __init__(self, credentials: str, schema: str):
        """Creates a new instance of ImageDataSet to load / save image data for given filepath.

        Args:
            filepath: The location of the image file to load / save data.
            schema: the postreSQL namespace injected bu the catalog
        """
        self.schema = schema
        Ad.__table__.schema = schema
        self.credentials = credentials
        self.conn = self.credentials["con"]
        self.database = self.credentials["database"]
        self.engine = create_engine(self.conn + f"/{self.database}", echo=True)
        create_postgres_namespace(self.engine, schema)
        Ad.metadata.create_all(self.engine)

    def _load(self) -> List[Ad]:
        """Loads ad from the database

        Returns:
            list of Ads
        """
        with session_scope(self.conn, self.database) as session:
            return session.query(Ad).all()

    def _save(self, ads: List[Ad]) -> None:
        """Saves ads in the database.
        """
        with session_scope(self.conn, self.database) as session:
            session.add_all(ads)

    def _describe(self) -> Dict[str, Any]:
        """Returns a dict that describes the attributes of the dataset.
        """
        return dict(
            schema=self.schema, database=self.database, tables=Ad.metadata.tables
        )
