'use client'

import { useState } from 'react';
import { SimEvaluation } from '@/app/lib/definitions';
import SimDataContext from '@/app/ui/dashboard/pv-context';
import { PvForm } from '@/app/ui/dashboard/pv-form';
import { PvDonutChart } from '@/app/ui/dashboard/pv-donut-chart';
import { PvPowerChart } from '@/app/ui/dashboard/pv-power-chart';
import { PvGenBarChart } from '@/app/ui/dashboard/pv-gen-bar-chart';
import { FinKpis } from '@/app/ui/dashboard/fin-kpis';
import { FinBarChart } from '@/app/ui/dashboard/fin-bar-chart';

export default function Page() {
    const [simData, setSimData] = useState<SimEvaluation | null>(null);

    return (
        <main>
        <SimDataContext.Provider value={simData}>
            <div className="grid gap-4 grid-cols-5">
                <div className="col-span-1">
                    <PvForm setData={setSimData} />
                </div>
                <div className="col-span-4">
                    {simData && (
                        <div className="grid gap-4 grid-cols-3 grid-rows-3 h-full">

                            <div className="col-span-1 row-span-1 flex flex-col flex-grow w-full">
                                {/* Donut chart for consumption */}
                                <PvDonutChart chartType="consumption"
                                />
                            </div>

                            <div className="col-span-1 row-span-1 flex flex-col flex-grow w-full">
                                {/* Donut chart for pv generation */}
                                <PvDonutChart chartType='generation'
                                />
                            </div>

                            <div className="col-span-1 row-span-1 flex flex-col flex-grow w-full">
                                <PvGenBarChart />
                            </div>

                            <div className="col-span-1 row-span-2 flex flex-col flex-grow w-full">
                                <div className='grid grid-rows-2 gap-4'>
                                    <FinKpis />
                                    <FinBarChart />
                                </div>
                            </div>

                            <div className="col-span-2 row-span-2 flex flex-col flex-grow w-full">
                                <PvPowerChart />
                            </div>


                        </div>
                    )}
                </div>
            </div>
        </SimDataContext.Provider>
        </main>
    );
}
