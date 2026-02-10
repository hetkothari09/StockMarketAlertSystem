import React, { useState, useEffect } from 'react';
import { fetchAlertSettings, updateAlertSettings } from '../api/market';
import { useToast } from './ToastContext';

const AlertToggles = () => {
    const [settings, setSettings] = useState({
        above_prev_day: true,
        above_weekly_avg: true,
        above_monthly_avg: true
    });
    const { showToast } = useToast();

    useEffect(() => {
        const loadSettings = async () => {
            try {
                const data = await fetchAlertSettings();
                setSettings(data);
            } catch (err) {
                console.error("Failed to fetch alert settings", err);
            }
        };
        loadSettings();
    }, []);

    const handleToggle = async (key) => {
        const newSettings = { ...settings, [key]: !settings[key] };
        setSettings(newSettings);
        try {
            await updateAlertSettings(newSettings);
            showToast(`Status alert ${newSettings[key] ? 'enabled' : 'disabled'}`, 'info');
        } catch (err) {
            showToast('Failed to update settings', 'error');
        }
    };

    return (
        <div className="panel alert-toggles-panel">
            <h3 className="panel-header">Global Alert Toggles</h3>
            <div className="toggle-group">
                <label className="toggle-item">
                    <div className="toggle-switch">
                        <input
                            type="checkbox"
                            checked={settings.above_prev_day}
                            onChange={() => handleToggle('above_prev_day')}
                        />
                        <span className="slider"></span>
                    </div>
                    <span>Above Prev Day</span>
                </label>

                <label className="toggle-item">
                    <div className="toggle-switch">
                        <input
                            type="checkbox"
                            checked={settings.above_weekly_avg}
                            onChange={() => handleToggle('above_weekly_avg')}
                        />
                        <span className="slider"></span>
                    </div>
                    <span>Above Weekly Avg</span>
                </label>

                <label className="toggle-item">
                    <div className="toggle-switch">
                        <input
                            type="checkbox"
                            checked={settings.above_monthly_avg}
                            onChange={() => handleToggle('above_monthly_avg')}
                        />
                        <span className="slider"></span>
                    </div>
                    <span>Above Monthly Avg</span>
                </label>
            </div>
        </div>
    );
};

export default AlertToggles;
