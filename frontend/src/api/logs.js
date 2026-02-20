import { API_BASE_URL } from '../config';

export const fetchLogs = async () => {
    const res = await fetch(`${API_BASE_URL}/logs`);
    return res.json();
};
