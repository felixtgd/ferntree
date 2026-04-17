import { NextResponse } from 'next/server';

export async function GET() {
    return NextResponse.json([
        {
            model_id: 'mock-model-1',
            electr_price: 45,
            feed_in_tariff: 8,
            pv_price: 1500,
            battery_price: 650,
            useful_life: 20,
            module_deg: 0.5,
            inflation: 3,
            op_cost: 1,
            down_payment: 25,
            pay_off_rate: 10,
            interest_rate: 5,
        },
    ]);
}
