import React from 'react';
import { format } from '../utils/helpers';

const StockRow = ({ stock, onClick }) => {
    // Determine if the row should be highlighted as an alert
    const isAlert =
        stock.status === "ALERT" ||
        stock.volume_intensity === "VERY HIGH" ||
        stock.volume_intensity === "HIGH" ||
        (stock.status && stock.status.startsWith("ABOVE"));

    const rowClass = isAlert ? "alert-row" : "";

    // Badge styling based on volume intensity
    let badgeClass = "badge-normal";
    if (stock.volume_intensity === "VERY HIGH") badgeClass = "badge-spike";
    if (stock.volume_intensity === "HIGH") badgeClass = "badge-high";
    if (stock.volume_intensity === "WAITING") badgeClass = "badge-wait";

    // Status text styling
    const statusClass = (stock.status === "ALERT" || (stock.status && stock.status.startsWith("ABOVE")))
        ? "status-strong"
        : "status-muted";

    return (
        <tr className={isAlert ? "alert-row" : ""} onClick={() => onClick(stock.symbol)}>
            <td>{stock.symbol}</td>
            <td className="live-vol">{format(stock.live_volume)}</td>
            <td className="avg">{format(stock.prev_day)}</td>
            <td className="avg">{format(stock.weekly_avg)}</td>
            <td className="avg">{format(stock.monthly_avg)}</td>
            <td>
                <span className={`badge ${badgeClass}`}>
                    {stock.volume_intensity}
                </span>
            </td>
            <td className={statusClass}>
                {stock.status}
            </td>
        </tr>
    );
};

export default StockRow;
