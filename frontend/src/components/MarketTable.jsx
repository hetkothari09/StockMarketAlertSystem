import React, { useMemo } from 'react';
import useMarketData from '../hooks/useMarketData';
import StockRow from './StockRow';
import { getRowPriority } from '../utils/helpers';

const MarketTable = ({ marketData, hiddenSymbols, intensityFilters, onStockClick, onAddStock }) => {
    const sortedData = useMemo(() => {
        return marketData
            .filter(stock => !hiddenSymbols.has(stock.symbol))
            .map(stock => {
                const originalIntensity = stock.volume_intensity || 'WAITING';
                const isFilteredOut = !intensityFilters.has(originalIntensity);

                // If filtered out, effectively treat it as "NORMAL" for both display and sorting
                // This ensures it "acts like a normal stock" and sorts by volume with others
                // UNLESS it has an alert (handled by getRowPriority via status)
                const effectiveIntensity = isFilteredOut ? "NORMAL" : originalIntensity;

                return {
                    ...stock,
                    volume_intensity: effectiveIntensity,
                    // Remove isDemoted and displayIntensity as we are modifying the source property directly
                    // for consistent behavior across Sort and Display
                };
            })
            .sort((a, b) => {
                const pa = getRowPriority(a);
                const pb = getRowPriority(b);

                if (pa !== pb) return pb - pa;

                // Secondary sort by live volume
                return (b.live_volume || 0) - (a.live_volume || 0);
            });
    }, [marketData, hiddenSymbols, intensityFilters]);

    return (
        <div className="panel market-panel">
            <div className="panel-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span>NIFTY 50 – Volume Dashboard</span>
                <button
                    className="add-stock-trigger"
                    onClick={onAddStock}
                    title="Add Custom Stock"
                    style={{
                        background: 'rgba(59, 130, 246, 0.15)',
                        border: '1px solid rgba(59, 130, 246, 0.3)',
                        color: '#60a5fa',
                        padding: '4px 10px',
                        borderRadius: '6px',
                        fontSize: '11px',
                        fontWeight: '600',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '6px',
                        transition: 'all 0.2s ease',
                        textTransform: 'uppercase',
                        letterSpacing: '0.03em'
                    }}
                >
                    <span style={{ fontSize: '16px', lineHeight: 1 }}>+</span>
                    Add Stock
                </button>
            </div>
            <div className="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>Symbol</th>
                            <th>Live Vol</th>
                            <th>Prev Day</th>
                            <th>Weekly Avg</th>
                            <th>Monthly Avg</th>
                            <th>Volume Movement</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {sortedData.map((stock) => (
                            <StockRow
                                key={stock.symbol}
                                stock={stock}
                                onClick={() => onStockClick(stock.symbol)}
                            />
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default MarketTable;
