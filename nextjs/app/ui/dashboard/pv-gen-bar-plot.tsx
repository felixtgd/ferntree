import { BarChart, Card,  } from '@tremor/react';
import React, { useContext, useState, useEffect } from 'react';
import SimDataContext from '@/app/ui/dashboard/pv-context';
import { ValueFormatter } from '@tremor/react';
import { SimEvaluation } from '@/app/lib/definitions';

const dataFormatterkWh: ValueFormatter = (number: number) => `${Math.round(number).toLocaleString()} kWh`;

export function GenBarPlot() {
  // Data context from the simulation
  const simData = useContext(SimDataContext);

  // Chart data: bar chart with monthly pv generation
  const [chartData, setChartData] = useState([]);

  // Function to fetch data from the backend
  const fetchData = async (simData: SimEvaluation | null) => {
    if (simData) {
      try {
        const response = await fetch(`http://localhost:8000/dashboard/pv-monthly-gen?sim_id=${simData.sim_id}`, {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' },
        });
        const pv_monthly_gen_data = await response.json();

        setChartData(pv_monthly_gen_data);
      } catch (error) {
        console.error(`Bar Chart: Failed to fetch data for sim_id ${simData.sim_id}:`, error);
      }
    }
  };

  useEffect(() => {
    fetchData(simData);
  }, [simData]);

  return (
    <div>
      {simData && (
        <>
          <div className="grid grid-cols-3 gap-4">
            <div className="col-span-2">
              <Card
                className="sm:mx-auto" // sm:max-w-lg
                decoration="top"
                decorationColor="blue-300"
              >
                <h3 className="text-center mt-2">Monthly PV Generation</h3>
                <BarChart
                  className="h-60"
                  data={chartData}
                  index="month"
                  categories={['PVGeneration']}
                  colors={['amber']}
                  valueFormatter={dataFormatterkWh}
                  yAxisWidth={80}
                  onValueChange={(v) => console.log(v)}
                  showLegend={false}
                  showAnimation={true}
                />
              </Card>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
