import { useState, useEffect } from 'react';
import { fetchActiveAlerts } from '../api/alerts';

const useAlerts = () => {
    const [alerts, setAlerts] = useState([]);

    useEffect(() => {
        const loadAlerts = async () => {
            const result = await fetchActiveAlerts();
            setAlerts(result);
        };

        loadAlerts(); // Initial load
        const interval = setInterval(loadAlerts, 2000); // Poll every 2s

        return () => clearInterval(interval);
    }, []);

    return alerts;
};

export default useAlerts;
