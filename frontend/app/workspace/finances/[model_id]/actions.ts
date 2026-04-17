'use server';

import { FinResults } from "@/app/utils/definitions";
import { getAnonymousUserId, loadBackendBaseUri } from '@/app/utils/helpers';


export async function fetchFinResults(model_id: string) {

    // Get the user ID
    const user_id = getAnonymousUserId();

    try {
        const BACKEND_BASE_URI = await loadBackendBaseUri();
        const response = await fetch(`${BACKEND_BASE_URI}/workspace/finances/fetch-fin-results?user_id=${user_id}&model_id=${model_id}`);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        const fin_results: FinResults = await response.json();
        return fin_results
    } catch (error) {
        console.error(`Failed to fetch finResults: ${error}`);
    }
};
