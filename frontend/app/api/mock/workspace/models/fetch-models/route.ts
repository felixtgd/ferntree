import { NextResponse } from 'next/server';

export async function GET() {
    return NextResponse.json([
        {
            model_id: 'mock-model-1',
            model_name: 'Mock Home',
            location: 'Berlin, Germany',
            roof_incl: 30,
            roof_azimuth: 0,
            electr_cons: 4000,
            peak_power: 10,
            battery_cap: 10,
            sim_id: 'mock-sim-1',
        },
        {
            model_id: 'mock-model-2',
            model_name: 'Mock Flat',
            location: 'Munich, Germany',
            roof_incl: 45,
            roof_azimuth: 45,
            electr_cons: 2500,
            peak_power: 6,
            battery_cap: 5,
            sim_id: null,
        },
    ]);
}
