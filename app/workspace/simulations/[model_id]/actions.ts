'use server';

import { SimResultsEval } from "@/app/utils/definitions";
import { DateRangePickerValue } from "@tremor/react";
import { getUserID, loadBackendBaseUri } from '@/app/utils/helpers';


export async function fetchSimResults(model_id: string) {

    // Get the user ID
    const user_id = await getUserID();

    try {
        const BACKEND_BASE_URI = await loadBackendBaseUri();
        const sim_results_eval: SimResultsEval = await fetch(`${BACKEND_BASE_URI}/workspace/simulations/fetch-sim-results?user_id=${user_id}&model_id=${model_id}`).then((res) => res.json());;
        return sim_results_eval
    } catch (error) {
        console.error(`Failed to fetch simResults: ${error}`);
    }
};


// export async function fetchModelSummary(modelId: string) {
//     try {
//         const modelSummary = await fetch(`${BACKEND_BASE_URI}/dashboard/model-summary?model_id=${modelId}`).then((res) => res.json());;
//         return modelSummary
//     } catch (error) {
//         console.error(`Failed to fetch modelSummary: ${error}`);
//     }
// };


// export async function fetchPvMonthlyData(modelId: string) {
//     try {
//         const BACKEND_BASE_URI = await loadBackendBaseUri();
//         const pv_monthly_gen_data = await fetch(`${BACKEND_BASE_URI}/dashboard/pv-monthly-gen?model_id=${modelId}`).then((res) => res.json());;
//         return pv_monthly_gen_data
//     } catch (error) {
//         console.error(`Failed to fetch simData: ${error}`);
//     }
// };


export async function fetchPowerData(model_id: string, date_range: DateRangePickerValue) {
    try {
        const request_body = {
        model_id: model_id,
        start_date: date_range.from?.toISOString(),
        end_date: date_range.to?.toISOString(),
        };

        const BACKEND_BASE_URI = await loadBackendBaseUri();
        const response = await fetch(`${BACKEND_BASE_URI}/dashboard/sim-timeseries-data`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(request_body),
        });

        const timeseries_data = await response.json();
        return timeseries_data;

    } catch (error) {
        console.error(`Power profiles: Failed to fetch data for date range ${date_range}:`, error);
    }
};
