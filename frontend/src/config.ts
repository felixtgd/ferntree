// Backend base URL and shared constants
export const BACKEND_BASE_URI =
  (import.meta.env.VITE_BACKEND_BASE_URI as string | undefined) ?? 'http://localhost:8000';

export const USER_ID = 'mvp-user';
