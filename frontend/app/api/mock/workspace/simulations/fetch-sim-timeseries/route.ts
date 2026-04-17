import { NextResponse } from 'next/server';

// Returns a short timeseries (6 hourly steps) for the power chart.
export async function POST() {
    const base = new Date('2023-06-19T08:00:00Z');
    const steps = Array.from({ length: 24 }, (_, i) => {
        const t = new Date(base.getTime() + i * 3600 * 1000);
        const pv = i >= 6 && i <= 18 ? Math.round(2 + Math.sin((i - 6) / 12 * Math.PI) * 5) : 0;
        const load = 1.5;
        const battery = pv > load ? Math.min(pv - load, 2) : 0;
        const total = load - pv - battery;
        return {
            time: t.toISOString(),
            Load: load,
            PV: pv,
            Battery: battery,
            Total: Math.round(total * 10) / 10,
            StateOfCharge: Math.min(100, Math.round(40 + i * 2)),
        };
    });
    return NextResponse.json(steps);
}
