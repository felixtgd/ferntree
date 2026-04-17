
import { PvDonutChart } from './pv-donut-chart';
import { PvPowerChart } from './pv-power-chart';
import { PvGenBarChart } from './pv-gen-bar-chart';
import { fetchPowerData } from './actions';


export default async function Page({ params }:
    {
        params: { model_id: string },
    }) {

    // Default date range: a representative summer week in June 2023 (matches simulation data year).
    const initial_power_data = await fetchPowerData(params.model_id, '2023-06-19', '2023-06-24');

    return (
        <div className="grid gap-4 grid-cols-3 grid-rows-3 h-full">

            {/* Donut chart for consumption */}
            <div className="col-span-1 row-span-1 flex flex-col flex-grow w-full h-full">
                <PvDonutChart chart_type='consumption' model_id={params.model_id}/>
            </div>

            {/* Donut chart for pv generation */}
            <div className="col-span-1 row-span-1 flex flex-col flex-grow w-full h-full">
                <PvDonutChart chart_type='generation' model_id={params.model_id}/>
            </div>

            {/* Bar chart for pv generation */}
            <div className="col-span-1 row-span-1 flex flex-col flex-grow w-full h-full">
                <PvGenBarChart model_id={params.model_id}/>
            </div>

            <div className="col-span-3 row-span-2 flex flex-col flex-grow w-full h-full">
                <PvPowerChart model_id={params.model_id} initial_data={initial_power_data} />
            </div>

        </div>
    );
}
