export async function fetchMarketData() {
    const res = await fetch(`http://${window.location.hostname}:7000/data`);
    return res.json();
}

export async function setTimeRange(start, end) {
    const res = await fetch(`http://${window.location.hostname}:7000/set-time-range`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ start, end })
    });
    return res.json();
}

export async function fetchAlertSettings() {
    const res = await fetch(`http://${window.location.hostname}:7000/alert-settings`);
    return res.json();
}

export async function updateAlertSettings(settings) {
    const res = await fetch(`http://${window.location.hostname}:7000/alert-settings`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(settings)
    });
    const data = await res.json();
    return data;
}

export async function addStock(symbol, days = 30) {
    const res = await fetch(`http://${window.location.hostname}:7000/add-stock`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ symbol, days })
    });
    return res.json();
}

export async function fetchAvailableSymbols() {
    const res = await fetch(`http://${window.location.hostname}:7000/available-symbols`);
    return res.json();
}
