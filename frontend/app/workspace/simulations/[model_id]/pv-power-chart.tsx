'use client';

import { useState } from 'react';
import { Card } from '@tremor/react';
import { fetchPowerData } from './actions';
import { BaseCard, BaseDateRangePicker, BasePowerLineChart } from '@/app/components/base-comps';
import { SimTimestep } from '@/app/utils/definitions';

const DEFAULT_FROM = '2023-06-19';
const DEFAULT_TO = '2023-06-24';

export function PvPowerChart({ model_id, initial_data }:
    { model_id: string; initial_data: SimTimestep[] | undefined }
) {
    const [dateFrom, setDateFrom] = useState(DEFAULT_FROM);
    const [dateTo, setDateTo] = useState(DEFAULT_TO);
    const [chartData, setChartData] = useState<SimTimestep[] | undefined>(initial_data);

    const handleDateRangeChange = async (from: string, to: string) => {
        setDateFrom(from);
        setDateTo(to);
        const data = await fetchPowerData(model_id, from, to);
        setChartData(data);
    };

    if (!chartData) {
        return (
            <div className="w-1/3">
                <BaseCard title="">
                    <div>
                        No results found. Run a simulation to get results.
                    </div>
                </BaseCard>
            </div>
        );
    }

    return (
        <Card
            className="flex flex-grow flex-col items-center justify-center w-full max-h-90"
            decoration="top"
            decorationColor="blue-300"
        >
            <BaseDateRangePicker
                dateFrom={dateFrom}
                dateTo={dateTo}
                onDateRangeChange={handleDateRangeChange}
            />
            <BasePowerLineChart data={chartData} />
        </Card>
    );
}
