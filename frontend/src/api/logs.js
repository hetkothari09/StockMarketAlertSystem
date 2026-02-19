export const fetchLogs = async () => {
    const res = await fetch(`http://${window.location.hostname}:7000/logs`);
    return res.json();
};
