'use client';

import { FinBarChartItem, PVMonthlyGenData } from '@/app/lib/definitions';
import { DonutChart, ValueFormatter, BarChart } from '@tremor/react';


const kWhFormatter: ValueFormatter = (number: number) =>
    `${Math.round(number).toLocaleString()} kWh`;

const moneyFormatter = (number: number) =>
    `€ ${Math.round(number).toLocaleString()}`;


export function BaseDonutChart( { data, label, colors }:
    { data: { name: string; value: number; share: number; }[];
    label: string;
    colors: string[];
} ) {
    return (
        <DonutChart
            data={data}
            category="value"
            index="name"
            label={label}
            valueFormatter={kWhFormatter}
            colors={colors}
        />
    );
}

export function BasePvBarChart( { data }: { data: PVMonthlyGenData[]; } ) {
    return (
        <BarChart
            className="mt-2 max-h-60"
            data={data}
            index="month"
            categories={['PVGeneration']}
            colors={['amber']}
            valueFormatter={kWhFormatter}
            yAxisWidth={85}
            showLegend={false}
            showAnimation={true}
        />
    );
}

export function BaseFinBarChart( { data }: { data: FinBarChartItem[]; } ) {
    return (
        <BarChart
            className="mt-2 max-h-40"
            data={ data }
            index="type"
            categories={['Cost savings', 'Feed-in revenue', 'Operation costs', 'PV', 'Battery']}
            colors={['blue', 'cyan', 'purple', 'emerald', 'lime']}
            valueFormatter={moneyFormatter}
            yAxisWidth={70}
            showLegend={false}
            showAnimation={true}
            stack={true}
        />
    );
}
