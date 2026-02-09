export async function fetchMarketData() {
    const res = await fetch("http://localhost:5000/data");
    return res.json();
}

export async function setTimeRange(start, end) {
    const res = await fetch("http://localhost:5000/set-time-range", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ start, end })
    });
    return res.json();
}
