import React from 'react';
import { format } from '../utils/helpers';

const StockRow = ({ stock, onClick }) => {
    // Determine if the row should be highlighted as an alert
    const isAlert =
        stock.status === "ALERT" ||
        stock.volume_intensity === "SPIKE" ||
        stock.volume_intensity === "HIGH" ||
        (stock.status && stock.status.startsWith("ABOVE"));

    const rowClass = isAlert ? "alert-row" : "";

    // Badge styling based on volume intensity
    const badgeClass =
        stock.volume_intensity === "SPIKE" ? "badge-spike" :
            stock.volume_intensity === "HIGH" ? "badge-high" :
                stock.volume_intensity === "WAITING" ? "badge-wait" :
                    "badge-normal";

    // Status text styling
    const statusClass =
        stock.status === "ALERT" || (stock.status && stock.status.startsWith("ABOVE"))
            ? "status-strong"
            : "status-muted";

    return (
        <tr className={rowClass} onClick={onClick}>
            <td>{stock.symbol}</td>

            {/* Live Volume */}
            <td className="live-vol">{format(stock.live_volume)}</td>

            {/* Averages */}
            <td className="avg">{format(stock.prev_day)}</td>
            <td className="avg">{format(stock.weekly_avg)}</td>
            <td className="avg">{format(stock.monthly_avg)}</td>

            {/* Volume Movement Badge */}
            <td>
                <span className={`badge ${badgeClass}`}>
                    {stock.volume_intensity}
                </span>
            </td>

            {/* Status Text */}
            <td className={statusClass}>
                {stock.status}
            </td>
        </tr>
    );
};

export default StockRow;
