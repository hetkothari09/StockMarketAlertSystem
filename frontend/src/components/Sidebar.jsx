import React from 'react';
import SystemLogs from './SystemLogs';
import ActiveAlerts from './ActiveAlerts';
import CreateAlert from './CreateAlert';

const Sidebar = () => {
    return (
        <div className="panel logs-panel">
            <div className="sidebar-panel system-logs-panel-container">
                <SystemLogs />
            </div>
            <div className="sidebar-panel create-alert-panel-container">
                <CreateAlert />
            </div>
            <div className="sidebar-panel active-alerts-panel-container">
                <ActiveAlerts />
            </div>
        </div>
    );
};

export default Sidebar;
