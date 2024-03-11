from sqlalchemy import Column, Integer, Float, CheckConstraint
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

class Timestep(Base):
    """ Table for the simulation results.
    Each row represents the results of one timestep in the simulation.
    """
    __tablename__ = "ferntree_sim"

    time =      Column("time",      Integer,   primary_key=True, index=True, nullable=False)
    T_amb =     Column("T_amb",     Float(24), nullable=False)
    P_solar =   Column("P_solar",   Float(24), nullable=False)
    T_in =      Column("T_in",      Float(24), nullable=False)
    T_en =      Column("T_en",      Float(24), nullable=False)
    P_heat_th = Column("P_heat_th", Float(24), nullable=False)
    P_heat_el = Column("P_heat_el", Float(24), nullable=False)
    P_base =    Column("P_base",    Float(24), nullable=False)
    P_pv =      Column("P_pv",      Float(24), nullable=False)
    P_bat =     Column("P_bat",     Float(24), nullable=False)

    __table_args__ = (
        CheckConstraint('"ferntree_sim".time >= 0'),

        CheckConstraint('"ferntree_sim"."T_amb" > 0'),
        CheckConstraint('"ferntree_sim"."T_amb" < 375.15'),

        CheckConstraint('"ferntree_sim"."P_solar" >= 0'),
        CheckConstraint('"ferntree_sim"."P_solar" < 10000'),

        CheckConstraint('"ferntree_sim"."T_in" > 0'),
        CheckConstraint('"ferntree_sim"."T_in" < 375.15'),

        CheckConstraint('"ferntree_sim"."T_en" > 0'),
        CheckConstraint('"ferntree_sim"."T_en" < 375.15'),

        CheckConstraint('"ferntree_sim"."P_heat_th" >= 0'),
        CheckConstraint('"ferntree_sim"."P_heat_th" < 10000'),

        CheckConstraint('"ferntree_sim"."P_heat_el" >= 0'),
        CheckConstraint('"ferntree_sim"."P_heat_el" < 10000'),

        CheckConstraint('"ferntree_sim"."P_base" >= 0'),
        CheckConstraint('"ferntree_sim"."P_base" < 10000'),

        CheckConstraint('"ferntree_sim"."P_pv" <= 0'),
        CheckConstraint('"ferntree_sim"."P_pv" < 10000'),
    )