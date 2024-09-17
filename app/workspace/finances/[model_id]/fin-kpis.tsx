import { List, ListItem } from '@tremor/react';
import { fetchFinResults } from './actions';
import { BaseCard } from '../../../components/base-comps';
import { FinKPIs, FinResults } from '@/app/utils/definitions';

const moneyFormatter = (number: number) =>
    `€ ${Math.round(number).toLocaleString()}`;

const yearFormatter = (number: number) =>
    `${number.toFixed(1).toLocaleString()} years`;

const interestFormatter = (number: number) =>
  `${number.toFixed(1).toLocaleString()} %`;

const lcoeFormatter = (number: number) =>
  `${number.toFixed(1).toLocaleString()} cents/kWh`;


export async function FinKpis({model_id}: {model_id: string}) {

  const fin_results : FinResults | undefined = await fetchFinResults(model_id);
  if (!fin_results) {
    return <div>Finance results not found</div>;
  }
  const kpis : FinKPIs = fin_results.fin_kpis;

  return (
    <div>
      <BaseCard title="Financial KPIs">
        <List className="mt-2">
            <ListItem key={kpis.investment.total}>
              <span>Total investment</span>
              <span><strong>{moneyFormatter(kpis.investment.total)}</strong></span>
            </ListItem>
            <ListItem key={kpis.break_even_year}>
              <span>Break-even</span>
              <span><strong>{yearFormatter(kpis.break_even_year)}</strong></span>
            </ListItem>
            <ListItem key={kpis.cum_profit}>
              <span>Cumulative profit over useful life</span>
              <span><strong>{moneyFormatter(kpis.cum_profit)}</strong></span>
            </ListItem>
            <ListItem key={kpis.lcoe}>
              <span>Levelised cost of electricity</span>
              <span><strong>{lcoeFormatter(kpis.lcoe)}</strong></span>
            </ListItem>
            <ListItem key={kpis.solar_interest_rate}>
              <span>Solar interest rate</span>
              <span><strong>{interestFormatter(kpis.solar_interest_rate)}</strong></span>
            </ListItem>
        </List>
      </BaseCard>
    </div>
  );
}
