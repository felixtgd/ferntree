import { LineChart, Card, DateRangePicker, DateRangePickerValue } from '@tremor/react';
import { enGB} from 'date-fns/locale';
import React, { useContext, useState, useEffect, useCallback } from 'react';
import SimDataContext from '@/app/ui/dashboard/pv-context';
// import { TimeseriesData } from '@/app/lib/definitions';


const dataFormatter = (number: number) =>
  `${number.toFixed(2)} kW`;


export function PowerProfilePlots() {
  // Data context from the simulation
  const data = useContext(SimDataContext);

  // Date range picker value
  const [dateValue, setdateValue] = useState<DateRangePickerValue>({
    from: new Date(2023, 4, 1),
    to: new Date(2023, 4, 8),
  });

  // Chart data / power profiles
  const [chartData, setChartData] = useState([]);

  // Function to fetch data from the backend
  const fetchData = useCallback(async (dateRange: DateRangePickerValue) => {
    try {
      const requestBody = {
        sim_id: data?.sim_id,
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
  }, [data?.sim_id]);

  // useEffect to trigger data fetch on date range change
  useEffect(() => {
    fetchData(dateValue);
  }, [dateValue, fetchData]);

  return (
    <div>
      {data && (
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
                  // add DateRangePickerItems for "typical" Winter, Spring, Summer, Fall days
                />
                <LineChart
                    className="h-80"
                    data={chartData}
                    index="time"
                    categories={['P_base', 'P_pv', 'P_bat']}
                    colors={['indigo', 'rose', 'cyan']}
                    valueFormatter={dataFormatter}
                    yAxisWidth={60}
                    onValueChange={(v) => console.log(v)}
                />
              </Card>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
