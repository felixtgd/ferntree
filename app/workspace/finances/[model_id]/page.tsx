
import { Suspense } from 'react';
import { FinBarSkeleton, FinKpiSkeleton } from '@/app/components/skeletons';
import { ModelSummary } from './model-summary';
import { FinKpis } from './fin-kpis';
import { FinBarChart } from './fin-bar-chart';


export default async function Page({ params }:
    {
        params: { model_id: string },
    }) {

    return (
        <div className="grid gap-4 grid-cols-3 grid-rows-3 h-full">

            {/* Model summary */}
            <div className="col-span-1 row-span-1 flex flex-col flex-grow w-full">
                <Suspense key={params.model_id}  fallback={<FinKpiSkeleton/>}>
                    <ModelSummary model_id={params.model_id}/>
                </Suspense>
            </div>

            {/* Fin KPIs */}
            <div className="col-span-1 row-span-1 flex flex-col flex-grow w-full">
                <Suspense key={params.model_id}  fallback={<FinKpiSkeleton/>}>
                    <FinKpis model_id={params.model_id}/>
                </Suspense>
            </div>

            {/* Bar chart with investments and revenue */}
            <div className="col-span-1 row-span-1 flex flex-col flex-grow w-full">
                <Suspense key={params.model_id}  fallback={<FinBarSkeleton/>}>
                    <FinBarChart model_id={params.model_id}/>
                </Suspense>
            </div>

        </div>
    );
}
