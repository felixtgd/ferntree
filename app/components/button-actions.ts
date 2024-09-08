"use server";

import { loadBackendBaseUri, getUserID } from '@/app/utils/helpers';
import { revalidatePath } from 'next/cache';
import { redirect } from 'next/navigation'


export async function deleteModel(model_id: string) {

    // Get the user ID
    const user_id = await getUserID();

    try {
        // Delete model
        const BACKEND_BASE_URI = await loadBackendBaseUri();
        const response_delete_model = await fetch(`${BACKEND_BASE_URI}/workspace/models/delete-model?user_id=${user_id}&model_id=${model_id}`, {
            method: 'DELETE',
        });

        const delete_result_acknowledged: boolean = await response_delete_model.json();
        if (!delete_result_acknowledged) {
            throw new Error(`Failed to delete model: ${model_id}`);
        }

        console.log(`DELETE workspace/models/delete-model: Model deleted (${response_delete_model.status}). Model ID: ${model_id}`);

    } catch (error) {
        console.error(`Failed to delete model: ${error}`);
    }

    revalidatePath('/workspace/models');
}


export async function runSimulation(model_id: string) {

    // Get the user ID
    const user_id = await getUserID();

    let run_successful: boolean;
    try {

        console.log(`GET workspace/simulations/run-sim: Started simulation of model ${model_id}.`);

        // Fetch models of user
        const BACKEND_BASE_URI = await loadBackendBaseUri();
        const response_sim_run = await fetch(`${BACKEND_BASE_URI}/workspace/simulations/run-sim?user_id=${user_id}&model_id=${model_id}`).then((res) => res.json());

        run_successful = response_sim_run.run_successful;

        console.log(`GET workspace/simulations/run-sim: Simulation finished, success: ${run_successful}.`);

    }
    catch (error) {
        console.error(`Failed to run simulation: ${error}`);
        run_successful = false;
    }

    if (run_successful) {
        redirect(`/workspace/simulations/${model_id}`);
    }
    else {
        revalidatePath('/workspace/simulations');
    }

}


export async function viewResults(model_id: string) {
    console.info(`View results for model: ${model_id}`);
    redirect(`/workspace/simulations/${model_id}`);
}

// not used right now, maybe in the future
export async function editModel(model_id: string) {
    // Placeholder for editing model
    console.log(`Edit model: ${model_id}`);
    revalidatePath('/workspace/models');
}
