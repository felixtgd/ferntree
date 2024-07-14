'use client';

import { FinBarChartItem, PowerTimeseriesItem, PVMonthlyGenData } from '@/app/lib/definitions';
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
} from '@tremor/react';


const kWhFormatter: ValueFormatter = (number: number) =>
    `${Math.round(number).toLocaleString()} kWh`;

const moneyFormatter = (number: number) =>
    `€ ${Math.round(number).toLocaleString()}`;

const kWFormatter2d: ValueFormatter = (number: number) =>
    `${number.toFixed(2)} kW`;

const kWhFormatter2d: ValueFormatter = (number: number) =>
    `${number.toFixed(2)} kWh`;



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

export function BaseDateRangePicker({ dateRange } : { dateRange: DateRangePickerValue }) {

    const [selectedDateRange, setSelectedDateRange] = useState<DateRangePickerValue>(dateRange);

    const router = useRouter();

    function updateSearchParams(selectedDateRange: DateRangePickerValue ) {
        setSelectedDateRange(selectedDateRange)
        const urlSearchParams = new URLSearchParams({
            dateFrom: selectedDateRange.from?.toISOString() ?? '',
            dateTo: selectedDateRange.to?.toISOString() ?? '',
        });
        router.replace(`?${urlSearchParams.toString()}`, { scroll: false });
        router.refresh();
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

export function BaseLineChart({ data } : { data: PowerTimeseriesItem[]; }) {
    return (
        <>
        <h3 className="text-center text-tremor-content-strong dark:text-dark-tremor-content-strong font-medium mt-2">Power Profiles</h3>
        <LineChart
          className="max-h-64"
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
      <h3 className="text-center text-tremor-content-strong dark:text-dark-tremor-content-strong font-medium mt-2">Battery State of Charge</h3>
      <LineChart
          className="max-h-32"
          data={data}
          index="time"
          categories={['StateOfCharge']}
          colors={['teal']}
          valueFormatter={kWhFormatter2d}
          yAxisWidth={80}
          showAnimation={true}
          startEndOnly={true}
          showLegend={false}
          showXAxis={false}
      />
      </>
    )
}
