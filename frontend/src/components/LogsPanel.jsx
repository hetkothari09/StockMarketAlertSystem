import React, { useEffect, useRef } from 'react';
import useLogs from '../hooks/useLogs';

const LogsPanel = () => {
    const logs = useLogs();
    const logsEndRef = useRef(null);

    const getLogClass = (msg) => {
        const m = msg.toUpperCase();
        if (m.includes("ALERT") || m.includes("SPIKE") || m.includes("INSTITUTIONAL")) return "log-alert";
        if (m.includes("STATUS CHANGE") || m.includes("ABOVE")) return "log-status";
        if (m.includes("CREATED") || m.includes("REMOVED")) return "log-info";
        return "log-default";
    };

    // Auto-scroll to bottom when logs update
    useEffect(() => {
        if (logsEndRef.current) {
            logsEndRef.current.scrollIntoView({ behavior: "smooth" });
        }
    }, [logs]);

    return (
        <div className="panel logs-panel">
            <div className="panel-header">System Logs</div>
            <div className="logs-content">
                {[...logs].reverse().map((log, index) => (
                    <div key={index} className={`log-entry ${getLogClass(log.message)}`}>
                        [{log.time}] {log.message}
                    </div>
                ))}
                <div ref={logsEndRef} />
            </div>
        </div>
    );
};

export default LogsPanel;
