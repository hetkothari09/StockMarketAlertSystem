
export const format = (val) => {
    if (val == null || val === undefined) return "-";
    return val.toLocaleString();
};

export const getRowPriority = (row) => {
    // 🔥 HIGHEST PRIORITY: USER ALERT
    if (row.status === "ALERT") return 4;

    // Institutional / volume anomalies
    if (row.volume_intensity === "VERY HIGH") return 3;
    if (row.volume_intensity === "HIGH") return 2;

    // Relative volume strength
    if (row.status && row.status.startsWith("ABOVE")) return 1;

    return 0;
};
