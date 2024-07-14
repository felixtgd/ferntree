import { Card } from '@tremor/react';
import { fetchPvMonthlyData } from './actions';
import { PVMonthlyGenData } from '@/app/lib/definitions';
import { BasePvBarChart } from './base-comps';


export async function PvGenBarChart({modelId}: {modelId: string}) {

  const chartData: PVMonthlyGenData[] = await fetchPvMonthlyData(modelId);

  return (
        <Card
          className="sm:mx-auto sm:max-w-lg max-h-80"
          decoration="top"
          decorationColor="blue-300"
        >
          <h3 className="text-center text-tremor-content-strong dark:text-dark-tremor-content-strong font-medium">Monthly PV Generation</h3>
          <BasePvBarChart data={chartData} />
        </Card>
  );
}
