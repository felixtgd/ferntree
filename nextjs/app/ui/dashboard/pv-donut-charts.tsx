import { useContext } from 'react';
import SimDataContext from '@/app/ui/dashboard/pv-context';
import { PvDonutChart } from '@/app/ui/dashboard/donut-chart';

export function PvDonutCharts() {
  const simData = useContext(SimDataContext);

  return (
    <div>
      {simData && (
        <>
          <div className="grid grid-cols-2 gap-4">
            <div className="col-span-1">
              {/* Donut chart for consumption */}
              <PvDonutChart
                data={[
                  {
                    name: 'PV',
                    value: simData.energy_kpis.self_consumption,
                    share: simData.energy_kpis.self_consumption/simData.energy_kpis.baseload_demand
                  },
                  {
                    name: 'Grid',
                    value: simData.energy_kpis.grid_consumption,
                    share: simData.energy_kpis.grid_consumption/simData.energy_kpis.baseload_demand
                  },
                ]}
                labels={{
                  center: simData.energy_kpis.self_sufficiency,
                  title: simData.energy_kpis.baseload_demand,
                }}
                title='Consumption'
              />
            </div>
            <div className="col-span-1">
              {/* Donut chart for pv generation */}
              <PvDonutChart
                data={[
                  {
                    name: 'Self-consumption',
                    value: simData.energy_kpis.self_consumption,
                    share: simData.energy_kpis.self_consumption/simData.energy_kpis.pv_generation
                  },
                  {
                    name: 'Grid Feed-in',
                    value: simData.energy_kpis.grid_feed_in,
                    share: simData.energy_kpis.grid_feed_in/simData.energy_kpis.pv_generation
                  },
                ]}
                labels={{
                  center: simData.energy_kpis.self_consumption_rate,
                  title: simData.energy_kpis.pv_generation,
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
