'use server';

import { ModelData } from '@/utils/definitions';
import { loadBackendBaseUri, getUserID } from '@/utils/helpers';



export async function fetchModels() {

    // Get the user ID
    const user_id = await getUserID();

    // Fetch models of user
    const BACKEND_BASE_URI = await loadBackendBaseUri();
    const response_load_models = await fetch(`${BACKEND_BASE_URI}/workspace/models/fetch-models?user_id=${user_id}`);
    const models: ModelData[] = await response_load_models.json();

    console.log(`GET workspace/models/fetch-models: Models loaded (${response_load_models.status}).`);

    return models;
}
