import { API_BASE_URL } from '../config';

export const fetchActiveAlerts = async () => {
    const res = await fetch(`${API_BASE_URL}/alerts`);
    return res.json();
};

export const removeAlert = async (id) => {
    await fetch(`${API_BASE_URL}/remove-alert`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id })
    });
};

export const addAlert = async (alertData) => {
    await fetch(`${API_BASE_URL}/add-alert`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(alertData)
    });
};
