import React, { useState } from 'react';
import { setTimeRange } from '../api/market';
import { useToast } from './ToastContext';

const TimeRangeSelector = () => {
    const [start, setStart] = useState("09:30");
    const [end, setEnd] = useState("16:00");
    const { showToast } = useToast();

    const handleApply = async () => {
        try {
            await setTimeRange(start, end);
            showToast(`Time range updated: ${start} - ${end}`, 'success');
        } catch (error) {
            showToast("Failed to update time range", 'error');
        }
    };

    return (
        <div className="time-range-selector">
            <span style={{ fontWeight: 'bold', color: '#9ca3af', fontSize: '13px' }}>Volume Time Range:</span>
            <input
                type="time"
                value={start}
                onChange={(e) => setStart(e.target.value)}
            />
            <span style={{ color: '#9ca3af' }}>to</span>
            <input
                type="time"
                value={end}
                onChange={(e) => setEnd(e.target.value)}
            />
            <button className="primary-btn" onClick={handleApply}>Apply</button>
        </div>
    );
};

export default TimeRangeSelector;
