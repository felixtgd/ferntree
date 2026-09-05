from typing import Any, Optional

from psycopg.rows import dict_row

from src.db.models import (
    FinFormData,
    FinResults,
)
from src.db.pool import pool
from src.db.repositories.base import BaseRepository


class FinanceRepository(BaseRepository):
    """Class for interacting with the PostgreSQL database."""

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
        internal_id = self._int_id(model_id)
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
        model_id = self._int_id(document.model_id)
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
        internal_id = self._int_id(model_id)
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
        model_id = self._int_id(document.model_id)
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
        internal_id = self._int_id(model_id)
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
