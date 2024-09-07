import { fetchSimResults } from './actions';
import { SimResultsEval, DonutChartData } from '@/app/utils/definitions';
import { List, ListItem } from '@tremor/react';
import { BaseCard, BaseDonutChart } from '@/app/components/base-comps';

function classNames(...classes: string[]) {
    return classes.filter(Boolean).join(' ');
  }

const valueFormatter = (number: number) =>
    `${Math.round(number).toLocaleString()} kWh`;

const shareFormatter = (number: number) =>
    `${Math.round(number * 100).toString()}%`;


function getChartData(chart_type: string, sim_results_eval: SimResultsEval | null): DonutChartData {
    const chart_data: DonutChartData = {
        data: [ {name: '', value: 0, share: 0} ],
        labels: {center: 0, title: 0},
        title: ''
    }
    if (sim_results_eval) {
        switch (chart_type) {
            case 'consumption':
                chart_data.data=[
                {
                    name: 'From: PV',
                    value: sim_results_eval.energy_kpis.self_consumption,
                    share: sim_results_eval.energy_kpis.self_consumption/sim_results_eval.energy_kpis.annual_consumption
                },
                {
                    name: 'From: Grid',
                    value: sim_results_eval.energy_kpis.grid_consumption,
                    share: sim_results_eval.energy_kpis.grid_consumption/sim_results_eval.energy_kpis.annual_consumption
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
                    name: 'To: Self-consumption',
                    value: sim_results_eval.energy_kpis.self_consumption,
                    share: sim_results_eval.energy_kpis.self_consumption/sim_results_eval.energy_kpis.pv_generation
                },
                {
                    name: 'To: Grid Feed-in',
                    value: sim_results_eval.energy_kpis.grid_feed_in,
                    share: sim_results_eval.energy_kpis.grid_feed_in/sim_results_eval.energy_kpis.pv_generation
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
        return <div>Error: Simulation results not found.</div>;
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
        </BaseCard>
    );
}
