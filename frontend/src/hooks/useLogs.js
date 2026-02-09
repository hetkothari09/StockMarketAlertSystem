import { useState, useEffect } from 'react';
import { fetchLogs } from '../api/logs';

const useLogs = () => {
    const [logs, setLogs] = useState([]);

    useEffect(() => {
        const loadLogs = async () => {
            const result = await fetchLogs();
            setLogs(result);
        };

        loadLogs(); // Initial load
        const interval = setInterval(loadLogs, 2000); // Poll every 2s

        return () => clearInterval(interval);
    }, []);

    return logs;
};

export default useLogs;
