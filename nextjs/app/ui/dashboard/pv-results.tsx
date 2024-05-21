import { useContext } from 'react';
import PvDataContext from '@/app/ui/dashboard/pv-context';

export default function PvResults() {
  const data = useContext(PvDataContext);

  return (
    <div>
      {data && (
        <div>
          <p>Status: {data.status}</p>
          <p>Total investment: {data.total_investment}</p>
          <p>Break-even year: {data.break_even_year}</p>
        </div>
      )}
    </div>
  );
};
