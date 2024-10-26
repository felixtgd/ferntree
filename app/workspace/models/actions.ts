// Server Actions: https://nextjs.org/docs/app/building-your-application/data-fetching/server-actions-and-mutations

'use server';

import { ModelDataSchema, FormState, CoordinateData } from '@/app/utils/definitions';
import { loadBackendBaseUri, getUserID } from '@/app/utils/helpers';
import { revalidatePath } from 'next/cache';


async function getLocationCoordinates(location: string) {

    try {
        const response_nominatim = await fetch(`https://nominatim.openstreetmap.org/search?q=${location}&format=json&limit=1`);
        const data = await response_nominatim.json();

        const coordinates: CoordinateData = {
            lat: data[0].lat,
            lon: data[0].lon,
            display_name: data[0].display_name,
        };

        console.log(`GET nominatim (${response_nominatim.status}): Coordinates retrieved for location ${location}: ${coordinates}`);
        return coordinates;
    }
    catch (error) {
        console.error(`Failed to retrieve coordinates for location ${location}: ${error}`);
        return null;
    }
}

export async function submitModel(prev_state: FormState, form_data: FormData) {
    // When invoked in a form, the action automatically receives the FormData object.
    // You don't need to use React useState to manage fields, instead, you can extract
    // the data using the native FormData methods.

    // Validate that formData has schema of ModelDataSchema
    const validated_fields = ModelDataSchema.safeParse(Object.fromEntries(form_data));

    let state: FormState = prev_state;
    if (!validated_fields.success) {
        console.error(`Invalid form data: ${validated_fields.error}`);
        state = {
            errors: validated_fields.error.flatten().fieldErrors,
            message: 'Missing Fields. Failed to submit form.',
          };
        return state;
    }

    // Get the location coordinates
    const location: string = validated_fields.data.location;
    const coordinates: CoordinateData | null = await getLocationCoordinates(location);
    if (coordinates === null) {
        console.error(`Failed to retrieve location coordinates for ${location}`);
        state = {
            errors: {},
            message: 'Failed to retrieve location coordinates.',
        };
        return state;
    }

    // Get the user ID
    const user_id = await getUserID();

    // Set time_created timestamp
    const timestamp: string = new Date().toISOString();

    // Set payload with user_id
    const payload = {
        ...validated_fields.data,
        user_id: user_id,
        coordinates: coordinates,
        time_created: timestamp,
    };

    try {
        // Submit user input form with model parameters
        const BACKEND_BASE_URI = await loadBackendBaseUri();
        const response_submit_model = await fetch(`${BACKEND_BASE_URI}/workspace/models/submit-model?user_id=${user_id}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        const model_id: string = await response_submit_model.json();

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
