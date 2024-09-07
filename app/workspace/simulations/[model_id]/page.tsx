
import { PvDonutChart } from './pv-donut-chart';
import { PvPowerChart } from './pv-power-chart';
import { PvGenBarChart } from './pv-gen-bar-chart';
import { Suspense } from 'react';
import { BarSkeleton, DonutSkeleton, LineChartSkeleton } from '@/app/components/skeletons';
import { ModelSelection } from '../model_select_card';
// import { ModelSummary } from './model-summary';


export default async function Page({ params, searchParams }:
    {
        params: { model_id: string },
        searchParams: Record<string, string | string[] | undefined>
    }) {

    return (
        <main>
            <div className="flex justify-between items-center p-4">
                <h3 className="mx-auto text-2xl font-semibold text-tremor-content-strong dark:text-dark-tremor-content-strong">
                    Simulations
                </h3>
            </div>
            <div className="grid gap-4 grid-cols-5">
                <div className="col-span-1">
                    <ModelSelection />
                </div>
                <div className="col-span-4">
                    <div className="grid gap-4 grid-cols-3 grid-rows-3">

                        {/* Placeholder */}
                        {/* <div className="col-span-1 row-span-1 flex flex-col flex-grow w-full">
                            <Suspense key={params.model_id}  fallback={<FinKpiSkeleton/>}>
                                <ModelSummary modelId={params.model_id}/>
                            </Suspense>
                        </div> */}

                        {/* Donut chart for consumption */}
                        <div className="col-span-1 row-span-1 flex flex-col flex-grow w-full">
                            <Suspense key={params.model_id}  fallback={<DonutSkeleton/>}>
                                <PvDonutChart chart_type='consumption' model_id={params.model_id}/>
                            </Suspense>
                        </div>

                        {/* Donut chart for pv generation */}
                        <div className="col-span-1 row-span-1 flex flex-col flex-grow w-full">
                            <Suspense key={params.model_id}  fallback={<DonutSkeleton/>}>
                                <PvDonutChart chart_type='generation' model_id={params.model_id}/>
                            </Suspense>
                        </div>

                        {/* Bar chart for pv generation */}
                        <div className="col-span-1 row-span-1 flex flex-col flex-grow w-full">
                            <Suspense key={params.model_id}  fallback={<BarSkeleton/>}>
                                <PvGenBarChart model_id={params.model_id}/>
                            </Suspense>
                        </div>

                        <div className="col-span-3 row-span-2 flex flex-col flex-grow w-full">
                            <Suspense key={params.model_id}  fallback={<LineChartSkeleton/>}>
                                <PvPowerChart model_id={params.model_id} search_params={searchParams}/>
                            </Suspense>
                        </div>

                    </div>
                </div>
            </div>
        </main>
    );
}
