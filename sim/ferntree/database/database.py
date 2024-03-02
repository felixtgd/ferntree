from sqlalchemy import URL, create_engine
from sqlalchemy.orm import Session

from database.orm_models import Base, Timestep

class Database():

    def __init__(self) -> None:
        # self._username = "dbuser"
        # self._password = "admin"
        self._host = "localhost"
        self._port = "5432"
        self._db_name = "sim_db"

        self.db_url = URL.create(
            "postgresql+psycopg2",
            #username=self._username,
            #password=self._password,
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

    def write_data(self, data):
        with Session(self.engine) as session:
            timestep_data = Timestep(
                timestep = data["timestep"],
                T_amb = data["T_amb"],
                P_solar = data["P_solar"],
                T_in = data["T_in"],
                T_env = data["T_env"],
                P_heat_th = data["P_heat_th"],
                P_heat_el = data["P_heat_el"],
                P_hgain = data["P_hgain"],
                P_base = data["P_base"],
                P_pv = data["P_pv"],
                P_bat = data["P_bat"],
            )

            session.add(timestep_data)
            session.commit()
