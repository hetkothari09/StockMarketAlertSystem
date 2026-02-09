import React, { useState } from 'react';
import MarketTable from './components/MarketTable';
import Sidebar from './components/Sidebar';
import TimeRangeSelector from './components/TimeRangeSelector';
import ChartModal from './components/ChartModal';

function App() {
    const [selectedSymbol, setSelectedSymbol] = useState(null);

    return (
        <div className="app-container">
            <div className="navbar">
                <div className="logo">VOL<span>ALERT</span></div>
                <TimeRangeSelector />
            </div>

            <div className="dashboard-container">
                <MarketTable onStockClick={setSelectedSymbol} />
                <Sidebar />
            </div>

            {selectedSymbol && (
                <ChartModal symbol={selectedSymbol} onClose={() => setSelectedSymbol(null)} />
            )}
        </div>
    );
}

export default App;
