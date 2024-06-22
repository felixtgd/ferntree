'use client'

import PvForm from '@/app/ui/dashboard/pv-form';
import SimDataContext from '@/app/ui/dashboard/pv-context';
import { PvDonutCharts } from '@/app/ui/dashboard/pv-donut-charts';
import { FinKpis } from '@/app/ui/dashboard/fin-kpis';
import { SimEvaluation } from '@/app/lib/definitions';
import { useState } from 'react';
import { PowerProfilePlots } from '@/app/ui/dashboard/power-plots';
import { PvGenBarPlot } from '../ui/dashboard/pv-gen-bar-plot';

export default function Page() {
    const [data, setData] = useState<SimEvaluation | null>(null);

    return (
        <main>
        <SimDataContext.Provider value={data}>
            <div className="grid gap-4 grid-cols-5">
                <div className="col-span-1">
                    <PvForm setData={setData} />
                </div>
                <div className="col-span-4">
                        <div className="grid gap-4 grid-rows-3 grid-cols-3">
                            <div className="col-span-2 row-span-1">
                                <PvDonutCharts />
                            </div>
                            <div className="col-span-1 row-span-1">
                                <PvGenBarPlot />
                            </div>
                            <div className="col-span-1 row-span-2">
                                <FinKpis />
                            </div>
                            <div className='col-span-2 row-span-2'>
                                <PowerProfilePlots />
                            </div>
                    </div>
                </div>
            </div>
        </SimDataContext.Provider>
        </main>
    );
}
