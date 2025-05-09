
import { Suspense } from 'react';
import { FinBarSkeleton, FinKpiSkeleton, LineChartSkeleton } from '@/app/components/skeletons';
import { ModelSummary } from './model-summary';
import { FinKpis } from './fin-kpis';
import { FinBarChart } from './fin-bar-chart';
import { FinLineChart } from './fin-line-chart';


export default async function Page({ params }:
    {
        params: { model_id: string },
    }) {

    return (
        <div className="grid gap-4 grid-cols-3 grid-rows-[360px_360px] h-full">

            {/* Model summary */}
            <div className="col-span-1 row-span-1">
                <Suspense key={params.model_id}  fallback={<FinKpiSkeleton/>}>
                    <ModelSummary model_id={params.model_id}/>
                </Suspense>
            </div>

            {/* Fin KPIs */}
            <div className="col-span-1 row-span-1">
                <Suspense key={params.model_id}  fallback={<FinKpiSkeleton/>}>
                    <FinKpis model_id={params.model_id}/>
                </Suspense>
            </div>

            {/* Bar chart with investments and revenue */}
            <div className="col-span-1 row-span-1">
                <Suspense key={params.model_id}  fallback={<FinBarSkeleton/>}>
                    <FinBarChart model_id={params.model_id}/>
                </Suspense>
            </div>

            {/* Line chart with yearly financial performance */}
            <div className="col-span-3 row-span-1">
                <Suspense key={params.model_id}  fallback={<LineChartSkeleton/>}>
                    <FinLineChart model_id={params.model_id}/>
                </Suspense>
            </div>


        </div>
    );
}
