import { BarChart, Card,  } from '@tremor/react';
import { ValueFormatter } from '@tremor/react';
import { fetchPvMonthlyData } from './actions';

const dataFormatterkWh: ValueFormatter = (number: number) => `${Math.round(number).toLocaleString()} kWh`;

export async function PvGenBarChart({modelId}: {modelId: string}) {

  const chartData = await fetchPvMonthlyData(modelId);

  return (
        <Card
          className="sm:mx-auto sm:max-w-lg max-h-80"
          decoration="top"
          decorationColor="blue-300"
        >
          <h3 className="text-center text-tremor-content-strong dark:text-dark-tremor-content-strong font-medium">Monthly PV Generation</h3>
          <BarChart
            className="mt-2 max-h-60"
            data={chartData}
            index="month"
            categories={['PVGeneration']}
            colors={['amber']}
            valueFormatter={dataFormatterkWh}
            yAxisWidth={85}
            onValueChange={(v) => console.log(v)}
            showLegend={false}
            showAnimation={true}
          />
        </Card>
  );
}
