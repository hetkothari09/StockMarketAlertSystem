// src/config.js

// Using Vite's environment variables to determine the base URL.
// When deployed, ensure VITE_API_URL is set in your Render environment variables.
export const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:7000";
