'use server';

import { DateRangePickerValue } from "@tremor/react";

// import { revalidatePath } from "next/cache";

// export async function runSimulation(modelId: string) {
//     try {
//         const response_sim_run = await fetch(`http://localhost:8000/dashboard/run-simulation?model_id=${modelId}`).then((res) => res.json());
//         if (response_sim_run.sim_run_success) {
//             console.log(`Simulation run successful for model ID: ${modelId}`);
//         } else {
//             console.error(`Simulation run failed for model ID: ${modelId}`);
//             return null;
//         }

//     } catch (error) {
//         console.error(`Failed to fetch simResults: ${error}`);
//     }
// };

export async function fetchSimResults(modelId: string) {
    try {
        // const response_sim_run = await fetch(`http://localhost:8000/dashboard/run-simulation?model_id=${modelId}`).then((res) => res.json());
        // if (response_sim_run.sim_run_success) {
        //     console.log(`Simulation run successful for model ID: ${modelId}`);
        // } else {
        //     console.error(`Simulation run failed for model ID: ${modelId}`);
        //     return null;
        // }

        // // Wait 3 seconds
        // await new Promise(resolve => setTimeout(resolve, 3000));

        const simResults = await fetch(`http://localhost:8000/dashboard/simulation-results?model_id=${modelId}`).then((res) => res.json());;

        // revalidatePath(`/dashboard/${modelId}`);
        return simResults

    } catch (error) {
        console.error(`Failed to fetch simResults: ${error}`);
    }
};


export async function fetchPvMonthlyData(modelId: string) {
    try {
        // const response_sim_run = await fetch(`http://localhost:8000/dashboard/run-simulation?model_id=${modelId}`).then((res) => res.json());
        // if (response_sim_run.sim_run_success) {
        //     console.log(`Simulation run successful for model ID: ${modelId}`);
        // } else {
        //     console.error(`Simulation run failed for model ID: ${modelId}`);
        // }

        // // Wait 3 seconds
        // await new Promise(resolve => setTimeout(resolve, 3000));

        const pv_monthly_gen_data = await fetch(`http://localhost:8000/dashboard/pv-monthly-gen?model_id=${modelId}`).then((res) => res.json());;

        return pv_monthly_gen_data

    } catch (error) {
        console.error(`Failed to fetch simData: ${error}`);
    }

    // revalidatePath(`/dashboard/${modelId}`);
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

    const response = await fetch('http://localhost:8000/dashboard/sim-timeseries-data', {
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
