export const fetchLogs = async () => {
    const res = await fetch("http://localhost:7000/logs");
    return res.json();
};
