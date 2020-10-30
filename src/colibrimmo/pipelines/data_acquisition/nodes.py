import logging
from typing import Any, Dict
from datetime import datetime

import pandas as pd
from colibrimmo.domain.appartement import Appartement
from colibrimmo.infra.database import session_scope, engine, sqlalchemy


def update_ads(data: pd.DataFrame, env: str):
    if not engine.dialect.has_schema(engine, env):
        engine.execute(sqlalchemy.schema.CreateSchema(env))
    df_adds = data.loc[0:100]
    return df_adds
    

def create_fake_appartement(iris_insee_code: int, parution_date: datetime, description: str) -> Dict[str, Any]:
    """Node for create an appartement in the code and in the PostgreSQL database.
    The paramters will be loaded and provided to your function
    automatically when the pipeline is executed and it is time to run this node.
    """
    with session_scope() as session:
        app1 = Appartement(iris_insee_code=iris_insee_code, parution_date=parution_date, description=description)
        app2 = Appartement(iris_insee_code=44590, parution_date="2020/12/10", description=description)
        app3 = Appartement(iris_insee_code=59000, parution_date="2020/12/13", description=description)
        
        status = 10
        logging.info('adding an appartement')
        session.add(app1)
        session.add(app2)
        session.add(app3)
        return {'status': status}
