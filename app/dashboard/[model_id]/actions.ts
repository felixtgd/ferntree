'use server';

import { DateRangePickerValue } from "@tremor/react";


const loadBackendBaseUri = () => {
    // Load backend base URI
    const BACKEND_BASE_URI = process.env.BACKEND_BASE_URI;
    if (!BACKEND_BASE_URI) {
        console.error('BACKEND_BASE_URI is not defined');
        throw new Error('Backend base URI is not defined.');
    }
    return BACKEND_BASE_URI;
}

export async function fetchSimResults(modelId: string) {
    try {
        // // Wait 3 seconds
        // await new Promise(resolve => setTimeout(resolve, 3000));

        const BACKEND_BASE_URI = loadBackendBaseUri();
        const simResults = await fetch(`${BACKEND_BASE_URI}/dashboard/simulation-results?model_id=${modelId}`).then((res) => res.json());;

        return simResults

    } catch (error) {
        console.error(`Failed to fetch simResults: ${error}`);
    }
};


export async function fetchPvMonthlyData(modelId: string) {
    try {
        // // Wait 3 seconds
        // await new Promise(resolve => setTimeout(resolve, 3000));

        const BACKEND_BASE_URI = loadBackendBaseUri();
        const pv_monthly_gen_data = await fetch(`${BACKEND_BASE_URI}/dashboard/pv-monthly-gen?model_id=${modelId}`).then((res) => res.json());;

        return pv_monthly_gen_data

    } catch (error) {
        console.error(`Failed to fetch simData: ${error}`);
    }
};


export async function fetchPowerData(modelId: string, dateRange: DateRangePickerValue) {
    try {
        const requestBody = {
        s_model_id: modelId,
        start_date: dateRange.from?.toISOString(),
        end_date: dateRange.to?.toISOString(),
        };

        // // Wait 3 seconds
        // await new Promise(resolve => setTimeout(resolve, 3000));

        const BACKEND_BASE_URI = loadBackendBaseUri();
        const response = await fetch(`${BACKEND_BASE_URI}/dashboard/sim-timeseries-data`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody),
        });
        const timeseries_data = await response.json();

        return timeseries_data;

    } catch (error) {
        console.error(`Power profiles: Failed to fetch data for date range ${dateRange}:`, error);
    }
};
