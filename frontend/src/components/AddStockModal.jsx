import React, { useState } from 'react';
import { addStock } from '../api/market';
import { useToast } from './ToastContext';

const AddStockModal = ({ onClose, onSuccess }) => {
    const [symbol, setSymbol] = useState('');
    const [days, setDays] = useState(30); // Default to 1 month
    const [isSubmitting, setIsSubmitting] = useState(false);
    const { showToast } = useToast();

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!symbol) return;

        setIsSubmitting(true);
        try {
            const res = await addStock(symbol, days);
            if (res.status === 'ok') {
                showToast(res.message || `Successfully added ${symbol}`, 'success');
                if (onSuccess) onSuccess();
                onClose();
            } else {
                showToast(res.message || 'Failed to add stock', 'error');
            }
        } catch (err) {
            showToast('Network error adding stock', 'error');
            console.error(err);
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="modal-overlay" onClick={onClose} style={{
            position: 'fixed', inset: 0,
            background: 'rgba(2, 6, 23, 0.85)',
            backdropFilter: 'blur(8px)',
            display: 'flex', justifyContent: 'center', alignItems: 'center',
            zIndex: 2000
        }}>
            <div className="modal-content glass" onClick={e => e.stopPropagation()} style={{
                maxWidth: '420px',
                width: '90%',
                background: 'rgba(15, 23, 42, 0.7)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                padding: '24px',
                borderRadius: '16px',
                position: 'relative',
                boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5)'
            }}>
                <button className="modal-close" onClick={onClose} style={{
                    position: 'absolute', top: '16px', right: '16px',
                    background: 'none', border: 'none', color: '#64748b',
                    fontSize: '20px', cursor: 'pointer'
                }}>×</button>

                <h3 style={{ margin: '0 0 8px 0', fontSize: '1.25rem', color: '#f8fafc' }}>Add Custom Stock</h3>
                <p style={{ margin: '0 0 20px 0', fontSize: '0.85rem', color: '#94a3b8' }}>
                    Enter an NSE symbol to begin real-time monitoring.
                </p>

                <form onSubmit={handleSubmit}>
                    <div className="form-group" style={{ marginBottom: '20px' }}>
                        <label style={{ display: 'block', marginBottom: '8px', fontSize: '0.75rem', fontWeight: '600', color: '#3b82f6', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                            SYMBOL NAME
                        </label>
                        <input
                            type="text"
                            value={symbol}
                            onChange={(e) => setSymbol(e.target.value.toUpperCase())}
                            placeholder="e.g. ZOMATO"
                            className="form-input"
                            autoFocus
                            style={{
                                width: '100%',
                                background: 'rgba(2, 6, 23, 0.5)',
                                border: '1px solid rgba(255, 255, 255, 0.1)',
                                borderRadius: '8px',
                                padding: '12px',
                                color: '#f8fafc',
                                fontSize: '1rem'
                            }}
                        />
                    </div>

                    <div className="form-group" style={{ marginBottom: '20px' }}>
                        <label style={{ display: 'block', marginBottom: '8px', fontSize: '0.75rem', fontWeight: '600', color: '#3b82f6', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                            HISTORICAL DATA RANGE
                        </label>
                        <select
                            value={days}
                            onChange={(e) => setDays(Number(e.target.value))}
                            style={{
                                width: '100%',
                                background: 'rgba(2, 6, 23, 0.5)',
                                border: '1px solid rgba(59, 130, 246, 0.3)',
                                borderRadius: '8px',
                                padding: '12px',
                                color: '#f8fafc',
                                fontSize: '1rem',
                                cursor: 'pointer',
                                outline: 'none',
                                transition: 'all 0.2s ease'
                            }}
                            onFocus={(e) => e.target.style.borderColor = 'rgba(59, 130, 246, 0.6)'}
                            onBlur={(e) => e.target.style.borderColor = 'rgba(59, 130, 246, 0.3)'}
                        >
                            <option value={30} style={{ background: '#0f172a', color: '#f8fafc' }}>1 Month (30 days)</option>
                            <option value={90} style={{ background: '#0f172a', color: '#f8fafc' }}>3 Months (90 days)</option>
                            <option value={180} style={{ background: '#0f172a', color: '#f8fafc' }}>6 Months (180 days)</option>
                            <option value={365} style={{ background: '#0f172a', color: '#f8fafc' }}>1 Year (365 days)</option>
                        </select>
                        <div style={{ marginTop: '12px', padding: '10px', borderRadius: '6px', background: 'rgba(59, 130, 246, 0.05)', borderLeft: '3px solid #3b82f6' }}>
                            <p style={{ margin: 0, fontSize: '11px', lineHeight: '1.4', color: '#60a5fa' }}>
                                <strong>Note:</strong> Historical data will be fetched in the background. The stock will appear immediately and metrics will populate once the backfill completes.
                            </p>
                        </div>
                    </div>

                    <div style={{ display: 'flex', gap: '12px', marginTop: '24px' }}>
                        <button
                            type="button"
                            onClick={onClose}
                            disabled={isSubmitting}
                            style={{
                                flex: 1,
                                padding: '12px 20px',
                                background: 'rgba(71, 85, 105, 0.3)',
                                border: '1px solid rgba(148, 163, 184, 0.2)',
                                borderRadius: '8px',
                                color: '#cbd5e1',
                                fontSize: '0.95rem',
                                fontWeight: '600',
                                cursor: isSubmitting ? 'not-allowed' : 'pointer',
                                transition: 'all 0.2s ease',
                                opacity: isSubmitting ? 0.5 : 1
                            }}
                            onMouseEnter={(e) => !isSubmitting && (e.target.style.background = 'rgba(71, 85, 105, 0.5)')}
                            onMouseLeave={(e) => !isSubmitting && (e.target.style.background = 'rgba(71, 85, 105, 0.3)')}
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            disabled={isSubmitting || !symbol}
                            style={{
                                flex: 2,
                                padding: '12px 20px',
                                background: (isSubmitting || !symbol) ? 'rgba(59, 130, 246, 0.3)' : 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
                                border: '1px solid rgba(59, 130, 246, 0.4)',
                                borderRadius: '8px',
                                color: '#ffffff',
                                fontSize: '0.95rem',
                                fontWeight: '600',
                                cursor: (isSubmitting || !symbol) ? 'not-allowed' : 'pointer',
                                transition: 'all 0.2s ease',
                                boxShadow: (isSubmitting || !symbol) ? 'none' : '0 4px 12px rgba(59, 130, 246, 0.3)',
                                opacity: (isSubmitting || !symbol) ? 0.5 : 1
                            }}
                            onMouseEnter={(e) => !(isSubmitting || !symbol) && (e.target.style.transform = 'translateY(-1px)', e.target.style.boxShadow = '0 6px 16px rgba(59, 130, 246, 0.4)')}
                            onMouseLeave={(e) => !(isSubmitting || !symbol) && (e.target.style.transform = 'translateY(0)', e.target.style.boxShadow = '0 4px 12px rgba(59, 130, 246, 0.3)')}
                        >
                            {isSubmitting ? 'Verifying...' : 'Add Stock'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default AddStockModal;
