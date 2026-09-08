"""Persist finance inputs and calculated finance results asynchronously."""

from typing import Optional

from src.db.async_client.repositories.base import BaseRepository
from src.db.schemas import (
    FinFormData,
    FinResults,
)


class FinanceRepository(BaseRepository):
    """Class for interacting with the PostgreSQL database."""

    async def fetch_finances(
        self, model_id: str, user_id: int
    ) -> Optional[FinFormData]:
        """Fetch financial input data for a user-owned model.

        Args:
            model_id (str): The string ID of the model.
            user_id (int): The user id that owns the model.

        Returns:
            Optional[FinFormData]: The financial data, if it exists.

        """
        internal_id = self._int_id(model_id)
        if internal_id is None:
            return None
        row = await self._fetch_one(
            """SELECT f.* FROM finances f JOIN models m
            ON m.id = f.model_id
            WHERE f.model_id = %s AND m.user_id = %s""",
            (internal_id, user_id),
        )
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

    async def fetch_finances_for_user(self, user_id: int) -> list[FinFormData]:
        """Fetch financial input data for all models owned by a user.

        Args:
            user_id (int): The user id that owns the models.

        Returns:
            list[FinFormData]: The user's financial data.

        """
        rows = await self._fetch_all(
            """SELECT f.* FROM finances f
            JOIN models m ON m.id = f.model_id
            WHERE m.user_id = %s ORDER BY f.model_id""",
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
            for row in rows
        ]

    async def upsert_finances(self, document: FinFormData, user_id: int) -> str:
        """Insert or update financial input data.

        Args:
            document (FinFormData): The financial input data.
            user_id (int): The user id that owns the data's model.

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
        async with self._owned_transaction(model_id, user_id) as cur:
            await cur.execute(
                f"INSERT INTO finances (model_id,{','.join(fields)}) "
                f"VALUES ({','.join(['%s'] * len(values))}) "
                f"ON CONFLICT (model_id) DO UPDATE SET {assignments} "
                "RETURNING id",
                values,
            )
            return str((await cur.fetchone())[0])

    async def fetch_fin_results(
        self, model_id: str, user_id: int
    ) -> Optional[FinResults]:
        """Fetch financial results for a user-owned model.

        Args:
            model_id (str): The string ID of the model.
            user_id (int): The user id that owns the model.

        Returns:
            Optional[FinResults]: The financial results, if they exist.

        """
        internal_id = self._int_id(model_id)
        if internal_id is None:
            return None
        row = await self._fetch_one(
            """SELECT f.* FROM fin_results f JOIN models m
            ON m.id = f.model_id
            WHERE f.model_id = %s AND m.user_id = %s""",
            (internal_id, user_id),
        )
        if row is None:
            return None
        yearly = await self._fetch_all(
            "SELECT year, cum_profit, cum_cash_flow, loan "
            "FROM fin_yearly_data WHERE fin_results_id = %s "
            "ORDER BY year",
            (row["id"],),
        )
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

    async def upsert_fin_results(self, document: FinResults, user_id: int) -> str:
        """Insert or update financial results and child rows.

        Args:
            document (FinResults): The financial results.
            user_id (int): The user id that owns the results' model.

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
        async with self._owned_transaction(model_id, user_id) as cur:
            await cur.execute(
                "DELETE FROM fin_results WHERE model_id = %s",
                (model_id,),
            )
            await cur.execute(
                "INSERT INTO fin_results "
                f"(model_id,{','.join(fields)}) "
                f"VALUES ({','.join(['%s'] * len(values))}) "
                "RETURNING id",
                values,
            )
            result_id = (await cur.fetchone())[0]
            await cur.executemany(
                "INSERT INTO fin_yearly_data "
                "(fin_results_id, year, cum_profit, cum_cash_flow, "
                "loan) VALUES (%s,%s,%s,%s,%s)",
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
