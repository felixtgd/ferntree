'use server'

import { ModelData } from "@/app/utils/definitions"
import { cache } from "react";

// Fixed user ID used for all backend requests in the auth-free MVP.
// Replace with real session-based identity when authentication is re-introduced.
const ANONYMOUS_USER_ID = 'mvp-user';

export async function getAnonymousUserId(): Promise<string> {
    return ANONYMOUS_USER_ID;
}

export async function loadBackendBaseUri() {
    const BACKEND_BASE_URI = process.env.BACKEND_BASE_URI;
    if (!BACKEND_BASE_URI) {
        throw new Error('Backend base URI is not defined.');
    }
    return BACKEND_BASE_URI;
}

export const fetchModels = cache(async (): Promise<ModelData[]> => {

    const user_id = await getAnonymousUserId();

    const BACKEND_BASE_URI = await loadBackendBaseUri();
    const response_load_models = await fetch(`${BACKEND_BASE_URI}/workspace/models/fetch-models?user_id=${user_id}`);
    const models: ModelData[] = await response_load_models.json();

    console.log(`GET workspace/models/fetch-models: Models loaded (${response_load_models.status}).`);

    return models;
})
