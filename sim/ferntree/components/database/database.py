from sqlalchemy import URL, create_engine
from sqlalchemy.orm import Session
from database import orm_models

class PostgresDatabase:
    """ Class for the Postgres database. 
    Main purpose is to write data to the database.
    """
    def __init__(self):
        """ Initializes a new instance of the PostgresDatabase class.
        - Defines the database URL
        - Defines the batch size for writing to the database
        """
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
        """ Startup of the database:
        - Creates the database engine
        - Drops existing tables
        - Creates new tables defined in orm_models
        """
        self.engine = create_engine(self.db_url)
        orm_models.Base.metadata.drop_all(self.engine)
        orm_models.Base.metadata.create_all(self.engine)

    def shutdown(self):
        """ Shutdown of the database:
        - Writes any remaining data in the buffer to the database
        """
        if self.data_buffer:
            self.write_batch(self.data_buffer)
            self.data_buffer = []


    def write_data_to_db(self, data):
        """ Writes data in batches to the database.
        - Appends data to the buffer
        - Writes the buffer to the database if it is full
        """
        self.data_buffer.append(data)

        if len(self.data_buffer) == self.batch_size:
            self.write_batch(self.data_buffer)
            self.data_buffer = []

    def write_batch(self, batch):
        """ Writes a batch of data to the database.
        - Opens a new session
        - Writes the batch to the database
        - Commits the session
        """
        with Session(self.engine) as session:
            session.bulk_save_objects(batch)
            session.commit()
