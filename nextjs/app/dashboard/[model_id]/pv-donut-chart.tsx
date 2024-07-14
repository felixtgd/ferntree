import { fetchSimResults } from './actions';
import { SimEvaluation, DonutChartData } from '@/app/lib/definitions';
import { Card, List, ListItem } from '@tremor/react';
import { BaseDonutChart } from './base-charts';

function classNames(...classes: string[]) {
    return classes.filter(Boolean).join(' ');
  }

const valueFormatter = (number: number) =>
    `${Math.round(number).toLocaleString()} kWh`;

const shareFormatter = (number: number) =>
    `${Math.round(number * 100).toString()}%`;


function getChartData(chartType: string, simResults: SimEvaluation|null): DonutChartData {
    const chartData: DonutChartData = {
        data: [ {name: '', value: 0, share: 0} ],
        labels: {center: 0, title: 0},
        title: ''
    }
    if (simResults) {
        switch (chartType) {
            case 'consumption':
                chartData.data=[
                {
                    name: 'PV',
                    value: simResults.energy_kpis.self_consumption,
                    share: simResults.energy_kpis.self_consumption/simResults.energy_kpis.baseload_demand
                },
                {
                    name: 'Grid',
                    value: simResults.energy_kpis.grid_consumption,
                    share: simResults.energy_kpis.grid_consumption/simResults.energy_kpis.baseload_demand
                },
                ]

                chartData.labels={
                center: simResults.energy_kpis.self_sufficiency,
                title: simResults.energy_kpis.baseload_demand,
                }

                chartData.title='Consumption'
                break;

            case 'generation':
                chartData.data=[
                {
                    name: 'Self-consumption',
                    value: simResults.energy_kpis.self_consumption,
                    share: simResults.energy_kpis.self_consumption/simResults.energy_kpis.pv_generation
                },
                {
                    name: 'Grid Feed-in',
                    value: simResults.energy_kpis.grid_feed_in,
                    share: simResults.energy_kpis.grid_feed_in/simResults.energy_kpis.pv_generation
                },
                ]

                chartData.labels={
                center: simResults.energy_kpis.self_consumption_rate,
                title: simResults.energy_kpis.pv_generation,
                }

                chartData.title='PV Generation'
                break;
        }
    }
    return chartData;
}

export async function PvDonutChart({chartType, modelId}: {chartType: string, modelId: string}) {

    const simResults : SimEvaluation = await fetchSimResults(modelId);

    const {data, labels, title} = getChartData(chartType, simResults);

    const colors = ['cyan', 'blue', 'indigo', 'violet', 'fuchsia'];

    const dataWithColors = data.map((item, index) => ({
        ...item,
        color: colors[index % colors.length],
    }));

    return (
        <>
            <Card
                className="sm:mx-auto sm:max-w-lg max-h-80"
                decoration="top"
                decorationColor="blue-300"
            >
                <h3 className="text-center text-tremor-content-strong dark:text-dark-tremor-content-strong font-medium mb-4">
                    {`${title}: ${valueFormatter(labels.title)} `}
                </h3>
                <BaseDonutChart
                    data={dataWithColors}
                    label={shareFormatter(labels.center)}
                    colors={dataWithColors.map((item) => item.color)}
                />
                <List className="mt-2">
                    {dataWithColors.map((item) => (
                        <ListItem key={item.name} className="space-x-6">
                            <div className="flex items-center space-x-2.5 truncate">
                                <span
                                    className={classNames(
                                        `bg-${item.color}-500`,
                                        'h-2.5 w-2.5 shrink-0 rounded-sm',
                                    )}
                                    aria-hidden={true}
                                />
                                <span className="truncate dark:text-dark-tremor-content-emphasis">
                                    {item.name}
                                </span>
                            </div>
                            <div className="flex items-center space-x-2">
                                <span className="font-medium tabular-nums text-tremor-content-strong dark:text-dark-tremor-content-strong">
                                    {valueFormatter(item.value)}
                                </span>
                                <span className="rounded-tremor-small bg-tremor-background-subtle px-1.5 py-0.5 text-tremor-label font-medium tabular-nums text-tremor-content-emphasis dark:bg-dark-tremor-background-subtle dark:text-dark-tremor-content-emphasis">
                                    {shareFormatter(item.share)}
                                </span>
                            </div>
                        </ListItem>
                    ))}
                </List>
            </Card>
        </>
    );
}
