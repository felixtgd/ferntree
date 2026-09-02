// API fetch wrappers — all calls go directly to FastAPI from the browser.
// user_id is always passed as a query parameter; never in the request body.

import { BACKEND_BASE_URI, USER_ID } from './config';
import type {
  CoordinateData,
  ModelData,
  SimResultsEval,
  SimTimestep,
  FinData,
  FinResults,
} from './types';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function apiUrl(path: string, params: Record<string, string> = {}): string {
  const url = new URL(BACKEND_BASE_URI + path);
  url.searchParams.set('user_id', USER_ID);
  for (const [k, v] of Object.entries(params)) {
    url.searchParams.set(k, v);
  }
  return url.toString();
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    throw new Error(`HTTP ${res.status} ${res.statusText}`);
  }
  return res.json() as Promise<T>;
}

// ---------------------------------------------------------------------------
// 1. GET /workspace/models/fetch-models
// ---------------------------------------------------------------------------
export async function fetchModels(): Promise<ModelData[]> {
  const res = await fetch(apiUrl('/workspace/models/fetch-models'));
  return handleResponse<ModelData[]>(res);
}

// ---------------------------------------------------------------------------
// 2. POST /workspace/models/submit-model
// Payload: ModelData fields + coordinates + time_created (no model_id / sim_id)
// Returns: model_id string
// ---------------------------------------------------------------------------
export async function submitModel(
  payload: Omit<ModelData, 'model_id' | 'sim_id'>,
): Promise<string> {
  const res = await fetch(apiUrl('/workspace/models/submit-model'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  return handleResponse<string>(res);
}

// ---------------------------------------------------------------------------
// 3. DELETE /workspace/models/delete-model
// Query params only — no request body.
// Returns: boolean (acknowledged)
// ---------------------------------------------------------------------------
export async function deleteModel(model_id: string): Promise<boolean> {
  const res = await fetch(apiUrl('/workspace/models/delete-model', { model_id }), {
    method: 'DELETE',
  });
  return handleResponse<boolean>(res);
}

// ---------------------------------------------------------------------------
// 4. GET /workspace/simulations/run-sim
// Returns: { run_successful: boolean }
// ---------------------------------------------------------------------------
export async function runSimulation(model_id: string): Promise<{ run_successful: boolean }> {
  const res = await fetch(apiUrl('/workspace/simulations/run-sim', { model_id }));
  return handleResponse<{ run_successful: boolean }>(res);
}

// ---------------------------------------------------------------------------
// 5. GET /workspace/simulations/fetch-sim-results
// ---------------------------------------------------------------------------
export async function fetchSimResults(model_id: string): Promise<SimResultsEval> {
  const res = await fetch(
    apiUrl('/workspace/simulations/fetch-sim-results', { model_id }),
  );
  return handleResponse<SimResultsEval>(res);
}

// ---------------------------------------------------------------------------
// 6. POST /workspace/simulations/fetch-sim-timeseries
// Body: { start_time: ISO string, end_time: ISO string }
// date_from / date_to are YYYY-MM-DD strings.
// ---------------------------------------------------------------------------
export async function fetchSimTimeseries(
  model_id: string,
  date_from: string,
  date_to: string,
): Promise<SimTimestep[]> {
  const body = {
    start_time: `${date_from}T00:00:00`,
    end_time: `${date_to}T23:59:59`,
  };
  const res = await fetch(
    apiUrl('/workspace/simulations/fetch-sim-timeseries', { model_id }),
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    },
  );
  return handleResponse<SimTimestep[]>(res);
}

// ---------------------------------------------------------------------------
// 7. GET /workspace/finances/fetch-fin-form-data
// ---------------------------------------------------------------------------
export async function fetchFinFormData(): Promise<FinData[]> {
  const res = await fetch(apiUrl('/workspace/finances/fetch-fin-form-data'));
  return handleResponse<FinData[]>(res);
}

// ---------------------------------------------------------------------------
// 8. POST /workspace/finances/submit-fin-form-data
// Returns: model_id string
// ---------------------------------------------------------------------------
export async function submitFinFormData(payload: FinData): Promise<string> {
  const res = await fetch(apiUrl('/workspace/finances/submit-fin-form-data'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  return handleResponse<string>(res);
}

// ---------------------------------------------------------------------------
// 9. GET /workspace/finances/fetch-fin-results
// ---------------------------------------------------------------------------
export async function fetchFinResults(model_id: string): Promise<FinResults> {
  const res = await fetch(
    apiUrl('/workspace/finances/fetch-fin-results', { model_id }),
  );
  return handleResponse<FinResults>(res);
}

// ---------------------------------------------------------------------------
// 10. Nominatim geocoding (called directly from the browser)
// Returns CoordinateData or null if no result / error.
// ---------------------------------------------------------------------------
export async function geocodeLocation(location: string): Promise<CoordinateData | null> {
  try {
    const url = `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(location)}&format=json&limit=1`;
    const res = await fetch(url, {
      headers: { 'User-Agent': 'ferntree-app/1.0' },
    });
    if (!res.ok) {
      throw new Error(`HTTP ${res.status}`);
    }
    const data = await res.json() as Array<{ lat: string; lon: string; display_name: string }>;
    if (!data.length) {
      return null;
    }
    return {
      lat: data[0].lat,
      lon: data[0].lon,
      display_name: data[0].display_name,
    };
  } catch (error) {
    console.error(`Nominatim geocoding failed for "${location}":`, error);
    return null;
  }
}
