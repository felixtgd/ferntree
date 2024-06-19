import { Card, BarChart } from '@tremor/react';
import { SimFinancialKPIs } from '@/app/lib/definitions';


const moneyFormatter = (number: number) =>
    `€ ${Math.round(number).toLocaleString()}`;

export function FinKpisCard({ kpis }: { kpis: SimFinancialKPIs }) {

  const chartData = [
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

  return (
    <Card
        className="sm:mx-auto"  //sm:max-w-lg
        decoration="top"
        decorationColor="blue-300"
    >
      <h3 className="text-tremor-content-strong dark:text-dark-tremor-content-strong font-medium">Financial Perfomance over 25 years</h3>
      <BarChart
        className="h-60"
        data={chartData}
        index="type"
        categories={['Cost savings', 'Feed-in revenue', 'Operation costs', 'PV', 'Battery']}
        colors={['blue', 'cyan', 'purple', 'emerald', 'lime']}
        valueFormatter={moneyFormatter}
        yAxisWidth={80}
        onValueChange={(v) => console.log(v)}
        showLegend={false}
        showAnimation={true}
        stack={true}
      />
    </Card>
  );
}
