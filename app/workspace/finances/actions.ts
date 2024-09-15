// Server Actions: https://nextjs.org/docs/app/building-your-application/data-fetching/server-actions-and-mutations

'use server';

import { FormState, FinDataSchema } from '@/app/utils/definitions';
import { loadBackendBaseUri, getUserID } from '@/app/utils/helpers';
import { revalidatePath } from 'next/cache';
import { redirect } from 'next/navigation';


export async function submitFinances(prev_state: FormState, form_data: FormData) {
    // When invoked in a form, the action automatically receives the FormData object.
    // You don't need to use React useState to manage fields, instead, you can extract
    // the data using the native FormData methods.

    // Validate that formData has schema of ModelDataSchema
    const validated_fields = FinDataSchema.safeParse(Object.fromEntries(form_data));

    let state: FormState = prev_state;
    if (!validated_fields.success) {
        console.error(`Invalid form data: ${validated_fields.error}`);
        state = {
            errors: validated_fields.error.flatten().fieldErrors,
            message: 'Missing Fields. Failed to submit form.',
          };
        return state;
    }

    // Get the user ID
    const user_id = await getUserID();

    // Set payload with user_id
    const payload = {
        ...validated_fields.data,
        user_id: user_id,
    };

    try {
        // Submit user input form with model parameters
        const BACKEND_BASE_URI = await loadBackendBaseUri();
        const response_submit_fin_data = await fetch(`${BACKEND_BASE_URI}/workspace/finances/submit-fin-data?user_id=${user_id}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        const model_id: string = await response_submit_fin_data.json();

        console.log(`POST workspace/finances/submit-fin-data: Model form submitted (${response_submit_fin_data.status}). Model ID: ${model_id}`);
        state = {
            errors: {},
            message: 'success',
        };
        redirect(`/workspace/finances/${model_id}`);

    } catch (error) {
        console.error(`Failed to submit model form: ${error}`);
        state = {
            errors: {},
            message: 'Failed to submit form.',
        };
        revalidatePath('/workspace/finances');
        return state;
    }
};