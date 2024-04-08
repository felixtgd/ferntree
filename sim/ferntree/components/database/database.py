from sqlalchemy import URL, create_engine, text
from sqlalchemy.orm import Session
from database import orm_models

import pandas as pd


class PostgresDatabase:
    """Class for the Postgres database.
    Main purpose is to write data to the database.
    """

    def __init__(self):
        """Initializes a new instance of the PostgresDatabase class.
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
        """Startup of the database:
        - Creates the database engine
        - Drops existing tables
        - Creates new tables defined in orm_models
        """
        self.engine = create_engine(self.db_url)
        orm_models.Base.metadata.drop_all(self.engine)
        orm_models.Base.metadata.create_all(self.engine)

    def shutdown(self):
        """Shutdown of the database:
        - Writes any remaining data in the buffer to the database
        """
        if self.data_buffer:
            self.write_batch(self.data_buffer)
            self.data_buffer = []

    def write_data_to_db(self, data):
        """Writes data in batches to the database.
        - Appends data to the buffer
        - Writes the buffer to the database if it is full
        """
        orm_obj = self.create_orm_object_from_dict(data)
        self.data_buffer.append(orm_obj)

        if len(self.data_buffer) == self.batch_size:
            self.write_batch(self.data_buffer)
            self.data_buffer = []

    def write_batch(self, batch):
        """Writes a batch of data to the database.
        - Opens a new session
        - Writes the batch to the database
        - Commits the session
        """
        with Session(self.engine) as session:
            session.bulk_save_objects(batch)
            session.commit()

    def create_orm_object_from_dict(self, dict):
        """Creates an ORM object from a dictionary."""
        orm_obj = orm_models.Timestep(
            time=dict["time"],
            T_amb=dict["T_amb"],
            P_solar=dict["P_solar"],
            T_in=dict["T_in"],
            T_en=dict["T_en"],
            P_heat_th=dict["P_heat_th"],
            P_heat_el=dict["P_heat_el"],
            P_base=dict["P_base"],
            P_pv=dict["P_pv"],
            P_bat=dict["P_bat"],
            Soc_bat=dict["Soc_bat"],
            fill_level=dict["fill_level"],
            P_load_pred=dict["P_load_pred"],
        )

        return orm_obj

    def get_load_profile(self, profile_id):
        """Gets a load profile from the database.
        - Queries the database for a load profile with the given profile_id
        - Returns the load profile
        """
        # Get column matching "profile_id" from table "annual_loadprofiles":
        # SELECT profile_id FROM annual_loadprofiles
        # NOTE: This is a bit of a hack, as columns are not really meant to be
        # queried like this in SQL.
        with Session(self.engine) as session:
            load_profile = session.execute(
                text('SELECT ":profile_id" FROM annual_loadprofiles'),
                {"profile_id": profile_id},
            ).fetchall()

        if not load_profile:
            raise ValueError(
                f"Load profile with ID {profile_id} not found in database."
            )

        # Turn elements of load_profile into a list
        load_profile = [x[0] for x in load_profile]

        return list(load_profile)

    def get_sim_results(self):
        """Gets the simulation results from the database."""
        with Session(self.engine) as session:
            results = session.query(orm_models.Timestep).all()

        # Create pd dataframe from results
        measurements = {
            column: [getattr(result, column) for result in results]
            for column in orm_models.Timestep.__table__.columns.keys()
        }

        df = pd.DataFrame(measurements)
        df["time"] = pd.to_datetime(df["time"], unit="s")
        df.set_index("time", inplace=True)

        df["P_net_load"] = df["P_base"] + df["P_pv"] + df["P_heat_el"]
        df["P_total"] = df["P_net_load"] + df["P_bat"]

        return df
