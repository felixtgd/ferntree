import { List, ListItem } from '@tremor/react';
import { fetchSimResults } from './actions';
import { SimEvaluation, SimFinancialKPIs } from '@/app/lib/definitions';
import { BaseCard } from './base-comps';

const moneyFormatter = (number: number) =>
    `€ ${Math.round(number).toLocaleString()}`;

const yearFormatter = (number: number) =>
    `${number.toFixed(1).toLocaleString()} years`;

const interestFormatter = (number: number) =>
  `${number.toFixed(1).toLocaleString()} %`;

const lcoeFormatter = (number: number) =>
  `${number.toFixed(1).toLocaleString()} cents/kWh`;


export async function FinKpis({modelId}: {modelId: string}) {

  const simResults : SimEvaluation = await fetchSimResults(modelId);
  const kpis : SimFinancialKPIs = simResults.financial_analysis.kpis;

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
            <ListItem key={kpis.cum_profit_25yrs}>
              <span>Cumulative profit over 25 years</span>
              <span><strong>{moneyFormatter(kpis.cum_profit_25yrs)}</strong></span>
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
