import React, { useMemo } from 'react';
import useMarketData from '../hooks/useMarketData';
import StockRow from './StockRow';
import { getRowPriority } from '../utils/helpers';

const MarketTable = ({ marketData, hiddenSymbols, onStockClick }) => {
    const sortedData = useMemo(() => {
        return marketData
            .filter(stock => !hiddenSymbols.has(stock.symbol))
            .sort((a, b) => {
                const pa = getRowPriority(a);
                const pb = getRowPriority(b);

                if (pa !== pb) return pb - pa;  // higher priority first

                // Secondary sort by live volume
                return (b.live_volume || 0) - (a.live_volume || 0);
            });
    }, [marketData, hiddenSymbols]);

    return (
        <div className="panel market-panel">
            <div className="panel-header">NIFTY 50 – Volume Dashboard</div>
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
