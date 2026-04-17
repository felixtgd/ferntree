'use client';

import { FinBarChartItem, FinChartData, PVMonthlyGen, SimTimestep } from '@/app/utils/definitions';
import {
    ValueFormatter,
    DonutChart,
    BarChart,
    LineChart,
    Card,
} from '@tremor/react';


const kWhFormatter: ValueFormatter = (number: number) =>
    `${Math.round(number).toLocaleString()} kWh`;

export const moneyFormatter = (number: number) =>
    `€ ${Math.round(number).toLocaleString()}`;

const kWFormatter2d: ValueFormatter = (number: number) =>
    `${number.toFixed(2)} kW`;

const percentFormatter: ValueFormatter = (number: number) =>
    `${Math.round(number).toString()}%`;


export function BaseCard({ title, children } : { title: string, children: React.ReactNode }) {
    return (
        <Card
            className="flex flex-grow flex-col items-center justify-center w-full h-full max-h-96"
            decoration="top"
            decorationColor="blue-300"
        >
            <h3 className="text-center text-tremor-content-strong dark:text-dark-tremor-content-strong font-medium mb-4">
                { title }
            </h3>
        { children }
        </Card>
    )
}

export function BaseDonutChart( { data, label, colors }:
    { data: { name: string; value: number; share: number; }[];
    label: string;
    colors: string[];
} ) {
    return (
        <DonutChart
            className="mt-2"
            data={data}
            category="value"
            index="name"
            label={label}
            valueFormatter={kWhFormatter}
            colors={colors}
        />
    );
}

export function BasePvBarChart( { data }: { data: PVMonthlyGen[]; } ) {
    return (
        <BarChart
            className="mt-2 h-[90%]"
            data={data}
            index="month"
            categories={['pv_generation']}
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
            className="mt-2 h-[90%]"
            data={ data }
            index="type"
            categories={[ 'Operation costs', 'Feed-in revenue', 'Cost savings', 'PV', 'Battery']}
            colors={['green-600', 'green-500', 'green-400', 'red-700', 'red-500']}
            valueFormatter={moneyFormatter}
            yAxisWidth={90}
            showLegend={false}
            showAnimation={true}
            stack={true}
        />
    );
}

export function BaseDateRangePicker(
    { dateFrom, dateTo, onDateRangeChange }:
    {
        dateFrom: string;
        dateTo: string;
        onDateRangeChange: (from: string, to: string) => void;
    }
) {
    return (
        <div className="flex items-center gap-2 mx-auto mb-2">
            <label className="text-sm font-medium">From</label>
            <input
                type="date"
                className="border border-gray-300 rounded px-2 py-1 text-sm"
                value={dateFrom}
                onChange={(e) => onDateRangeChange(e.target.value, dateTo)}
            />
            <label className="text-sm font-medium">To</label>
            <input
                type="date"
                className="border border-gray-300 rounded px-2 py-1 text-sm"
                value={dateTo}
                onChange={(e) => onDateRangeChange(dateFrom, e.target.value)}
            />
        </div>
    );
}

export function BasePowerLineChart({ data } : { data: SimTimestep[]; }) {

    const categories = ['Load', 'PV', 'Battery', 'Total'];
    const colors = ['rose', 'amber', 'teal', 'indigo'];

    return (
        <>
            <h3 className="text-center text-tremor-content-strong dark:text-dark-tremor-content-strong font-medium m-4">
                Power Profiles
            </h3>
            <LineChart
                className="h-[50%] w-full"
                data={data}
                index="time"
                categories={categories}
                colors={colors}
                valueFormatter={kWFormatter2d}
                yAxisWidth={80}
                showAnimation={true}
                startEndOnly={true}
                showXAxis={false}
            />
            <h3 className="text-center text-tremor-content-strong dark:text-dark-tremor-content-strong font-medium m-4">
                Battery State of Charge
            </h3>
            <LineChart
                className="h-[25%] w-full"
                data={data}
                index="time"
                categories={['StateOfCharge']}
                colors={['teal']}
                valueFormatter={percentFormatter}
                yAxisWidth={80}
                showAnimation={true}
                startEndOnly={true}
                showLegend={false}
                showXAxis={true}
                minValue={0}
                maxValue={100}
            />
        </>
    )
}


export function BaseFinLineChart({ data }: { data: FinChartData[] }) {

    const categories = ['Cum. Profit', 'Investment', 'Cum. Cash Flow', 'Loan'];
    const colors = ['green-600', 'red-500', 'blue-500', 'orange-500'];

    return (
        <>
            <h3 className="text-center text-tremor-content-strong dark:text-dark-tremor-content-strong font-medium mb-4">
                Financial Performance
            </h3>
            <LineChart
                className="w-full h-[90%]"
                data={data}
                index="Year"
                categories={categories}
                colors={colors}
                valueFormatter={moneyFormatter}
                yAxisWidth={80}
                showAnimation={true}
                startEndOnly={false}
                showXAxis={true}
            />
        </>
    );
}
