from sqlalchemy import Column, Integer, String, Date

from colibrimmo.infra.database import Base


class Ad(Base):
    __tablename__ = "ads"
    id = Column(Integer, primary_key=True)
    parution_date = Column(Date)
    iris_insee_code = Column(Integer)
    price = Column(Integer)

    def __repr__(self):
        return """<Ad(id='%s', parution_date='%s', iris_insee_code='%s') >" 
        % (self.id, self.parution_date, self.iris_insee_code)"""
