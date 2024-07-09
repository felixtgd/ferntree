'use server';

// import { revalidatePath } from "next/cache";


export async function fetchSimData(modelId: string) {
    try {
        const response_sim_run = await fetch(`http://localhost:8000/dashboard/run-simulation?model_id=${modelId}`).then((res) => res.json());
        if (response_sim_run.sim_run_success) {
            console.log(`Simulation run successful for model ID: ${modelId}`);
        } else {
            console.error(`Simulation run failed for model ID: ${modelId}`);
        }

        const response_sim_results = await fetch(`http://localhost:8000/dashboard/simulation-results?model_id=${modelId}`);
        const simData = await response_sim_results.json();
        return simData

    } catch (error) {
        console.error(`Failed to fetch simData: ${error}`);
    }

    // revalidatePath(`/dashboard/${modelId}`);

};
