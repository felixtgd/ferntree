import { NextResponse } from 'next/server';

export async function GET() {
    return NextResponse.json({
        model_id: 'mock-model-1',
        energy_kpis: {
            annual_consumption: 4000,
            pv_generation: 9500,
            grid_consumption: 1200,
            grid_feed_in: 6700,
            self_consumption: 2800,
            self_consumption_rate: 0.29,
            self_sufficiency: 0.70,
        },
        pv_monthly_gen: [
            { month: 'Jan', pv_generation: 300 },
            { month: 'Feb', pv_generation: 450 },
            { month: 'Mar', pv_generation: 750 },
            { month: 'Apr', pv_generation: 900 },
            { month: 'May', pv_generation: 1100 },
            { month: 'Jun', pv_generation: 1200 },
            { month: 'Jul', pv_generation: 1150 },
            { month: 'Aug', pv_generation: 1050 },
            { month: 'Sep', pv_generation: 800 },
            { month: 'Oct', pv_generation: 500 },
            { month: 'Nov', pv_generation: 350 },
            { month: 'Dec', pv_generation: 250 },
        ],
    });
}
