import { Card } from '@tremor/react';
import { fetchFinResults } from './actions';
import { FinChartData, FinResults, FinYearlyData } from '@/app/utils/definitions';
import { BaseCard, BaseFinLineChart } from '@/app/components/base-comps';


function formatChartData(fin_results: FinResults) {

  const fin_yearly_data: FinYearlyData[] = fin_results.yearly_data;
  const currentYear = new Date().getFullYear();
  const formattedData: FinChartData[] = fin_yearly_data.map((yearly_data) => {
    return {
      "Year": currentYear + yearly_data.year,
      "Cum. Profit": yearly_data.cum_profit,
      "Investment": fin_results.fin_kpis.investment.total,
      "Cum. Cash Flow": yearly_data.cum_cash_flow,
      "Loan": yearly_data.loan,
    };
  });

  return formattedData;
}

export async function FinLineChart({model_id}: {model_id: string}) {

    const fin_results : FinResults | undefined = await fetchFinResults(model_id);
    if (!fin_results) {
      return (
        <div className="w-1/3">
          <BaseCard title="">
            <div>
              No results found. Calculate finances to get results.
            </div>
          </BaseCard>
        </div>
      )
    }
    // const fin_yearly_data: FinYearlyData[] = fin_results.yearly_data;
    const formattedData = formatChartData(fin_results);

  return (
    <Card
      className="flex flex-grow flex-col items-center justify-center w-full h-full"
      decoration="top"
      decorationColor="blue-300"
    >
        <BaseFinLineChart data={formattedData} />
    </Card>
  );
}
