import { Card } from '@tremor/react';
import { FinBarChartItem, SimEvaluation, SimFinancialKPIs } from '@/app/lib/definitions';
import { fetchSimResults } from './actions';
import { BaseFinBarChart } from './base-comps';


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
    <div>
      <Card
          className="sm:mx-auto sm:max-w-lg"
          decoration="top"
          decorationColor="blue-300"
      >
        <h3 className="text-center text-tremor-content-strong dark:text-dark-tremor-content-strong font-medium">Financial Perfomance over 25 years</h3>
        <BaseFinBarChart data={chartData} />
      </Card>
    </div>
  );
}
