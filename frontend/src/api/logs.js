export const fetchLogs = async () => {
    const res = await fetch("http://localhost:5000/logs");
    return res.json();
};
