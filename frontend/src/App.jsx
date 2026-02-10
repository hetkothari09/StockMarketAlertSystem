import React, { useState, useMemo } from 'react';
import MarketTable from './components/MarketTable';
import TimeRangeSelector from './components/TimeRangeSelector';
import ChartModal from './components/ChartModal';
import { ToastProvider } from './components/ToastContext';
import CreateAlert from './components/CreateAlert';
import ActiveAlerts from './components/ActiveAlerts';
import AlertToggles from './components/AlertToggles';
import SymbolFilter from './components/SymbolFilter';
import SystemLogs from './components/SystemLogs';
import useMarketData from './hooks/useMarketData';

function App() {
    const [selectedSymbol, setSelectedSymbol] = useState(null);
    const [hiddenSymbols, setHiddenSymbols] = useState(new Set());
    const marketData = useMarketData();

    // Get all unique symbols from available data
    const allSymbols = useMemo(() => marketData.map(s => s.symbol), [marketData]);

    const handleToggleSymbol = (symbol) => {
        setHiddenSymbols(prev => {
            const next = new Set(prev);
            if (next.has(symbol)) next.delete(symbol);
            else next.add(symbol);
            return next;
        });
    };

    const handleShowAll = () => setHiddenSymbols(new Set());
    const handleHideAll = () => setHiddenSymbols(new Set(allSymbols));

    return (
        <ToastProvider>
            <div className="app-container">
                <div className="navbar">
                    <div className="logo">VOL<span>ALERT</span></div>
                    <TimeRangeSelector />
                </div>

                <div className="dashboard-container">
                    {/* LEFT: Alerts & Filters Column */}
                    <div className="side-panel left-panel">
                        <div className="create-alert-panel-container">
                            <CreateAlert />
                        </div>
                        <div className="active-alerts-panel-container">
                            <ActiveAlerts />
                        </div>
                        <div className="alert-toggles-container">
                            <AlertToggles />
                        </div>
                        <div className="symbol-filter-container">
                            <SymbolFilter
                                allSymbols={allSymbols}
                                hiddenSymbols={hiddenSymbols}
                                onToggleSymbol={handleToggleSymbol}
                                onShowAll={handleShowAll}
                                onHideAll={handleHideAll}
                            />
                        </div>
                    </div>

                    {/* CENTER: Market Table (Chart) */}
                    <MarketTable
                        marketData={marketData}
                        hiddenSymbols={hiddenSymbols}
                        onStockClick={setSelectedSymbol}
                    />

                    {/* RIGHT: System Logs Column */}
                    <div className="side-panel right-panel">
                        <div className="system-logs-panel-container full-height">
                            <SystemLogs />
                        </div>
                    </div>
                </div>

                {selectedSymbol && (
                    <ChartModal symbol={selectedSymbol} onClose={() => setSelectedSymbol(null)} />
                )}
            </div>
        </ToastProvider>
    );
}

export default App;
