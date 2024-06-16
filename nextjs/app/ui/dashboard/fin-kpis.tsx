import { Card, List, ListItem } from '@tremor/react';


const moneyFormatter = (number: number) =>
    `€ ${Math.round(number).toLocaleString()}`;

const yearFormatter = (number: number) =>
    `${number.toFixed(1).toLocaleString()} years`;

export function FinKpisCard({ data }: { data: { investment: number; break_even: number}}) {

  return (
    <Card
        className="sm:mx-auto sm:max-w-lg"
        decoration="top"
        decorationColor="blue-300"
    >
      <h3 className="text-tremor-content-strong dark:text-dark-tremor-content-strong font-medium">Financial KPIs</h3>
      <List className="mt-2">
          <ListItem key={data.investment}>
            <span>Total investment</span>
            <span>{moneyFormatter(data.investment)}</span>
          </ListItem>
          <ListItem key={data.investment}>
            <span>Break-even</span>
            <span>{yearFormatter(data.break_even)}</span>
          </ListItem>
          <ListItem key={data.investment}>
            <span>Cumulative profit over 25 years</span>
            <span>X</span>
          </ListItem>
          <ListItem key={data.investment}>
            <span>Levelised cost of electricity</span>
            <span>X</span>
          </ListItem>
          <ListItem key={data.investment}>
            <span>Solar interest</span>
            <span>X</span>
          </ListItem>
      </List>
    </Card>
  );
}
