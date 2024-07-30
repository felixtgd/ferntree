import { FinBarChartItem, SimEvaluation, SimFinancialKPIs } from '@/app/data/definitions';
import { fetchSimResults } from './actions';
import { BaseCard, BaseFinBarChart } from '../../components/base-comps';


function getChartData(kpis: SimFinancialKPIs) {
  return [
    {
      type: 'Investment',
      'PV': kpis.investment.pv,
      'Battery': kpis.investment.battery,
    },
    {
      type: 'Revenue',
      'Cost savings': kpis.cum_cost_savings_25yrs,
      'Feed-in revenue': kpis.cum_feed_in_revenue_25yrs,
      'Operation costs': -1 * kpis.cum_operation_costs_25yrs,
    },
  ];
}

export async function FinBarChart({modelId}: {modelId: string}) {

  const simResults : SimEvaluation = await fetchSimResults(modelId);
  const kpis : SimFinancialKPIs = simResults.financial_analysis.kpis;
  const chartData : FinBarChartItem[] = getChartData(kpis);

  return (
    <BaseCard title="Financial Perfomance over 25 years">
      <BaseFinBarChart data={chartData} />
    </BaseCard>
  );
}
