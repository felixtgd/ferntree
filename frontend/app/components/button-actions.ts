"use server";

import { loadBackendBaseUri, getAnonymousUserId } from '@/app/utils/helpers';
import { revalidatePath } from 'next/cache';


export async function deleteModel(model_id: string) {

    // Get the user ID
    const user_id = getAnonymousUserId();

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
    const user_id = getAnonymousUserId();

    let run_successful: boolean;
    try {

        console.log(`GET workspace/simulations/run-sim: Started simulation of model ${model_id}.`);

        // Fetch models of user
        const BACKEND_BASE_URI = await loadBackendBaseUri();
        const res = await fetch(`${BACKEND_BASE_URI}/workspace/simulations/run-sim?user_id=${user_id}&model_id=${model_id}`);
        if (!res.ok) {
            throw new Error(`HTTP ${res.status}`);
        }
        const response_sim_run = await res.json();

        run_successful = response_sim_run.run_successful;

        console.log(`GET workspace/simulations/run-sim: Simulation finished, success: ${run_successful}.`);

    }
    catch (error) {
        console.error(`Failed to run simulation: ${error}`);
        run_successful = false;
    }

    revalidatePath('/workspace/simulations');

    return { success: run_successful, model_id };

}
