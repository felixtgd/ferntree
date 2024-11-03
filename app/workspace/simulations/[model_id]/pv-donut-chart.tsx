import { fetchSimResults } from './actions';
import { SimResultsEval, DonutChartData } from '@/app/utils/definitions';
import { List, ListItem } from '@tremor/react';
import { BaseCard, BaseDonutChart } from '@/app/components/base-comps';
import { Tooltip } from '@/app/components/components';

function classNames(...classes: string[]) {
    return classes.filter(Boolean).join(' ');
  }

const valueFormatter = (number: number) =>
    `${Math.round(number).toLocaleString()} kWh`;

const shareFormatter = (number: number) =>
    `${Math.round(number * 100).toString()}%`;


function getChartData(chart_type: string, sim_results_eval: SimResultsEval | null): DonutChartData {
    const chart_data: DonutChartData = {
        data: [ {name: '', value: 0, share: 0, tooltip: ''} ],
        labels: {center: 0, title: 0},
        title: ''
    }
    if (sim_results_eval) {
        switch (chart_type) {
            case 'consumption':
                chart_data.data=[
                {
                    name: 'PV',
                    value: sim_results_eval.energy_kpis.self_consumption,
                    share: sim_results_eval.energy_kpis.annual_consumption !== 0
                        ? sim_results_eval.energy_kpis.self_consumption / sim_results_eval.energy_kpis.annual_consumption
                        : 0,
                    tooltip: 'Consumption covered by the PV generation (self-consumption)'
                },
                {
                    name: 'Grid',
                    value: sim_results_eval.energy_kpis.grid_consumption,
                    share: sim_results_eval.energy_kpis.annual_consumption !== 0
                        ? sim_results_eval.energy_kpis.grid_consumption / sim_results_eval.energy_kpis.annual_consumption
                        : 0,
                    tooltip: 'Consumption covered by electricity from the grid'
                },
                ]

                chart_data.labels={
                center: sim_results_eval.energy_kpis.self_sufficiency,
                title: sim_results_eval.energy_kpis.annual_consumption,
                }

                chart_data.title='Consumption'
                break;

            case 'generation':
                chart_data.data=[
                {
                    name: 'Self-cons.',
                    value: sim_results_eval.energy_kpis.self_consumption,
                    share: sim_results_eval.energy_kpis.pv_generation !== 0
                    ? sim_results_eval.energy_kpis.self_consumption/sim_results_eval.energy_kpis.pv_generation
                    : 0,
                    tooltip: 'PV generation directly consumed by the household (self-consumption)'
                },
                {
                    name: 'Grid feed-in',
                    value: sim_results_eval.energy_kpis.grid_feed_in,
                    share: sim_results_eval.energy_kpis.pv_generation !== 0
                    ? sim_results_eval.energy_kpis.grid_feed_in/sim_results_eval.energy_kpis.pv_generation
                    : 0,
                    tooltip: 'PV generation fed into the grid'
                },
                ]

                chart_data.labels={
                center: sim_results_eval.energy_kpis.self_consumption_rate,
                title: sim_results_eval.energy_kpis.pv_generation,
                }

                chart_data.title='PV Generation'
                break;
        }
    }
    return chart_data;
}

export async function PvDonutChart({chart_type, model_id}: {chart_type: string, model_id: string}) {

    const sim_results_eval: SimResultsEval | undefined = await fetchSimResults(model_id);

    if (!sim_results_eval) {
        return (
            <div>
                <BaseCard title="">
                    <div>
                        No results found. Run a simulation to get results.
                    </div>
                </BaseCard>
            </div>
        )
      }

    const {data, labels, title} = getChartData(chart_type, sim_results_eval);

    const colors = ['cyan', 'blue', 'indigo', 'violet', 'fuchsia'];

    const data_with_colors = data.map((item, index) => ({
        ...item,
        color: colors[index % colors.length],
    }));

    return (
        <BaseCard title={`${title}: ${valueFormatter(labels.title)} `}>
            <BaseDonutChart
                data={data_with_colors}
                label={shareFormatter(labels.center)}
                colors={data_with_colors.map((item) => item.color)}
            />
            <List className="mt-2">
                {data_with_colors.map((item) => (
                    <ListItem key={item.name} className="space-x-2">
                        <div className="flex items-center space-x-2 truncate">
                            <span
                                className={classNames(
                                    `bg-${item.color}-500`,
                                    'h-2.5 w-2.5 shrink-0 rounded-sm',
                                )}
                                aria-hidden={true}
                            />
                            <Tooltip content={item.tooltip}>
                                <span className="truncate dark:text-dark-tremor-content-emphasis" style={{ maxWidth: '100px' }}>
                                    {item.name}
                                </span>
                            </Tooltip>
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
        </BaseCard>
    );
}
