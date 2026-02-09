import { useState, useEffect } from 'react';
import { fetchMarketData } from '../api/market';

const useMarketData = () => {
    const [data, setData] = useState([]);

    useEffect(() => {
        const loadData = async () => {
            const result = await fetchMarketData();
            setData(result);
        };

        loadData(); // Initial load
        const interval = setInterval(loadData, 1000); // Poll every 1s

        return () => clearInterval(interval);
    }, []);

    return data;
};

export default useMarketData;
