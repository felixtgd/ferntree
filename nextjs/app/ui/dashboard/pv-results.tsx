import { useContext } from 'react';
import SimDataContext from '@/app/ui/dashboard/pv-context';
import { PvDonutChart } from '@/app/ui/dashboard/donut-chart';

export default function PvResults() {
  const data = useContext(SimDataContext);

  return (
    <div>
      {data && (
        <>
          <div className="flex items-start space-x-4">
            <div className="m-4 p-4">
              {/* Donut chart for consumption */}
              <PvDonutChart
                data={[
                  {
                    name: 'PV',
                    value: data.energy_kpis.self_consumption,
                    share: data.energy_kpis.self_consumption/data.energy_kpis.baseload_demand
                  },
                  {
                    name: 'Grid',
                    value: data.energy_kpis.grid_consumption,
                    share: data.energy_kpis.grid_consumption/data.energy_kpis.baseload_demand
                  },
                ]}
                labels={{
                  center: data.energy_kpis.self_sufficiency,
                  title: data.energy_kpis.baseload_demand,
                }}
                title='Consumption'
              />
            </div>
            <div className="m-4 p-4">
              {/* Donut chart for pv generation */}
              <PvDonutChart
                data={[
                  {
                    name: 'Self-consumption',
                    value: data.energy_kpis.self_consumption,
                    share: data.energy_kpis.self_consumption/data.energy_kpis.pv_generation
                  },
                  {
                    name: 'Grid Feed-in',
                    value: data.energy_kpis.grid_feed_in,
                    share: data.energy_kpis.grid_feed_in/data.energy_kpis.pv_generation
                  },
                ]}
                labels={{
                  center: data.energy_kpis.self_consumption_rate,
                  title: data.energy_kpis.pv_generation,
                }}
                title='PV Generation'
              />
            </div>
          </div>

        </>
      )}
    </div>
  );
}
