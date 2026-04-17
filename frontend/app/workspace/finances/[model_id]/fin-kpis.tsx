import { List, ListItem } from '@tremor/react';
import { fetchFinResults } from './actions';
import { BaseCard } from '@/app/components/base-comps';
import { FinKPIs, FinResults } from '@/app/utils/definitions';

const moneyFormatter = (number: number) => `€ ${Math.round(number).toLocaleString()}`;

const yearFormatter = (number: number) =>
    `${number.toLocaleString(undefined, {minimumFractionDigits: 1, maximumFractionDigits: 1})} years`;

const interestFormatter = (number: number) =>
  `${number.toLocaleString(undefined, {minimumFractionDigits: 1, maximumFractionDigits: 1})} %`;

const lcoeFormatter = (number: number) =>
  `${number.toLocaleString(undefined, {minimumFractionDigits: 1, maximumFractionDigits: 1})} ct/kWh`;


export async function FinKpis({model_id}: {model_id: string}) {

  const fin_results : FinResults | undefined = await fetchFinResults(model_id);
  if (!fin_results) {
    return (
      <div>
        <BaseCard title="">
          <div>
            No results found. Calculate finances to get results.
          </div>
        </BaseCard>
      </div>
    )
  }
  const kpis : FinKPIs = fin_results.fin_kpis;

  return (
    <div>
      <BaseCard title="Key Performance Indicators">
        <List className="mt-2">
            <ListItem key="investment">
              <span title="Total investment of PV and battery">Total investment</span>
              <span><strong>{moneyFormatter(kpis.investment.total)}</strong></span>
            </ListItem>
            <ListItem key="cum_profit">
              <span title="Cumulative profit over the lifetime of the system">Cum. profit</span>
              <span><strong>{moneyFormatter(kpis.cum_profit)}</strong></span>
            </ListItem>
            <ListItem key="break_even_year">
              <span title="Time at which the cumulative profit equals the total investment">Break-even</span>
              <span><strong>{yearFormatter(kpis.break_even_year)}</strong></span>
            </ListItem>
            <ListItem key="loan">
              <span title="Total loan = total investment - down payment">Total loan</span>
              <span><strong>{moneyFormatter(kpis.loan)}</strong></span>
            </ListItem>
            <ListItem key="loan_paid_off">
              <span title="Year when the loan is paid off">Loan paid off</span>
              <span><strong>{yearFormatter(kpis.loan_paid_off)}</strong></span>
            </ListItem>
            <ListItem key="lcoe">
              <span title="Levelized cost of electricity = total system cost over its lifetime / total electricity output">LCOE</span>
              <span><strong>{lcoeFormatter(kpis.lcoe)}</strong></span>
            </ListItem>
            <ListItem key="solar_interest_rate">
              <span title="Average annual return on investment">ROI</span>
              <span><strong>{interestFormatter(kpis.solar_interest_rate)}</strong></span>
            </ListItem>
        </List>
      </BaseCard>
    </div>
  );
}
