/** When true, the UI still refuses invented scores. Metrics come only from a real evaluation file. */
export const USE_MOCKS = import.meta.env.VITE_USE_MOCKS !== "false";

export const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

export const APP_NAME = "Image Forgery Check";
