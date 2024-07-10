'use server';

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

        // Wait 2 seconds
        await new Promise(resolve => setTimeout(resolve, 2000));

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

    const pv_monthly_gen_data = await fetch(`http://localhost:8000/dashboard/pv-monthly-gen?model_id=${modelId}`).then((res) => res.json());;

    return pv_monthly_gen_data

    } catch (error) {
        console.error(`Failed to fetch simData: ${error}`);
    }

    // revalidatePath(`/dashboard/${modelId}`);
};
