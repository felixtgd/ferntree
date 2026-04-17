
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
                <ModelSummary model_id={params.model_id}/>
            </div>

            {/* Fin KPIs */}
            <div className="col-span-1 row-span-1">
                <FinKpis model_id={params.model_id}/>
            </div>

            {/* Bar chart with investments and revenue */}
            <div className="col-span-1 row-span-1">
                <FinBarChart model_id={params.model_id}/>
            </div>

            {/* Line chart with yearly financial performance */}
            <div className="col-span-3 row-span-1">
                <FinLineChart model_id={params.model_id}/>
            </div>


        </div>
    );
}
