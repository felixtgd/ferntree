// Server Actions: https://nextjs.org/docs/app/building-your-application/data-fetching/server-actions-and-mutations

'use server';

import { FormState, FinDataSchema, FinData } from '@/app/utils/definitions';
import { loadBackendBaseUri, getUserID } from '@/app/utils/helpers';

export async function submitFinFormData(prev_state: FormState, form_data: FormData) {
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

    let model_id: string;
    try {
        // Submit user input form with model parameters
        const BACKEND_BASE_URI = await loadBackendBaseUri();
        const response_submit_fin_data = await fetch(`${BACKEND_BASE_URI}/workspace/finances/submit-fin-form-data?user_id=${user_id}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        model_id = await response_submit_fin_data.json();

        console.log(`POST workspace/finances/submit-fin-data: Fin form submitted (${response_submit_fin_data.status}). Model ID: ${model_id}`);
        state = {
            errors: {},
            message: 'success',
            model_id: model_id,
            timestamp: new Date().toISOString(),
        };
        return state;

    } catch (error) {
        console.error(`Failed to submit model form: ${error}`);
        state = {
            errors: {},
            message: 'Failed to submit form.',
        };
        return state;
    }

};


export async function fetchFinFormData() {

    // Get the user ID
    const user_id = await getUserID();

    // Fetch models of user
    const BACKEND_BASE_URI = await loadBackendBaseUri();
    const response_load_models = await fetch(`${BACKEND_BASE_URI}/workspace/finances/fetch-fin-form-data?user_id=${user_id}`);
    const fin_form_data_all: FinData[] = await response_load_models.json();

    console.log(`GET workspace/finances/fetch-fin-form-data: Fin form data fetched (${response_load_models.status}).`);

    return fin_form_data_all;
}
