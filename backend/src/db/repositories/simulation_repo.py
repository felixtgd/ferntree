from typing import Any, Optional

from psycopg.rows import dict_row

from src.db.pool import pool
from src.db.repositories.base import BaseRepository
from src.db.schemas import (
    SimDataIn,
    SimResultsEval,
)

MAX_TIMESTEPS = 100_000


class SimulationRepository(BaseRepository):
    """Class for interacting with the PostgreSQL database."""

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
        model_id = self._int_id(document.model_id)
        if model_id is None:
            raise RuntimeError(f"Invalid model ID {document.model_id}")
        values = (
            model_id,
            self._parse_datetime(document.run_time),
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
        internal_id = self._int_id(model_id)
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
        model_id = self._int_id(document.model_id)
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

    async def fetch_timesteps(
        self,
        model_id: str,
        user_id: str,
        start: Optional[float] = None,
        end: Optional[float] = None,
        limit: Optional[int] = None,
    ) -> list[dict[str, float]]:
        """Fetch user-owned simulation timesteps in an optional time range."""
        internal_id = self._int_id(model_id)
        if internal_id is None:
            return []

        effective_limit = MAX_TIMESTEPS if limit is None else min(limit, MAX_TIMESTEPS)
        query = """SELECT t.time, t.t_amb, t.p_solar, t.p_base, t.p_pv, t.p_bat,
                   t.soc_bat, t.fill_level, t.p_load_pred
                   FROM sim_timesteps t JOIN models m ON m.sim_id = t.sim_id
                   JOIN users u ON u.id = m.user_id
                   WHERE m.id = %s AND u.username = %s"""
        params: list[Any] = [internal_id, user_id]
        if start is not None and end is not None:
            query += " AND t.time BETWEEN %s AND %s"
            params.extend([start, end])
        query += " ORDER BY t.time LIMIT %s"
        params.append(effective_limit)

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
