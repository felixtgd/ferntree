"use server";

import { loadBackendBaseUri, getUserID } from '@/app/utils/helpers';
import { revalidatePath } from 'next/cache';


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
    // Placeholder for running simulation
    console.log(`Run simulation: ${model_id}`);
    revalidatePath('/workspace/models');
}

export async function viewResults(model_id: string) {
    // Placeholder for viewing results
    console.log(`View results: ${model_id}`);
    revalidatePath('/workspace/models');
}

// not used right now, maybe in the future
export async function editModel(model_id: string) {
    // Placeholder for editing model
    console.log(`Edit model: ${model_id}`);
    revalidatePath('/workspace/models');
}