import { PvForm } from '../pv-form';
import { PvDonutChart } from './pv-donut-chart';
import { PvPowerChart } from './pv-power-chart';
import { PvGenBarChart } from './pv-gen-bar-chart';
import { FinKpis } from './fin-kpis';
import { FinBarChart } from './fin-bar-chart';
import { Suspense } from 'react';
import { BarSkeleton, DonutSkeleton, FinBarSkeleton, FinKpiSkeleton } from './skeletons';


export default async function Page({ params }: { params: { model_id: string } }) {

    return (
        <main>
            <div className="grid gap-4 grid-cols-5">
                <div className="col-span-1">
                    <PvForm />
                </div>
                <div className="col-span-4">
                    <div className="grid gap-4 grid-cols-3 grid-rows-3 h-full">

                        <div className="col-span-1 row-span-1 flex flex-col flex-grow w-full">
                            {/* Donut chart for consumption */}
                            <Suspense key={params.model_id}  fallback={<DonutSkeleton/>}>
                                <PvDonutChart chartType='consumption' modelId={params.model_id}/>
                            </Suspense>
                        </div>

                        <div className="col-span-1 row-span-1 flex flex-col flex-grow w-full">
                            {/* Donut chart for pv generation */}
                            <Suspense key={params.model_id}  fallback={<DonutSkeleton/>}>
                                <PvDonutChart chartType='generation' modelId={params.model_id}/>
                            </Suspense>
                        </div>

                        <div className="col-span-1 row-span-1 flex flex-col flex-grow w-full">
                            <Suspense key={params.model_id}  fallback={<BarSkeleton/>}>
                                <PvGenBarChart modelId={params.model_id}/>
                            </Suspense>
                        </div>

                        <div className="col-span-1 row-span-2 flex flex-col flex-grow w-full">
                            <div className='grid grid-rows-2 gap-4'>
                            <Suspense key={params.model_id}  fallback={<FinKpiSkeleton/>}>
                                <FinKpis modelId={params.model_id}/>
                            </Suspense>
                            <Suspense key={params.model_id}  fallback={<FinBarSkeleton/>}>
                                <FinBarChart modelId={params.model_id}/>
                            </Suspense>
                            </div>
                        </div>

                        <div className="col-span-2 row-span-2 flex flex-col flex-grow w-full">
                            <Suspense key={params.model_id}  fallback={<div>Loading...</div>}>
                                <PvPowerChart modelId={params.model_id}/>
                            </Suspense>
                        </div>
                    </div>
                </div>
            </div>
        </main>
    );
}
