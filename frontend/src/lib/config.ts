const isDevModeEnabled = import.meta.env.DEV_MODE_ENABLED === 'true';
export const API_BASE = isDevModeEnabled ? "http://localhost:8000/api" : "/api";
