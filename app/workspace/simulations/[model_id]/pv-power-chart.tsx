import { Card, DateRangePickerValue } from '@tremor/react';
import { fetchPowerData } from './actions';
import { z } from "zod";
import { redirect } from 'next/navigation';
import { BaseDateRangePicker, BasePowerLineChart } from '@/app/components/base-comps';
import { SimTimestep } from '@/app/utils/definitions';

export async function PvPowerChart({ model_id, search_params }:
  {
    model_id: string;
    search_params: Record<string, string | string[] | undefined>;
  }
) {

  const selected_date_range: DateRangePickerValue = {
    from: search_params.dateFrom ? new Date(search_params.dateFrom as string) : new Date(2023, 5, 19),
    to: search_params.dateTo ? new Date(search_params.dateTo as string) : new Date(2023, 5, 24)
  };

  // Validate that dateRange values are valid dates
  const date_range_schema = z.object({
    from: z.date(),
    to: z.date()
  });

  const date_range = date_range_schema.safeParse(
    {
      from: selected_date_range.from,
      to: selected_date_range.to
    }
  );

  if (!date_range.success) {
    console.error(`Invalid date range: ${date_range.error}`);
    redirect(`/workspace/simulations/${model_id}`);
  }

  const chart_data : SimTimestep[] | undefined = await fetchPowerData(model_id, date_range.data);

  if (!chart_data) {
    return <div>Failed to load chart data</div>;
  }

  return (
    <Card
      className="flex flex-grow flex-col items-center justify-center w-full max-h-120"
      decoration="top"
      decorationColor="blue-300"
    >
      <BaseDateRangePicker date_range={date_range.data} />
      <BasePowerLineChart data={chart_data} />
    </Card>
  );
}
