from sqlalchemy import URL, create_engine
from sqlalchemy.orm import Session

from database.orm_models import Base

class Database():

    def __init__(self) -> None:
        self._host = "localhost"
        self._port = "5432"
        self._db_name = "sim_db"

        self.db_url = URL.create(
            "postgresql+psycopg2",
            host=self._host,
            port=self._port,
            database=self._db_name,
        )

    def startup(self):
        self.engine = create_engine(self.db_url)
        Base.metadata.drop_all(self.engine)
        Base.metadata.create_all(self.engine)

    def shutdown(self):
        pass

    def write_batch_to_db(self, data):
        with Session(self.engine) as session:
            session.add_all(data)
            session.commit()
