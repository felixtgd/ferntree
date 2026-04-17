'use server';

import { SimResultsEval, SimTimestep } from "@/app/utils/definitions";
import { getAnonymousUserId, loadBackendBaseUri } from '@/app/utils/helpers';
import { cache } from "react";


// cache() deduplicates fetches within a single server render pass (per-request scope).
export const fetchSimResults = cache(async (model_id: string): Promise<SimResultsEval | undefined> => {

    // Get the user ID
    const user_id = getAnonymousUserId();

    try {
        const BACKEND_BASE_URI = await loadBackendBaseUri();
        const response = await fetch(`${BACKEND_BASE_URI}/workspace/simulations/fetch-sim-results?user_id=${user_id}&model_id=${model_id}`);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        const sim_results_eval: SimResultsEval = await response.json();
        return sim_results_eval
    } catch (error) {
        console.error(`Failed to fetch simResults: ${error}`);
        return undefined
    }
});


export async function fetchPowerData(model_id: string, date_from: string, date_to: string) {

    // Get the user ID
    const user_id = getAnonymousUserId();

    try {
        const request_body = {
            start_time: new Date(date_from).toISOString(),
            end_time: new Date(date_to).toISOString(),
        };

        console.log(`POST /workspace/simulations/fetch-sim-timeseries: From ${request_body.start_time} to ${request_body.end_time}`);

        const BACKEND_BASE_URI = await loadBackendBaseUri();
        const response = await fetch(`${BACKEND_BASE_URI}/workspace/simulations/fetch-sim-timeseries?user_id=${user_id}&model_id=${model_id}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(request_body),
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        const timeseries_data: SimTimestep[] = await response.json();
        console.log(`POST /workspace/simulations/fetch-sim-timeseries: Number of data points: ${timeseries_data.length}`);

        return timeseries_data;

    } catch (error) {
        console.error(`Power profiles: Failed to fetch data for date range ${date_from} - ${date_to}:`, error);
        return [];
    }
};
