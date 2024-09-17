import { fetchFinResults } from './actions';
import { BaseCard, BaseFinBarChart } from '../../../components/base-comps';
import { FinBarChartItem, FinKPIs, FinResults } from '@/app/utils/definitions';


function getChartData(kpis: FinKPIs) {
  return [
    {
      type: 'Investment',
      'PV': kpis.investment.pv,
      'Battery': kpis.investment.battery,
    },
    {
      type: 'Revenue',
      'Cost savings': kpis.cum_cost_savings,
      'Feed-in revenue': kpis.cum_feed_in_revenue,
      'Operation costs': -1 * kpis.cum_operation_costs,
    },
  ];
}

export async function FinBarChart({model_id}: {model_id: string}) {

  const fin_results : FinResults | undefined = await fetchFinResults(model_id);
  if (!fin_results) {
    return <div>Finance results not found</div>;
  }
  const kpis : FinKPIs = fin_results.fin_kpis;
  const chartData : FinBarChartItem[] = getChartData(kpis);

  return (
    <BaseCard title="Financial Perfomance over Useful Life">
      <BaseFinBarChart data={chartData} />
    </BaseCard>
  );
}
