'use client'

import { LineChart, Card, DateRangePicker, DateRangePickerValue, DateRangePickerItem } from '@tremor/react';
import { enGB} from 'date-fns/locale';
import { useState, useEffect, useCallback } from 'react';
import { ValueFormatter } from '@tremor/react';

const dataFormatterkW: ValueFormatter = (number: number) => `${number.toFixed(2)} kW`;
const dataFormatterkWh: ValueFormatter = (number: number) => `${number.toFixed(2)} kWh`;

export function PvPowerChart({modelId}: {modelId: string}) {
  // Date range picker value
  const [dateValue, setdateValue] = useState<DateRangePickerValue>({
    from: new Date(2023, 5, 19),
    to: new Date(2023, 5, 24),
  });

  // Chart data: power profiles of system components
  const [chartData, setChartData] = useState([]);

  // Function to fetch data from the backend
  const fetchData = useCallback(async (dateRange: DateRangePickerValue) => {
      try {
        const requestBody = {
          s_model_id: modelId,
          start_date: dateRange.from?.toISOString(),
          end_date: dateRange.to?.toISOString(),
        };

        // Wait 3 seconds
        await new Promise(resolve => setTimeout(resolve, 3000));

        const response = await fetch('http://localhost:8000/dashboard/sim-timeseries-data', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(requestBody),
        });
        const timeseries_data = await response.json();

        setChartData(timeseries_data);
      } catch (error) {
        console.error(`Power profiles: Failed to fetch data for date range ${dateRange}:`, error);
      }
    }
  , [modelId]);

  // useEffect to trigger data fetch on date range change
  useEffect(() => {
    fetchData(dateValue);
  }, [dateValue, fetchData]);

  return (
    <Card
        className="sm:mx-auto max-h-160" // sm:max-w-lg
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
      <h3 className="text-center text-tremor-content-strong dark:text-dark-tremor-content-strong font-medium mt-2">Power Profiles</h3>
      <LineChart
          className="max-h-64"
          data={chartData}
          index="time"
          categories={['Load', 'PV', 'Battery', 'Total']}
          colors={['rose', 'amber', 'teal', 'indigo']}
          valueFormatter={dataFormatterkW}
          yAxisWidth={80}
          onValueChange={(v) => console.log(v)}
          showAnimation={true}
          startEndOnly={true}
          showXAxis={false}
      />
      <h3 className="text-center text-tremor-content-strong dark:text-dark-tremor-content-strong font-medium mt-2">Battery State of Charge</h3>
      <LineChart
          className="max-h-32"
          data={chartData}
          index="time"
          categories={['StateOfCharge']}
          colors={['teal']}
          valueFormatter={dataFormatterkWh}
          yAxisWidth={80}
          onValueChange={(v) => console.log(v)}
          showAnimation={true}
          startEndOnly={true}
          showLegend={false}
          showXAxis={false}
      />
    </Card>
  );
}