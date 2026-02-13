import React, { useState } from 'react';
import useMarketData from '../hooks/useMarketData';
import { addAlert } from '../api/alerts';
import { useToast } from './ToastContext';

const CreateAlert = () => {
    const marketData = useMarketData();
    const { showToast } = useToast();
    const [symbol, setSymbol] = useState("");
    const [operator, setOperator] = useState(">");
    const [rightType, setRightType] = useState("FIXED");
    const [rightValue, setRightValue] = useState("");

    // Initialize symbol when data loads
    React.useEffect(() => {
        if (marketData.length > 0 && !symbol) {
            setSymbol(marketData[0].symbol);
        }
    }, [marketData, symbol]);

    const handleCreate = async () => {
        if (!symbol) return;

        // Validation: Check if value is provided for Fixed/Multiplier types
        if ((rightType === 'FIXED' || rightType === 'MULTIPLIER_WEEKLY') && !rightValue) {
            showToast('Please enter a value for this alert type', 'error');
            return;
        }

        const payload = {
            symbol,
            operator,
            right_type: rightType,
            right_value: rightType === 'FIXED' || rightType === 'MULTIPLIER_WEEKLY' ? parseFloat(rightValue) : null
        };

        await addAlert(payload);
        setRightValue(""); // Clear value
        showToast(`Alert created for ${symbol}`, 'success');
    };

    return (
        <div className="sidebar-panel create-alert-panel">
            <div className="panel-header">Create Volume Alert</div>
            <div className="alert-form-grid">
                <select value={symbol} onChange={(e) => setSymbol(e.target.value)} className="col-span-2">
                    {marketData.map(stock => (
                        <option key={stock.symbol} value={stock.symbol}>{stock.symbol}</option>
                    ))}
                </select>

                <select value={operator} onChange={(e) => setOperator(e.target.value)}>
                    <option value=">">&gt;</option>
                    <option value=">=">&gt;=</option>
                </select>

                <select value={rightType} onChange={(e) => setRightType(e.target.value)}>
                    <option value="FIXED">Fixed Volume</option>
                    <option value="PREV_DAY">Prev Day Volume</option>
                    <option value="WEEKLY_AVG">Weekly Avg</option>
                    <option value="MONTHLY_AVG">Monthly Avg</option>
                    <option value="MULTIPLIER_WEEKLY">Weekly Avg ×</option>
                </select>

                {(rightType === 'FIXED' || rightType === 'MULTIPLIER_WEEKLY') && (
                    <input
                        type="number"
                        placeholder="Value"
                        value={rightValue}
                        onChange={(e) => setRightValue(e.target.value)}
                        className="col-span-2"
                    />
                )}

                <button
                    className="primary-btn col-span-2"
                    onClick={handleCreate}
                >
                    Create
                </button>
            </div>
        </div>
    );
};

export default CreateAlert;
