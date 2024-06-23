import { Card, List, ListItem } from '@tremor/react';
import { useContext } from 'react';
import SimDataContext from '@/app/ui/dashboard/pv-context';


const moneyFormatter = (number: number) =>
    `€ ${Math.round(number).toLocaleString()}`;

const yearFormatter = (number: number) =>
    `${number.toFixed(1).toLocaleString()} years`;

const interestFormatter = (number: number) =>
  `${number.toFixed(1).toLocaleString()} %`;

const lcoeFormatter = (number: number) =>
  `${number.toFixed(1).toLocaleString()} cents/kWh`;


export function FinKpis() {

  const simData = useContext(SimDataContext);
  const kpis = simData?.financial_analysis.kpis;

  return (
    <div>
      {kpis && (
        <Card
            className="sm:mx-auto sm:max-w-lg"
            decoration="top"
            decorationColor="blue-300"
        >
            <h3 className="text-center text-tremor-content-strong dark:text-dark-tremor-content-strong font-medium">Financial KPIs</h3>
            <List className="mt-2">
                <ListItem key={kpis.investment.total}>
                  <span>Total investment</span>
                  <span>{moneyFormatter(kpis.investment.total)}</span>
                </ListItem>
                <ListItem key={kpis.break_even_year}>
                  <span>Break-even</span>
                  <span>{yearFormatter(kpis.break_even_year)}</span>
                </ListItem>
                <ListItem key={kpis.cum_profit_25yrs}>
                  <span>Cumulative profit over 25 years</span>
                  <span>{moneyFormatter(kpis.cum_profit_25yrs)}</span>
                </ListItem>
                <ListItem key={kpis.lcoe}>
                  <span>Levelised cost of electricity</span>
                  <span>{lcoeFormatter(kpis.lcoe)}</span>
                </ListItem>
                <ListItem key={kpis.solar_interest_rate}>
                  <span>Solar interest rate</span>
                  <span>{interestFormatter(kpis.solar_interest_rate)}</span>
                </ListItem>
            </List>
        </Card>
      )}
    </div>
  );
}
