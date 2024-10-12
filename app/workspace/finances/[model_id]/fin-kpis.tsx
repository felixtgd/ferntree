import { List, ListItem } from '@tremor/react';
import { fetchFinResults } from './actions';
import { BaseCard } from '@/app/components/base-comps';
import { FinKPIs, FinResults } from '@/app/utils/definitions';
import { Tooltip } from '@/app/components/components';

const moneyFormatter = (number: number) =>
    `€ ${Math.round(number).toLocaleString()}`;

const yearFormatter = (number: number) =>
    `${number.toFixed(1).toLocaleString()} years`;

const interestFormatter = (number: number) =>
  `${number.toFixed(1).toLocaleString()} %`;

const lcoeFormatter = (number: number) =>
  `${number.toFixed(1).toLocaleString()} ct/kWh`;


export async function FinKpis({model_id}: {model_id: string}) {

  const fin_results : FinResults | undefined = await fetchFinResults(model_id);
  if (!fin_results) {
    return <div>Finance results not found</div>;
  }
  const kpis : FinKPIs = fin_results.fin_kpis;

  return (
    <div>
      <BaseCard title="Key Performance Indicators">
        <List className="mt-2">
            <ListItem key={kpis.investment.total}>
              <Tooltip content="Total investment of PV and battery">
                <span>Total investment</span>
              </Tooltip>
              <span><strong>{moneyFormatter(kpis.investment.total)}</strong></span>
            </ListItem>
            <ListItem key={kpis.cum_profit}>
              <Tooltip content="Cumulative profit over the lifetime of the system">
                <span>Cum. profit</span>
              </Tooltip>
              <span><strong>{moneyFormatter(kpis.cum_profit)}</strong></span>
            </ListItem>
            <ListItem key={kpis.break_even_year}>
              <Tooltip content="Time at which the cumulative profit equals the total investment">
                <span>Break-even</span>
              </Tooltip>
              <span><strong>{yearFormatter(kpis.break_even_year)}</strong></span>
            </ListItem>
            <ListItem key={kpis.loan}>
              <Tooltip content="Total loan = total investment - down payment">
                <span>Total loan</span>
              </Tooltip>
              <span><strong>{moneyFormatter(kpis.loan)}</strong></span>
            </ListItem>
            <ListItem key={kpis.loan_paid_off}>
              <Tooltip content="Year when the loan is paid off">
                <span>Loan paid off</span>
              </Tooltip>
              <span><strong>{yearFormatter(kpis.loan_paid_off)}</strong></span>
            </ListItem>
            <ListItem key={kpis.lcoe}>
              <Tooltip content="Levelized cost of electricity = total system cost over its lifetime / total electricity output">
                <span>LCOE</span>
              </Tooltip>
              <span><strong>{lcoeFormatter(kpis.lcoe)}</strong></span>
            </ListItem>
            <ListItem key={kpis.solar_interest_rate}>
              <Tooltip content="Average annual return on investment">
                <span>ROI</span>
              </Tooltip>
              <span><strong>{interestFormatter(kpis.solar_interest_rate)}</strong></span>
            </ListItem>
        </List>
      </BaseCard>
    </div>
  );
}
