import React, { useState } from 'react';

const SymbolFilter = ({ allSymbols, hiddenSymbols, onToggleSymbol, onShowAll, onHideAll }) => {
    const [search, setSearch] = useState("");

    const filteredSymbols = search.trim() === ""
        ? []
        : allSymbols.filter(s =>
            s.toLowerCase().includes(search.toLowerCase())
        ).sort();

    return (
        <div className="panel symbol-filter-panel">
            <div className="panel-header">Symbol Filter</div>

            <div className="filter-controls">
                <input
                    type="text"
                    placeholder="Search symbols..."
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    className="symbol-search-input"
                />
                <div className="filter-actions">
                    <button onClick={onShowAll} className="btn-small btn-outline">Show All</button>
                    <button onClick={onHideAll} className="btn-small btn-outline">Hide All</button>
                </div>
            </div>

            <div className="symbol-list-container">
                {filteredSymbols.map(symbol => (
                    <label key={symbol} className="symbol-toggle-item">
                        <input
                            type="checkbox"
                            checked={!hiddenSymbols.has(symbol)}
                            onChange={() => onToggleSymbol(symbol)}
                        />
                        <span className="symbol-name">{symbol}</span>
                    </label>
                ))}
                {filteredSymbols.length === 0 && (
                    <div className="no-results">No symbols found</div>
                )}
            </div>
        </div>
    );
};

export default SymbolFilter;
