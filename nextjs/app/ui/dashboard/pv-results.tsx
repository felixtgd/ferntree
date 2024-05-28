import { useContext } from 'react';
import SimDataContext from '@/app/ui/dashboard/pv-context';

export default function PvResults() {
  const data = useContext(SimDataContext);

  return (
    <div>
      {data && (
        <div>
          <p>Results</p>
          <p>Baseload demand: {Math.round(data.energy_kpis.baseload_demand)} kWh</p>
          <p>PV generation: {Math.round(data.energy_kpis.pv_generation)} kWh</p>
          <p>Grid consumption: {Math.round(data.energy_kpis.grid_consumption)} kWh</p>
          <p>Grid feed-in: {Math.round(data.energy_kpis.grid_feed_in)} kWh</p>
          <p>Self consumption: {Math.round(data.energy_kpis.self_consumption)} kWh</p>
          <p>Self consumption rate: {Math.round(data.energy_kpis.self_consumption_rate * 100)} %</p>
          <p>Self sufficiency: {Math.round(data.energy_kpis.self_sufficiency * 100)} %</p>
        </div>
      )}
    </div>
  );
};
