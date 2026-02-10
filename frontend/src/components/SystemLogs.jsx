import React, { useEffect, useRef } from 'react';
import useLogs from '../hooks/useLogs';

const SystemLogs = () => {
    const logs = useLogs();
    const containerRef = useRef(null);

    const getLogClass = (msg) => {
        const m = msg.toUpperCase();
        if (m.includes("ALERT") || m.includes("SPIKE") || m.includes("INSTITUTIONAL")) return "log-alert";
        if (m.includes("STATUS CHANGE") || m.includes("ABOVE")) return "log-status";
        if (m.includes("CREATED") || m.includes("REMOVED")) return "log-info";
        return "log-default";
    };

    // Auto-scroll logic for "Newest at Top"
    useEffect(() => {
        const container = containerRef.current;
        if (!container) return;

        // If user is near the top (reading new logs), stay at top.
        // If user scrolled down (reading history), don't disturb them.
        if (container.scrollTop < 50) {
            container.scrollTop = 0;
        }
    }, [logs]);

    return (
        <div className="sidebar-panel system-logs-panel">
            <div className="panel-header">System Logs</div>
            <div className="logs-content" ref={containerRef}>
                {[...logs].reverse().map((log, index) => (
                    <div key={index} className={`log-entry ${getLogClass(log.message)}`}>
                        [{log.time}] {log.message}
                    </div>
                ))}
            </div>
        </div>
    );
};

export default SystemLogs;
