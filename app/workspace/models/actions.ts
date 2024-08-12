// Server Actions: https://nextjs.org/docs/app/building-your-application/data-fetching/server-actions-and-mutations

'use server';

import { ModelDataSchema, FormState, ModelData } from '@/utils/definitions';
import { getUser } from '@/utils/helpers';
import { User } from 'next-auth';
import { revalidatePath } from 'next/cache';

const loadBackendBaseUri = () => {
    // Load backend base URI
    const BACKEND_BASE_URI = process.env.BACKEND_BASE_URI;
    if (!BACKEND_BASE_URI) {
        console.error('BACKEND_BASE_URI is not defined');
        throw new Error('Backend base URI is not defined.');
    }
    return BACKEND_BASE_URI;
}

export async function submitModel(prevState: FormState, formData: FormData) {
    // When invoked in a form, the action automatically receives the FormData object.
    // You don't need to use React useState to manage fields, instead, you can extract
    // the data using the native FormData methods.

    let state: FormState = prevState;

    // Validate that formData has schema of ModelDataSchema
    const validatedFields = ModelDataSchema.safeParse(Object.fromEntries(formData));

    if (!validatedFields.success) {
        console.error(`Invalid form data: ${validatedFields.error}`);
        state = {
            errors: validatedFields.error.flatten().fieldErrors,
            message: 'Missing Fields. Failed to submit form.',
          };
        return state;
    }

    // Get the user ID
    const user: User | null = await getUser()
    const user_id = user?.id;
    if (!user || !user_id) {
        console.error('User is not defined');
        state = {
            errors: {},
            message: 'Failed to get user.',
          };
        return state;
    }

    // Set payload with user_id
    const payload = {
        ...validatedFields.data,
        user_id: user_id,
    };

    try {
        // Submit user input form with model parameters
        const BACKEND_BASE_URI = loadBackendBaseUri();
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
    const user: User | null = await getUser()
    const user_id = user?.id;
    if (!user || !user_id) {
        console.error('User is not defined');
        return null;
    }

    // Fetch models of user
    const BACKEND_BASE_URI = loadBackendBaseUri();
    const response_load_models = await fetch(`${BACKEND_BASE_URI}/workspace/models/fetch-models?user_id=${user_id}`);
    const models: ModelData[] = await response_load_models.json();

    console.log(`GET workspace/models/load-models: Models loaded (${response_load_models.status}).`);

    return models;
}
