from sqlalchemy import URL, create_engine
from sqlalchemy.orm import Session

from database import orm_models

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

        self.batch_size = 1000
        self.data_buffer = []

    def startup(self):
        self.engine = create_engine(self.db_url)
        orm_models.Base.metadata.drop_all(self.engine)
        orm_models.Base.metadata.create_all(self.engine)

    def shutdown(self):
        if self.data_buffer:
            self.write_batch(self.data_buffer)
            self.data_buffer = []


    def write_data_to_db(self, data):
        self.data_buffer.append(data)

        if len(self.data_buffer) == self.batch_size:
            self.write_batch(self.data_buffer)
            self.data_buffer = []

    def write_batch(self, batch):
        with Session(self.engine) as session:
            session.add_all(batch)
            session.commit()
