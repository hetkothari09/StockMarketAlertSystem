import React from 'react';
import useAlerts from '../hooks/useAlerts';
import { removeAlert } from '../api/alerts';

const ActiveAlerts = () => {
    const alerts = useAlerts();

    const handleRemove = async (id) => {
        await removeAlert(id);
    };

    return (
        <div className="sidebar-panel active-alerts-panel">
            <div className="panel-header">Active Alerts</div>
            <div className="active-alerts-list">
                {alerts.length === 0 ? (
                    <div style={{ padding: '10px', color: '#9ca3af', fontSize: '12px' }}>No active alerts</div>
                ) : (
                    alerts.map((alert) => (
                        <div key={alert.id} className="alert-item">
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
                                <span style={{ fontWeight: 'bold', color: '#e5e7eb' }}>{alert.symbol}</span>
                                <span style={{ fontSize: '11px', color: '#9ca3af' }}>
                                    {alert.operator} {alert.right_type} {alert.right_value}
                                </span>
                            </div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                {alert.triggered && <span title="Triggered">🔥</span>}
                                <button onClick={() => handleRemove(alert.id)}>✕</button>
                            </div>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
};

export default ActiveAlerts;
