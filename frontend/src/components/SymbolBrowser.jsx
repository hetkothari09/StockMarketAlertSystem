import React, { useState, useEffect } from 'react';
import { fetchAvailableSymbols } from '../api/market';

const SymbolBrowser = ({ onClose, onSelect }) => {
    const [symbols, setSymbols] = useState([]);
    const [filteredSymbols, setFilteredSymbols] = useState([]);
    const [searchQuery, setSearchQuery] = useState('');
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadSymbols();
    }, []);

    useEffect(() => {
        if (searchQuery.trim() === '') {
            setFilteredSymbols(symbols);
        } else {
            const query = searchQuery.toUpperCase();
            const filtered = symbols.filter(s =>
                s.symbol.includes(query) ||
                (s.name && s.name.toUpperCase().includes(query))
            );
            setFilteredSymbols(filtered);
        }
    }, [searchQuery, symbols]);

    const loadSymbols = async () => {
        try {
            const res = await fetchAvailableSymbols();
            if (res.status === 'ok') {
                setSymbols(res.symbols);
                setFilteredSymbols(res.symbols);
            }
        } catch (error) {
            console.error('Failed to load symbols:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleSelect = (symbol) => {
        onSelect(symbol.symbol);
        onClose();
    };

    return (
        <div
            className="modal-overlay"
            onClick={onClose}
            style={{
                position: 'fixed',
                inset: 0,
                background: 'rgba(2, 6, 23, 0.9)',
                backdropFilter: 'blur(12px)',
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                zIndex: 2100
            }}
        >
            <div
                className="symbol-browser-content"
                onClick={e => e.stopPropagation()}
                style={{
                    width: '90%',
                    maxWidth: '800px',
                    height: '80vh',
                    background: 'rgba(15, 23, 42, 0.95)',
                    border: '1px solid rgba(59, 130, 246, 0.3)',
                    borderRadius: '16px',
                    padding: '24px',
                    display: 'flex',
                    flexDirection: 'column',
                    boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.7)'
                }}
            >
                {/* Header */}
                <div style={{ marginBottom: '20px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                        <h3 style={{ margin: 0, fontSize: '1.5rem', color: '#f8fafc' }}>
                            Browse NSE Symbols
                        </h3>
                        <button
                            onClick={onClose}
                            style={{
                                background: 'none',
                                border: 'none',
                                color: '#64748b',
                                fontSize: '24px',
                                cursor: 'pointer',
                                padding: '0',
                                lineHeight: 1
                            }}
                        >×</button>
                    </div>
                    <p style={{ margin: '0 0 16px 0', fontSize: '0.9rem', color: '#94a3b8' }}>
                        {loading ? 'Loading symbols...' : `${filteredSymbols.length} symbols available`}
                    </p>

                    {/* Search Bar */}
                    <input
                        type="text"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        placeholder="Search by symbol or company name..."
                        autoFocus
                        style={{
                            width: '100%',
                            background: 'rgba(2, 6, 23, 0.5)',
                            border: '1px solid rgba(59, 130, 246, 0.3)',
                            borderRadius: '8px',
                            padding: '12px 16px',
                            color: '#f8fafc',
                            fontSize: '1rem',
                            outline: 'none',
                            transition: 'border-color 0.2s ease'
                        }}
                        onFocus={(e) => e.target.style.borderColor = 'rgba(59, 130, 246, 0.6)'}
                        onBlur={(e) => e.target.style.borderColor = 'rgba(59, 130, 246, 0.3)'}
                    />
                </div>

                {/* Symbol List */}
                <div
                    style={{
                        flex: 1,
                        overflowY: 'auto',
                        background: 'rgba(2, 6, 23, 0.3)',
                        borderRadius: '8px',
                        padding: '8px'
                    }}
                >
                    {loading ? (
                        <div style={{ textAlign: 'center', padding: '40px', color: '#94a3b8' }}>
                            Loading symbols...
                        </div>
                    ) : filteredSymbols.length === 0 ? (
                        <div style={{ textAlign: 'center', padding: '40px', color: '#94a3b8' }}>
                            No symbols found matching "{searchQuery}"
                        </div>
                    ) : (
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '8px' }}>
                            {filteredSymbols.map((symbol) => (
                                <div
                                    key={symbol.token}
                                    onClick={() => handleSelect(symbol)}
                                    style={{
                                        background: 'rgba(15, 23, 42, 0.6)',
                                        border: '1px solid rgba(59, 130, 246, 0.2)',
                                        borderRadius: '6px',
                                        padding: '12px',
                                        cursor: 'pointer',
                                        transition: 'all 0.2s ease'
                                    }}
                                    onMouseEnter={(e) => {
                                        e.currentTarget.style.background = 'rgba(59, 130, 246, 0.1)';
                                        e.currentTarget.style.borderColor = 'rgba(59, 130, 246, 0.5)';
                                        e.currentTarget.style.transform = 'translateY(-2px)';
                                    }}
                                    onMouseLeave={(e) => {
                                        e.currentTarget.style.background = 'rgba(15, 23, 42, 0.6)';
                                        e.currentTarget.style.borderColor = 'rgba(59, 130, 246, 0.2)';
                                        e.currentTarget.style.transform = 'translateY(0)';
                                    }}
                                >
                                    <div style={{ fontWeight: '600', fontSize: '0.95rem', color: '#f8fafc', marginBottom: '4px' }}>
                                        {symbol.symbol}
                                    </div>
                                    <div style={{ fontSize: '0.75rem', color: '#94a3b8', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                                        {symbol.name}
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default SymbolBrowser;
