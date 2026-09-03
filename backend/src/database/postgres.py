import os
from datetime import datetime
from typing import Any, Optional

from dotenv import load_dotenv
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool

from src.database.models import (
    FinFormData,
    FinResults,
    ModelDataOut,
    SimDataIn,
    SimResultsEval,
)

load_dotenv("./.env")
DATABASE_URL = os.environ["DATABASE_URL"]
pool = AsyncConnectionPool(conninfo=DATABASE_URL, open=False)


def _int_id(value: str) -> Optional[int]:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _parse_datetime(value: Optional[str]) -> Optional[datetime]:
    return datetime.fromisoformat(value) if value else None


class Database:
    """Class for interacting with the PostgreSQL database."""

    async def _assert_model_owner(self, conn: Any, model_id: int, user_id: str) -> None:
        """Raise an error unless the user owns the model.

        Args:
            conn (Any): The active database connection.
            model_id (int): The internal model ID.
            user_id (str): The username claiming ownership of the model.

        """
        async with conn.cursor() as cur:
            await cur.execute(
                """SELECT 1 FROM models m JOIN users u ON u.id = m.user_id
                WHERE m.id = %s AND u.username = %s""",
                (model_id, user_id),
            )
            if await cur.fetchone() is None:
                raise RuntimeError(f"Model {model_id} not found")

    async def check_user_exists(self, user_id: str) -> bool:
        """Check whether a username exists in the database.

        Args:
            user_id (str): The username to check.

        Returns:
            bool: Whether the username exists.

        """
        async with pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT 1 FROM users WHERE username = %s", (user_id,))
                return await cur.fetchone() is not None

    async def insert_model(self, model: dict[str, Any]) -> str:
        """Insert a model into the database.

        Args:
            model (dict): The model data to insert.

        Returns:
            str: The string ID of the inserted model.

        """
        coordinates = model.get("coordinates") or {}
        async with pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    INSERT INTO models (
                        user_id, model_name, location, roof_incl, roof_azimuth,
                        electr_cons, peak_power, battery_cap, time_created,
                        coord_lat, coord_lon, coord_display_name
                    )
                    SELECT id, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    FROM users WHERE username = %s
                    RETURNING id
                    """,
                    (
                        model["model_name"],
                        model["location"],
                        model["roof_incl"],
                        model["roof_azimuth"],
                        model["electr_cons"],
                        model["peak_power"],
                        model["battery_cap"],
                        _parse_datetime(model.get("time_created")),
                        coordinates.get("lat"),
                        coordinates.get("lon"),
                        coordinates.get("display_name"),
                        model["user_id"],
                    ),
                )
                row = await cur.fetchone()
                if row is None:
                    raise RuntimeError(f"User {model['user_id']} not found")
                return str(row[0])

    @staticmethod
    def _model_from_row(row: dict[str, Any]) -> ModelDataOut:
        coordinates = None
        if row["coord_lat"] is not None:
            coordinates = {
                "lat": row["coord_lat"],
                "lon": row["coord_lon"],
                "display_name": row["coord_display_name"],
            }
        return ModelDataOut(
            user_id=row["username"],
            model_name=row["model_name"],
            location=row["location"],
            roof_incl=row["roof_incl"],
            roof_azimuth=row["roof_azimuth"],
            electr_cons=row["electr_cons"],
            peak_power=row["peak_power"],
            battery_cap=row["battery_cap"],
            coordinates=coordinates,
            time_created=row["time_created"].isoformat()
            if row["time_created"]
            else None,
            model_id=str(row["id"]),
            sim_id=str(row["sim_id"]) if row["sim_id"] is not None else None,
        )

    async def fetch_models(self, user_id: str) -> list[ModelDataOut]:
        """Fetch all models belonging to a user.

        Args:
            user_id (str): The username that owns the models.

        Returns:
            list[ModelDataOut]: The user's models.

        """
        async with pool.connection() as conn:
            async with conn.cursor(row_factory=dict_row) as cur:
                await cur.execute(
                    """
                    SELECT m.*, u.username FROM models m
                    JOIN users u ON u.id = m.user_id
                    WHERE u.username = %s ORDER BY m.id
                    """,
                    (user_id,),
                )
                return [self._model_from_row(row) async for row in cur]

    async def fetch_model_by_id(self, model_id: str, user_id: str) -> ModelDataOut:
        """Fetch one user-owned model by its string ID.

        Args:
            model_id (str): The string ID of the model.
            user_id (str): The username that owns the model.

        Returns:
            ModelDataOut: The requested model.

        """
        internal_id = _int_id(model_id)
        if internal_id is None:
            raise RuntimeError(f"Failed to fetch model with ID {model_id}")
        async with pool.connection() as conn:
            async with conn.cursor(row_factory=dict_row) as cur:
                await cur.execute(
                    """
                    SELECT m.*, u.username FROM models m
                    JOIN users u ON u.id = m.user_id
                    WHERE m.id = %s AND u.username = %s
                    """,
                    (internal_id, user_id),
                )
                row = await cur.fetchone()
                if row is None:
                    raise RuntimeError(f"Failed to fetch model with ID {model_id}")
                return self._model_from_row(row)

    async def update_sim_id_of_model(
        self, model_id: str, sim_id: str, user_id: str
    ) -> bool:
        """Associate a simulation with a user-owned model.

        Args:
            model_id (str): The string ID of the model.
            sim_id (str): The string ID of the simulation.
            user_id (str): The username that owns the model.

        Returns:
            bool: Whether the model was updated.

        """
        model_pk, sim_pk = _int_id(model_id), _int_id(sim_id)
        if model_pk is None or sim_pk is None:
            return False
        async with pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """UPDATE models SET sim_id = %s
                    WHERE id = %s AND user_id = (
                        SELECT id FROM users WHERE username = %s)""",
                    (sim_pk, model_pk, user_id),
                )
                return cur.rowcount > 0

    async def delete_model(self, model_id: str, user_id: str) -> bool:
        """Delete a user-owned model and its dependent records.

        Args:
            model_id (str): The string ID of the model.
            user_id (str): The username that owns the model.

        Returns:
            bool: Whether the model was deleted.

        """
        internal_id = _int_id(model_id)
        if internal_id is None:
            return False
        async with pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """DELETE FROM models WHERE id = %s AND user_id = (
                        SELECT id FROM users WHERE username = %s)""",
                    (internal_id, user_id),
                )
                return cur.rowcount > 0

    async def upsert_simulation(self, document: SimDataIn, user_id: str) -> str:
        """Insert or update simulation input data.

        Args:
            document (SimDataIn): The simulation input data.
            user_id (str): The username that owns the simulation's model.

        Returns:
            str: The string ID of the simulation.

        """
        settings = document.system_settings
        coordinates = document.coordinates
        model_id = _int_id(document.model_id)
        if model_id is None:
            raise RuntimeError(f"Invalid model ID {document.model_id}")
        values = (
            model_id,
            _parse_datetime(document.run_time),
            document.timezone,
            document.timebase,
            document.planning_horizon,
            document.T_amb,
            document.G_i,
            coordinates.get("lat"),
            coordinates.get("lon"),
            coordinates.get("display_name"),
            settings.baseload.annual_consumption,
            settings.baseload.profile_id,
            settings.pv.roof_tilt,
            settings.pv.roof_azimuth,
            settings.pv.peak_power,
            settings.battery.capacity,
            settings.battery.max_power,
            settings.battery.soc_init,
            settings.battery.battery_ctrl.planning_horizon,
            settings.battery.battery_ctrl.useable_capacity,
            settings.battery.battery_ctrl.greedy,
            settings.battery.battery_ctrl.opt_fill,
        )
        columns = (
            "model_id",
            "run_time",
            "timezone",
            "timebase",
            "planning_horizon",
            "t_amb",
            "g_i",
            "coord_lat",
            "coord_lon",
            "coord_display_name",
            "baseload_annual_consumption",
            "baseload_profile_id",
            "pv_roof_tilt",
            "pv_roof_azimuth",
            "pv_peak_power",
            "battery_capacity",
            "battery_max_power",
            "battery_soc_init",
            "batctrl_planning_horizon",
            "batctrl_useable_capacity",
            "batctrl_greedy",
            "batctrl_opt_fill",
        )
        column_list = ",".join(columns)
        updates = ", ".join(f"{column} = EXCLUDED.{column}" for column in columns)
        async with pool.connection() as conn:
            await self._assert_model_owner(conn, model_id, user_id)
            async with conn.cursor() as cur:
                await cur.execute(
                    f"INSERT INTO simulations ({column_list}) "
                    f"VALUES ({','.join(['%s'] * len(values))}) "
                    f"ON CONFLICT (model_id) DO UPDATE SET {updates} RETURNING id",
                    values,
                )
                return str((await cur.fetchone())[0])

    async def fetch_sim_results_eval(
        self, model_id: str, user_id: str
    ) -> Optional[SimResultsEval]:
        """Fetch evaluated simulation results for a user-owned model.

        Args:
            model_id (str): The string ID of the model.
            user_id (str): The username that owns the model.

        Returns:
            Optional[SimResultsEval]: The evaluation, if it exists.

        """
        internal_id = _int_id(model_id)
        if internal_id is None:
            return None
        async with pool.connection() as conn:
            async with conn.cursor(row_factory=dict_row) as cur:
                await cur.execute(
                    """SELECT e.* FROM sim_results_eval e
                    JOIN models m ON m.id = e.model_id JOIN users u ON u.id = m.user_id
                    WHERE e.model_id = %s AND u.username = %s""",
                    (internal_id, user_id),
                )
                row = await cur.fetchone()
                if row is None:
                    return None
                await cur.execute(
                    "SELECT month, pv_generation FROM pv_monthly_gen "
                    "WHERE eval_id = %s ORDER BY id",
                    (row["id"],),
                )
                monthly = [dict(item) async for item in cur]
                return SimResultsEval(
                    model_id=model_id,
                    energy_kpis={
                        key: row[key]
                        for key in (
                            "annual_consumption",
                            "pv_generation",
                            "grid_consumption",
                            "grid_feed_in",
                            "self_consumption",
                            "self_consumption_rate",
                            "self_sufficiency",
                        )
                    },
                    pv_monthly_gen=monthly,
                )

    async def upsert_sim_results_eval(
        self, document: SimResultsEval, user_id: str
    ) -> str:
        """Insert or update evaluated simulation results and child rows.

        Args:
            document (SimResultsEval): The evaluated simulation results.
            user_id (str): The username that owns the results' model.

        Returns:
            str: The string ID of the evaluation.

        """
        model_id = _int_id(document.model_id)
        if model_id is None:
            raise RuntimeError(f"Invalid model ID {document.model_id}")
        kpis = document.energy_kpis
        values = (
            model_id,
            kpis.annual_consumption,
            kpis.pv_generation,
            kpis.grid_consumption,
            kpis.grid_feed_in,
            kpis.self_consumption,
            kpis.self_consumption_rate,
            kpis.self_sufficiency,
        )
        async with pool.connection() as conn:
            await self._assert_model_owner(conn, model_id, user_id)
            async with conn.transaction():
                async with conn.cursor() as cur:
                    await cur.execute(
                        """INSERT INTO sim_results_eval
                        (model_id, annual_consumption, pv_generation, grid_consumption,
                         grid_feed_in, self_consumption, self_consumption_rate,
                         self_sufficiency)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                        ON CONFLICT (model_id) DO UPDATE SET
                        annual_consumption=EXCLUDED.annual_consumption,
                        pv_generation=EXCLUDED.pv_generation,
                        grid_consumption=EXCLUDED.grid_consumption,
                        grid_feed_in=EXCLUDED.grid_feed_in,
                        self_consumption=EXCLUDED.self_consumption,
                        self_consumption_rate=EXCLUDED.self_consumption_rate,
                        self_sufficiency=EXCLUDED.self_sufficiency
                        WHERE sim_results_eval.model_id IN (
                            SELECT m.id FROM models m JOIN users u ON u.id = m.user_id
                            WHERE m.id = EXCLUDED.model_id AND u.username = %s)
                        RETURNING id""",
                        values + (user_id,),
                    )
                    eval_id = (await cur.fetchone())[0]
                    await cur.execute(
                        "DELETE FROM pv_monthly_gen WHERE eval_id = %s", (eval_id,)
                    )
                    await cur.executemany(
                        "INSERT INTO pv_monthly_gen "
                        "(eval_id, month, pv_generation) VALUES (%s,%s,%s)",
                        [
                            (eval_id, item.month, item.pv_generation)
                            for item in document.pv_monthly_gen
                        ],
                    )
                    return str(eval_id)

    async def fetch_finances(
        self, model_id: str, user_id: str
    ) -> Optional[FinFormData]:
        """Fetch financial input data for a user-owned model.

        Args:
            model_id (str): The string ID of the model.
            user_id (str): The username that owns the model.

        Returns:
            Optional[FinFormData]: The financial data, if it exists.

        """
        internal_id = _int_id(model_id)
        if internal_id is None:
            return None
        async with pool.connection() as conn:
            async with conn.cursor(row_factory=dict_row) as cur:
                await cur.execute(
                    """SELECT f.* FROM finances f JOIN models m ON m.id = f.model_id
                    JOIN users u ON u.id = m.user_id
                    WHERE f.model_id = %s AND u.username = %s""",
                    (internal_id, user_id),
                )
                row = await cur.fetchone()
                return (
                    FinFormData(
                        model_id=model_id,
                        **{
                            key: row[key]
                            for key in (
                                "electr_price",
                                "feed_in_tariff",
                                "pv_price",
                                "battery_price",
                                "useful_life",
                                "module_deg",
                                "inflation",
                                "op_cost",
                                "down_payment",
                                "pay_off_rate",
                                "interest_rate",
                            )
                        },
                    )
                    if row
                    else None
                )

    async def fetch_finances_for_user(self, user_id: str) -> list[FinFormData]:
        """Fetch financial input data for all models owned by a user.

        Args:
            user_id (str): The username that owns the models.

        Returns:
            list[FinFormData]: The user's financial data.

        """
        async with pool.connection() as conn:
            async with conn.cursor(row_factory=dict_row) as cur:
                await cur.execute(
                    """SELECT f.* FROM finances f
                    JOIN models m ON m.id = f.model_id
                    JOIN users u ON u.id = m.user_id
                    WHERE u.username = %s ORDER BY f.model_id""",
                    (user_id,),
                )
                fields = (
                    "electr_price",
                    "feed_in_tariff",
                    "pv_price",
                    "battery_price",
                    "useful_life",
                    "module_deg",
                    "inflation",
                    "op_cost",
                    "down_payment",
                    "pay_off_rate",
                    "interest_rate",
                )
                return [
                    FinFormData(
                        model_id=str(row["model_id"]),
                        **{field: row[field] for field in fields},
                    )
                    async for row in cur
                ]

    async def upsert_finances(self, document: FinFormData, user_id: str) -> str:
        """Insert or update financial input data.

        Args:
            document (FinFormData): The financial input data.
            user_id (str): The username that owns the data's model.

        Returns:
            str: The string ID of the financial data.

        """
        model_id = _int_id(document.model_id)
        if model_id is None:
            raise RuntimeError(f"Invalid model ID {document.model_id}")
        fields = (
            "electr_price",
            "feed_in_tariff",
            "pv_price",
            "battery_price",
            "useful_life",
            "module_deg",
            "inflation",
            "op_cost",
            "down_payment",
            "pay_off_rate",
            "interest_rate",
        )
        values = (model_id,) + tuple(getattr(document, field) for field in fields)
        assignments = ", ".join(f"{field}=EXCLUDED.{field}" for field in fields)
        async with pool.connection() as conn:
            await self._assert_model_owner(conn, model_id, user_id)
            async with conn.cursor() as cur:
                await cur.execute(
                    f"INSERT INTO finances (model_id,{','.join(fields)}) "
                    f"VALUES ({','.join(['%s'] * len(values))}) "
                    f"ON CONFLICT (model_id) DO UPDATE SET {assignments} "
                    "WHERE finances.model_id IN ("
                    "SELECT m.id FROM models m JOIN users u ON u.id = m.user_id "
                    "WHERE m.id = EXCLUDED.model_id AND u.username = %s) "
                    "RETURNING id",
                    values + (user_id,),
                )
                return str((await cur.fetchone())[0])

    async def fetch_fin_results(
        self, model_id: str, user_id: str
    ) -> Optional[FinResults]:
        """Fetch financial results for a user-owned model.

        Args:
            model_id (str): The string ID of the model.
            user_id (str): The username that owns the model.

        Returns:
            Optional[FinResults]: The financial results, if they exist.

        """
        internal_id = _int_id(model_id)
        if internal_id is None:
            return None
        async with pool.connection() as conn:
            async with conn.cursor(row_factory=dict_row) as cur:
                await cur.execute(
                    """SELECT f.* FROM fin_results f JOIN models m ON m.id = f.model_id
                    JOIN users u ON u.id = m.user_id
                    WHERE f.model_id = %s AND u.username = %s""",
                    (internal_id, user_id),
                )
                row = await cur.fetchone()
                if row is None:
                    return None
                await cur.execute(
                    "SELECT year, cum_profit, cum_cash_flow, loan "
                    "FROM fin_yearly_data WHERE fin_results_id = %s ORDER BY year",
                    (row["id"],),
                )
                yearly = [dict(item) async for item in cur]
                return FinResults(
                    model_id=model_id,
                    fin_kpis={
                        "investment": {
                            "pv": row["investment_pv"],
                            "battery": row["investment_battery"],
                            "total": row["investment_total"],
                        },
                        **{
                            key: row[key]
                            for key in (
                                "break_even_year",
                                "cum_profit",
                                "cum_cost_savings",
                                "cum_feed_in_revenue",
                                "cum_operation_costs",
                                "lcoe",
                                "solar_interest_rate",
                                "loan",
                                "loan_paid_off",
                            )
                        },
                    },
                    yearly_data=yearly,
                )

    async def upsert_fin_results(self, document: FinResults, user_id: str) -> str:
        """Insert or update financial results and child rows.

        Args:
            document (FinResults): The financial results.
            user_id (str): The username that owns the results' model.

        Returns:
            str: The string ID of the financial results.

        """
        model_id = _int_id(document.model_id)
        if model_id is None:
            raise RuntimeError(f"Invalid model ID {document.model_id}")
        kpis = document.fin_kpis
        fields = (
            "investment_pv",
            "investment_battery",
            "investment_total",
            "break_even_year",
            "cum_profit",
            "cum_cost_savings",
            "cum_feed_in_revenue",
            "cum_operation_costs",
            "lcoe",
            "solar_interest_rate",
            "loan",
            "loan_paid_off",
        )
        values = (
            model_id,
            kpis.investment.pv,
            kpis.investment.battery,
            kpis.investment.total,
            kpis.break_even_year,
            kpis.cum_profit,
            kpis.cum_cost_savings,
            kpis.cum_feed_in_revenue,
            kpis.cum_operation_costs,
            kpis.lcoe,
            kpis.solar_interest_rate,
            kpis.loan,
            kpis.loan_paid_off,
        )
        assignments = ", ".join(f"{field}=EXCLUDED.{field}" for field in fields)
        async with pool.connection() as conn:
            await self._assert_model_owner(conn, model_id, user_id)
            async with conn.transaction():
                async with conn.cursor() as cur:
                    await cur.execute(
                        f"INSERT INTO fin_results (model_id,{','.join(fields)}) "
                        f"VALUES ({','.join(['%s'] * len(values))}) "
                        f"ON CONFLICT (model_id) DO UPDATE SET {assignments} "
                        "WHERE fin_results.model_id IN ("
                        "SELECT m.id FROM models m JOIN users u ON u.id = m.user_id "
                        "WHERE m.id = EXCLUDED.model_id AND u.username = %s) "
                        "RETURNING id",
                        values + (user_id,),
                    )
                    result_id = (await cur.fetchone())[0]
                    await cur.execute(
                        "DELETE FROM fin_yearly_data WHERE fin_results_id = %s",
                        (result_id,),
                    )
                    await cur.executemany(
                        "INSERT INTO fin_yearly_data "
                        "(fin_results_id, year, cum_profit, cum_cash_flow, loan) "
                        "VALUES (%s,%s,%s,%s,%s)",
                        [
                            (
                                result_id,
                                item.year,
                                item.cum_profit,
                                item.cum_cash_flow,
                                item.loan,
                            )
                            for item in document.yearly_data
                        ],
                    )
                    return str(result_id)

    async def fetch_timesteps(
        self,
        model_id: str,
        user_id: str,
        start: Optional[float] = None,
        end: Optional[float] = None,
        limit: Optional[int] = None,
    ) -> list[dict[str, float]]:
        """Fetch user-owned simulation timesteps in an optional time range.

        Args:
            model_id (str): The string ID of the model.
            user_id (str): The username that owns the model.
            start (Optional[float]): The inclusive start timestamp.
            end (Optional[float]): The inclusive end timestamp.
            limit (Optional[int]): The maximum number of rows to return.

        Returns:
            list[dict]: The matching simulation timesteps.

        """
        internal_id = _int_id(model_id)
        if internal_id is None:
            return []
        query = """SELECT t.time, t.t_amb, t.p_solar, t.p_base, t.p_pv, t.p_bat,
                   t.soc_bat, t.fill_level, t.p_load_pred
                   FROM sim_timesteps t JOIN models m ON m.sim_id = t.sim_id
                   JOIN users u ON u.id = m.user_id
                   WHERE m.id = %s AND u.username = %s"""
        params: list[Any] = [internal_id, user_id]
        if start is not None and end is not None:
            query += " AND t.time BETWEEN %s AND %s"
            params.extend([start, end])
        query += " ORDER BY t.time"
        if limit is not None:
            query += " LIMIT %s"
            params.append(limit)
        async with pool.connection() as conn:
            async with conn.cursor(row_factory=dict_row) as cur:
                await cur.execute(query, params)
                return [
                    {
                        "time": row["time"],
                        "T_amb": row["t_amb"],
                        "P_solar": row["p_solar"],
                        "P_base": row["p_base"],
                        "P_pv": row["p_pv"],
                        "P_bat": row["p_bat"],
                        "Soc_bat": row["soc_bat"],
                        "fill_level": row["fill_level"],
                        "P_load_pred": row["p_load_pred"],
                    }
                    async for row in cur
                ]

    async def clean_collection(self, collection: str) -> None:
        """Truncate an allowlisted database table.

        Args:
            collection (str): The table name to truncate.

        """
        allowed = {
            "users",
            "models",
            "simulations",
            "sim_timesteps",
            "sim_results_eval",
            "pv_monthly_gen",
            "finances",
            "fin_results",
            "fin_yearly_data",
            "loadprofiles",
        }
        if collection not in allowed:
            raise ValueError(f"Unknown table: {collection}")
        async with pool.connection() as conn:
            await conn.execute(f"TRUNCATE TABLE {collection} RESTART IDENTITY CASCADE")
