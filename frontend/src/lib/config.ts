// // Use the machine's Tailscale hostname for API calls
// export const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

import { env } from '$env/dynamic/public';
export const API_BASE = env.PUBLIC_API_BASE || 'http://localhost:8000';
