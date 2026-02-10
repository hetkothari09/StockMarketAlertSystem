export const fetchActiveAlerts = async () => {
    const res = await fetch("http://localhost:7000/alerts");
    return res.json();
};

export const removeAlert = async (id) => {
    await fetch("http://localhost:7000/remove-alert", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id })
    });
};

export const addAlert = async (alertData) => {
    await fetch("http://localhost:7000/add-alert", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(alertData)
    });
};
