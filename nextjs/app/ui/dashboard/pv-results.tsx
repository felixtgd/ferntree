import { useContext } from 'react';
import PvDataContext from '@/app/ui/dashboard/pv-context';

export default function PvResults() {
  const data = useContext(PvDataContext);

  return (
    <div>
      {data && (
        <div>
          <p>Status: {data.status}</p>
          <p>Model: {JSON.stringify(data.model)}</p>
        </div>
      )}
    </div>
  );
};
