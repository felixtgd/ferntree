import { fetchSimResults } from './actions';
import { SimResultsEval, PVMonthlyGen } from '@/app/utils/definitions';
import { BaseCard, BasePvBarChart } from '../../../components/base-comps';


export async function PvGenBarChart({model_id}: {model_id: string}) {

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

  const chart_data: PVMonthlyGen[] = sim_results_eval.pv_monthly_gen;

  return (
    <BaseCard title="Monthly PV Generation">
      <BasePvBarChart data={chart_data} />
    </BaseCard>
  );
}
