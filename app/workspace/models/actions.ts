// Server Actions: https://nextjs.org/docs/app/building-your-application/data-fetching/server-actions-and-mutations

'use server';

import { ModelDataSchema, FormState } from '@/app/utils/definitions';
import { loadBackendBaseUri, getUserID } from '@/app/utils/helpers';
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
        state = {
            errors: {},
            message: 'success',
        };

    } catch (error) {
        console.error(`Failed to submit model form: ${error}`);
        state = {
            errors: {},
            message: 'Failed to submit form.',
        };
    }

    revalidatePath('/workspace/models');
    return state;

};
