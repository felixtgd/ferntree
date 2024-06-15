import { LineChart, Card, DateRangePicker, DateRangePickerValue, DateRangePickerItem } from '@tremor/react';
import { enGB} from 'date-fns/locale';
import React, { useContext, useState, useEffect, useCallback } from 'react';
import SimDataContext from '@/app/ui/dashboard/pv-context';
import { ValueFormatter } from '@tremor/react';

const dataFormatter: ValueFormatter = (number: number) => `${number.toFixed(2)} kW`;

export function PowerProfilePlots() {
  // Data context from the simulation
  const simData = useContext(SimDataContext);

  // Date range picker value
  const [dateValue, setdateValue] = useState<DateRangePickerValue>({
    from: new Date(2023, 4, 1),
    to: new Date(2023, 4, 8),
  });

  // Chart data / power profiles
  const [chartData, setChartData] = useState([]);

  // Function to fetch data from the backend
  const fetchData = useCallback(async (dateRange: DateRangePickerValue) => {
    if (simData) {
      try {
        const requestBody = {
          sim_id: simData?.sim_id,
          start_date: dateRange.from?.toISOString(),
          end_date: dateRange.to?.toISOString(),
        };
        const response = await fetch('http://localhost:8000/dashboard/fetch-timeseries-data', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(requestBody),
        });
        const timeseries_data = await response.json();

        setChartData(timeseries_data);
      } catch (error) {
        console.error(`Failed to fetch data for date range ${dateRange}:`, error);
      }
    }
  }, [simData]);

  // useEffect to trigger data fetch on date range change
  useEffect(() => {
    fetchData(dateValue);
  }, [dateValue, fetchData]);

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
                <DateRangePicker
                  className="mx-auto max-w-md"
                  value={dateValue}
                  onValueChange={setdateValue}
                  locale={enGB}
                >
                  <DateRangePickerItem
                    key="spring"
                    value="spring"
                    from={new Date(2023, 2, 19)}
                    to={new Date(2023, 2, 24)}
                  >
                    Spring
                  </DateRangePickerItem>
                  <DateRangePickerItem
                    key="summer"
                    value="summer"
                    from={new Date(2023, 5, 19)}
                    to={new Date(2023, 5, 24)}
                  >
                    Summer
                  </DateRangePickerItem>
                  <DateRangePickerItem
                    key="autumn"
                    value="autumn"
                    from={new Date(2023, 8, 19)}
                    to={new Date(2023, 8, 24)}
                  >
                    Autumn
                  </DateRangePickerItem>
                  <DateRangePickerItem
                    key="winter"
                    value="winter"
                    from={new Date(2023, 11, 19)}
                    to={new Date(2023, 11, 24)}
                  >
                    Winter
                  </DateRangePickerItem>
                </DateRangePicker>
                <LineChart
                    className="h-80"
                    data={chartData}
                    index="time"
                    categories={['Load', 'PV', 'Battery', 'Total']}
                    colors={['rose', 'amber', 'emerald', 'indigo']}
                    valueFormatter={dataFormatter}
                    yAxisWidth={80}
                    onValueChange={(v) => console.log(v)}
                    showAnimation={true}
                    startEndOnly={true}
                />
              </Card>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
