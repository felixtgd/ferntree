'use server';

import { FinResults } from "@/app/utils/definitions";
import { getUserID, loadBackendBaseUri } from '@/app/utils/helpers';


export async function fetchFinResults(model_id: string) {

    // Get the user ID
    const user_id = await getUserID();

    try {
        const BACKEND_BASE_URI = await loadBackendBaseUri();
        const fin_results: FinResults = await fetch(`${BACKEND_BASE_URI}/workspace/finances/fetch-fin-results?user_id=${user_id}&model_id=${model_id}`).then((res) => res.json());;
        return fin_results
    } catch (error) {
        console.error(`Failed to fetch simResults: ${error}`);
    }
};
