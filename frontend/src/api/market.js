import { API_BASE_URL } from '../config';

export async function fetchMarketData() {
    const res = await fetch(`${API_BASE_URL}/data`);
    return res.json();
}

export async function setTimeRange(start, end) {
    const res = await fetch(`${API_BASE_URL}/set-time-range`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ start, end })
    });
    return res.json();
}

export async function fetchAlertSettings() {
    const res = await fetch(`${API_BASE_URL}/alert-settings`);
    return res.json();
}

export async function updateAlertSettings(settings) {
    const res = await fetch(`${API_BASE_URL}/alert-settings`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(settings)
    });
    const data = await res.json();
    return data;
}

export async function addStock(symbol, days = 30) {
    const res = await fetch(`${API_BASE_URL}/add-stock`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ symbol, days })
    });
    return res.json();
}

export async function fetchAvailableSymbols() {
    const res = await fetch(`${API_BASE_URL}/available-symbols`);
    return res.json();
}
