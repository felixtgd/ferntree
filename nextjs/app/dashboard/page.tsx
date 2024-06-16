'use client'

import PvForm from '@/app/ui/dashboard/pv-form';
import SimDataContext from '@/app/ui/dashboard/pv-context';
import PvResults from '@/app/ui/dashboard/pv-results';
import { SimEvaluation } from '@/app/lib/definitions';
import { useState } from 'react';
import { PowerProfilePlots } from '@/app/ui/dashboard/power-plots';
import { GenBarPlot } from '../ui/dashboard/pv-gen-bar-plot';

export default function Page() {
    const [data, setData] = useState<SimEvaluation | null>(null);

    return (
        <main>
        <SimDataContext.Provider value={data}>
            <div className="grid gap-6 grid-cols-5">
                <div className="col-span-1">
                    <PvForm setData={setData} />
                </div>
                <div className="col-span-4">
                    <div>
                        <PvResults />
                    </div>
                    <div className='mt-4'>
                        <PowerProfilePlots />
                    </div>
                    <div className='mt-4'>
                        <GenBarPlot />
                    </div>
                </div>
            </div>
        </SimDataContext.Provider>
        </main>
    );
}
