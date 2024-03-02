from sqlalchemy import Column, Integer, Float
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

class Timestep(Base):
    __tablename__ = "ferntree_sim"

    timestep = Column("timestep", Integer, primary_key=True, autoincrement=True)
    T_amb = Column("T_amb", Float, nullable=False)
    P_solar = Column("P_solar", Float, nullable=False)
    T_in = Column("T_in", Float, nullable=True)
    T_en = Column("T_en", Float, nullable=True)
    P_heat_th = Column("P_heat_th", Float, nullable=True)
    P_heat_el = Column("P_heat_el", Float, nullable=True)
    P_hgain = Column("P_hgain", Float, nullable=True)
    P_base = Column("P_base", Float, nullable=True)
    P_pv = Column("P_pv", Float, nullable=True)
    P_bat = Column("P_bat", Float, nullable=True)

