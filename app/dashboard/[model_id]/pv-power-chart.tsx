import { Card, DateRangePickerValue } from '@tremor/react';
import { fetchPowerData } from './actions';
import { z } from "zod";
import { redirect } from 'next/navigation';
import { BaseDateRangePicker, BaseLineChart } from './base-comps';
import { PowerTimeseriesItem } from '@/app/data/definitions';

export async function PvPowerChart({ modelId, searchParams }:
  {
    modelId: string;
    searchParams: Record<string, string | string[] | undefined>;
  }
) {

  const selectedDateRange: DateRangePickerValue = {
    from: searchParams.dateFrom ? new Date(searchParams.dateFrom as string) : new Date(2023, 5, 19),
    to: searchParams.dateTo ? new Date(searchParams.dateTo as string) : new Date(2023, 5, 24)
  };

  // Validate that dateRange values are valid dates
  const dateRangeSchema = z.object({
    from: z.date(),
    to: z.date()
  });

  const dateRange = dateRangeSchema.safeParse(
    {
      from: selectedDateRange.from,
      to: selectedDateRange.to
    }
  );

  if (!dateRange.success) {
    console.error(`Invalid date range: ${dateRange.error}`);
    redirect(`/dashboard/${modelId}`);
  }

  const chartData : PowerTimeseriesItem[] = await fetchPowerData(modelId, dateRange.data);

  return (
    <Card
      className="flex flex-grow flex-col items-center justify-center w-full max-h-120"
      decoration="top"
      decorationColor="blue-300"
    >
      <BaseDateRangePicker dateRange={dateRange.data} />
      <BaseLineChart data={chartData} />
    </Card>
  );
}
