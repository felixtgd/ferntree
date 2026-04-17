import { NextResponse } from 'next/server';

export async function GET() {
    const investment_total = 15000 + 6500; // pv + battery
    const yearly_data = Array.from({ length: 21 }, (_, i) => ({
        year: i,
        cum_profit: Math.round(-investment_total + i * 2100),
        cum_cash_flow: Math.round(-investment_total * 0.75 + i * 2100),
        loan: Math.max(0, Math.round(investment_total * 0.75 - i * 2100 * 0.5)),
    }));

    return NextResponse.json({
        model_id: 'mock-model-1',
        fin_kpis: {
            investment: { pv: 15000, battery: 6500, total: investment_total },
            break_even_year: 10.2,
            cum_profit: 17000,
            cum_cost_savings: 28000,
            cum_feed_in_revenue: 8500,
            cum_operation_costs: 2150,
            lcoe: 8.5,
            solar_interest_rate: 7.2,
            loan: 16125,
            loan_paid_off: 8.5,
        },
        yearly_data,
    });
}
