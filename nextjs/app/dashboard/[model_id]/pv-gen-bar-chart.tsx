import { fetchPvMonthlyData } from './actions';
import { PVMonthlyGenData } from '@/app/lib/definitions';
import { BaseCard, BasePvBarChart } from './base-comps';


export async function PvGenBarChart({modelId}: {modelId: string}) {

  const chartData: PVMonthlyGenData[] = await fetchPvMonthlyData(modelId);

  return (
    <BaseCard title="Monthly PV Generation">
      <BasePvBarChart data={chartData} />
    </BaseCard>
  );
}
