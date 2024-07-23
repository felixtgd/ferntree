import { PvForm } from '../pv-form';
import { PvDonutChart } from './pv-donut-chart';
import { PvPowerChart } from './pv-power-chart';
import { PvGenBarChart } from './pv-gen-bar-chart';
import { FinKpis } from './fin-kpis';
import { FinBarChart } from './fin-bar-chart';
import { Suspense } from 'react';
import { BarSkeleton, DonutSkeleton, FinBarSkeleton, FinKpiSkeleton, LineChartSkeleton } from './skeletons';
import { ModelSummary } from './model-summary';


export default async function Page({ params, searchParams }:
    {
        params: { model_id: string },
        searchParams: Record<string, string | string[] | undefined>
    }) {

    return (
        <main>
            <div className="grid gap-4 grid-cols-5">
                <div className="col-span-1">
                    <PvForm />
                </div>
                <div className="col-span-4">
                    <div className="grid gap-4 grid-cols-3 grid-rows-4">

                        {/* Placeholder */}
                        <div className="col-span-1 row-span-1 flex flex-col flex-grow w-full">
                            <Suspense key={params.model_id}  fallback={<FinKpiSkeleton/>}>
                                <ModelSummary modelId={params.model_id}/>
                            </Suspense>
                        </div>

                        {/* Financial KPIs */}
                        <div className="col-span-1 row-span-1 flex flex-col flex-grow w-full">
                            <Suspense key={params.model_id}  fallback={<FinKpiSkeleton/>}>
                                <FinKpis modelId={params.model_id}/>
                            </Suspense>
                        </div>

                        {/* Bar chart for financial analysis */}
                        <div className="col-span-1 row-span-1 flex flex-col flex-grow w-full">
                            <Suspense key={params.model_id}  fallback={<FinBarSkeleton/>}>
                                <FinBarChart modelId={params.model_id}/>
                            </Suspense>
                        </div>

                        {/* Donut chart for consumption */}
                        <div className="col-span-1 row-span-1 flex flex-col flex-grow w-full">
                            <Suspense key={params.model_id}  fallback={<DonutSkeleton/>}>
                                <PvDonutChart chartType='consumption' modelId={params.model_id}/>
                            </Suspense>
                        </div>

                        {/* Donut chart for pv generation */}
                        <div className="col-span-1 row-span-1 flex flex-col flex-grow w-full">
                            <Suspense key={params.model_id}  fallback={<DonutSkeleton/>}>
                                <PvDonutChart chartType='generation' modelId={params.model_id}/>
                            </Suspense>
                        </div>

                        {/* Bar chart for pv generation */}
                        <div className="col-span-1 row-span-1 flex flex-col flex-grow w-full">
                            <Suspense key={params.model_id}  fallback={<BarSkeleton/>}>
                                <PvGenBarChart modelId={params.model_id}/>
                            </Suspense>
                        </div>

                        <div className="col-span-3 row-span-2 flex flex-col flex-grow w-full">
                            <Suspense key={params.model_id}  fallback={<LineChartSkeleton/>}>
                                <PvPowerChart modelId={params.model_id} searchParams={searchParams}/>
                            </Suspense>
                        </div>

                    </div>
                </div>
            </div>
        </main>
    );
}
