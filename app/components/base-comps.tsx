'use client';

import { FinBarChartItem, FinChartData, PVMonthlyGen, SimTimestep } from '@/app/utils/definitions';
import { useRouter } from 'next/navigation';
import { useState } from 'react'
import { enGB } from 'date-fns/locale';
import {
    ValueFormatter,
    DonutChart,
    BarChart,
    DateRangePicker,
    DateRangePickerValue,
    DateRangePickerItem,
    LineChart,
    Card,
} from '@tremor/react';


const kWhFormatter: ValueFormatter = (number: number) =>
    `${Math.round(number).toLocaleString()} kWh`;

const moneyFormatter = (number: number) =>
    `€ ${Math.round(number).toLocaleString()}`;

const kWFormatter2d: ValueFormatter = (number: number) =>
    `${number.toFixed(2)} kW`;

// const kWhFormatter2d: ValueFormatter = (number: number) =>
//     `${number.toFixed(2)} kWh`;

const percentFormatter: ValueFormatter = (number: number) =>
    `${Math.round(number).toString()}%`;


export function BaseCard({ title, children } : { title: string, children: React.ReactNode }) {
    return (
        <Card
            className="flex flex-grow flex-col items-center justify-center w-full h-full max-h-80"
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
            yAxisWidth={70}
            showLegend={false}
            showAnimation={true}
            stack={true}
        />
    );
}

export function BaseDateRangePicker({ date_range } : { date_range: DateRangePickerValue }) {

    const [selectedDateRange, setSelectedDateRange] = useState<DateRangePickerValue>(date_range);

    const router = useRouter();

    function updateSearchParams(selectedDateRange: DateRangePickerValue ) {
        setSelectedDateRange(selectedDateRange)
        const urlSearchParams = new URLSearchParams({
            dateFrom: selectedDateRange.from?.toISOString() ?? '',
            dateTo: selectedDateRange.to?.toISOString() ?? '',
        });
        router.replace(`?${urlSearchParams.toString()}`, { scroll: false });
    }

    return (
        <>
        <DateRangePicker
            className="mx-auto max-w-md"
            value={selectedDateRange}
            onValueChange={updateSearchParams}
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
        </>
    );
}

export function BasePowerLineChart({ data } : { data: SimTimestep[]; }) {
    return (
        <>
            <h3 className="text-center text-tremor-content-strong dark:text-dark-tremor-content-strong font-medium m-4">
                Power Profiles
            </h3>
            <LineChart
                className="h-[50%] w-full"
                data={data}
                index="time"
                categories={['Load', 'PV', 'Battery', 'Total']}
                colors={['rose', 'amber', 'teal', 'indigo']}
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


export function BaseFinLineChart({ data } : { data: FinChartData[]; }) {
        return (
        <>
            <h3 className="text-center text-tremor-content-strong dark:text-dark-tremor-content-strong font-medium m-4">
                Financial Performance
            </h3>
            <LineChart
                className="w-full"
                data={data}
                index="Year"
                categories={['Cum. Profit', 'Investment', 'Cum. Cash Flow', 'Loan']}
                colors={['green-600', 'red-500', 'blue-500', 'amber']}
                valueFormatter={moneyFormatter}
                yAxisWidth={80}
                showAnimation={true}
                startEndOnly={false}
                showXAxis={true}
            />
        </>
    )
}
