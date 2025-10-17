export const DEV_MODE_ENABLED = import.meta.env.DEV;
export const API_BASE = DEV_MODE_ENABLED ? "http://localhost:8000/api" : "/api";
