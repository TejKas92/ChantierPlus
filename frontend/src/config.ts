// Automatically use the same host as the frontend, but port 8000 for API
const API_URL = import.meta.env.VITE_API_URL || `${window.location.protocol}//${window.location.hostname}:8000`;

export const API_BASE_URL = API_URL;
export default API_URL;
