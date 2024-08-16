// Server Actions: https://nextjs.org/docs/app/building-your-application/data-fetching/server-actions-and-mutations

'use server';

import { ModelDataSchema, FormState, ModelData } from '@/utils/definitions';
import { loadBackendBaseUri, getUserID } from '@/utils/helpers';
import { revalidatePath } from 'next/cache';


export async function submitModel(prevState: FormState, formData: FormData) {
    // When invoked in a form, the action automatically receives the FormData object.
    // You don't need to use React useState to manage fields, instead, you can extract
    // the data using the native FormData methods.

    // Validate that formData has schema of ModelDataSchema
    const validatedFields = ModelDataSchema.safeParse(Object.fromEntries(formData));

    let state: FormState = prevState;
    if (!validatedFields.success) {
        console.error(`Invalid form data: ${validatedFields.error}`);
        state = {
            errors: validatedFields.error.flatten().fieldErrors,
            message: 'Missing Fields. Failed to submit form.',
          };
        return state;
    }

    // Get the user ID
    const user_id = await getUserID();

    // Set payload with user_id
    const payload = {
        ...validatedFields.data,
        user_id: user_id,
    };

    try {
        // Submit user input form with model parameters
        const BACKEND_BASE_URI = await loadBackendBaseUri();
        const response_submit_model = await fetch(`${BACKEND_BASE_URI}/workspace/models/submit-model?user_id=${user_id}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        const model_id = await response_submit_model.json();

        console.log(`POST workspace/models/submit-model: Model form submitted (${response_submit_model.status}). Model ID: ${model_id}`);

    } catch (error) {
        console.error(`Failed to submit model form: ${error}`);
    }

    revalidatePath('/workspace/models');
    return state;

};

export async function fetchModels() {

    // Get the user ID
    const user_id = await getUserID();

    // Fetch models of user
    const BACKEND_BASE_URI = await loadBackendBaseUri();
    const response_load_models = await fetch(`${BACKEND_BASE_URI}/workspace/models/fetch-models?user_id=${user_id}`);
    const models: ModelData[] = await response_load_models.json();

    console.log(`GET workspace/models/load-models: Models loaded (${response_load_models.status}).`);

    return models;
}

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

export async function editModel(model_id: string) {
    // Placeholder for editing model
    console.log(`Edit model: ${model_id}`);
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
