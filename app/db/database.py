import os
import datetime

from sqlalchemy import create_engine, DateTime, Column, Integer, String
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, 'cwl.db')
engine = create_engine(f'sqlite:///{db_path}', echo=True)

Base = declarative_base()

class CWL(Base):
    __tablename__ = 'cwl'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    workflow_id = Column(String)
    creation_date = Column(DateTime, default=datetime.datetime.now)

    def to_dict(self):
        dict_repr = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        dict_repr['creation_date'] = self.creation_date.strftime('%Y-%m-%dT%H:%M:%S')
        return dict_repr

Base.metadata.create_all(bind=engine)

session = scoped_session(sessionmaker(bind=engine))