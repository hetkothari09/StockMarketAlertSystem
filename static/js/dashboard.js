let latestData = [];
let dropdownInitialized = false;
let lastToastId = 0;
const seenLogs = new Set();

/* ================= TOAST NOTIFICATIONS ================= */



function showToast(message, type = "info") {
    const container = document.getElementById("toast-container");
    if (!container) return;

    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;
    toast.textContent = message;

    container.appendChild(toast);
    setTimeout(() => toast.classList.add("show"), 10);

    setTimeout(() => {
        toast.classList.remove("show");
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

/* ================= MARKET DATA ================= */
function getRowPriority(row) {
    // 🔥 HIGHEST PRIORITY: USER ALERT
    if (row.status === "ALERT") return 4;

    // Institutional / volume anomalies
    if (row.volume_intensity === "SPIKE") return 3;
    if (row.volume_intensity === "HIGH") return 2;

    // Relative volume strength
    if (row.status && row.status.startsWith("ABOVE")) return 1;

    return 0;
}

async function fetchActiveAlerts() {
    const res = await fetch("/alerts");
    const alerts = await res.json();

    const box = document.getElementById("user-alerts");
    box.innerHTML = "";

    if (!alerts.length) {
        box.innerHTML = `<div class="muted">No active alerts</div>`;
        return;
    }

    // 🔥 HEADER — ADD ONCE
    const header = document.createElement("div");
    header.className = "alert-header";
    header.innerHTML = `
        <div>Symbol</div>
        <div>Condition</div>
        <div>Status</div>
        <div></div>
    `;
    box.appendChild(header);

    // 🔥 ROWS — APPEND
    alerts.forEach(a => {
        const row = document.createElement("div");
        row.className = "alert-row-box";

        row.innerHTML = `
            <div class="alert-col symbol">${a.symbol}</div>
            <div class="alert-col condition">
                ${a.operator} ${a.right_type} ${a.right_value ?? ""}
            </div>
            <div class="alert-col status">
                ${a.triggered ? "🔥" : ""}
            </div>
            <div class="alert-col action">
                <button onclick="removeAlert('${a.id}')">✕</button>
            </div>
        `;

        box.appendChild(row);
    });
}

async function removeAlert(id) {
    await fetch("/remove-alert", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id })
    });

    showToast("Alert removed", "warn");
    fetchActiveAlerts();
}

async function fetchMarketData() {
    const res = await fetch("/data");
    let data = await res.json();

    latestData = data;

    // Move red-alert rows to top
    data.sort((a, b) => {
    const pa = getRowPriority(a);
    const pb = getRowPriority(b);

    if (pa !== pb) return pb - pa;  // higher priority first

    // Optional: secondary sort by live volume
    return (b.live_volume || 0) - (a.live_volume || 0);
});

    const tbody = document.getElementById("market-body");
    tbody.innerHTML = "";

    const alertSelect = document.getElementById("alert-symbol");
    const compareSelect = document.getElementById("compare-symbol");

    if (!dropdownInitialized) {
        alertSelect.innerHTML = "";
        compareSelect.innerHTML = "";

        data.forEach(row => {
            const opt = document.createElement("option");
            opt.value = row.symbol;
            opt.textContent = row.symbol;
            alertSelect.appendChild(opt);
            compareSelect.appendChild(opt.cloneNode(true));
        });

        dropdownInitialized = true;
    }

    data.forEach(row => {
        const tr = document.createElement("tr");
        
        if (
            row.status === "ALERT" ||                       // 🔥 USER ALERT
            row.volume_intensity === "SPIKE" ||
            row.volume_intensity === "HIGH" ||
            (row.status && row.status.startsWith("ABOVE"))
        ) {
            tr.classList.add("alert-row");
        }

        tr.style.cursor = "pointer"; // ✅ cursor fix

        tr.innerHTML = `
            <td>${row.symbol}</td>

            <!-- 🔥 LIVE VOLUME (PRIMARY) -->
            <td class="num live-vol">${format(row.live_volume)}</td>

            <!-- 🧊 AVERAGES (SECONDARY) -->
            <td class="num avg">${format(row.prev_day)}</td>
            <td class="num avg">${format(row.weekly_avg)}</td>
            <td class="num avg">${format(row.monthly_avg)}</td>

            <!-- 📊 VOLUME MOVEMENT (BADGE) -->
            <td class="num">
                <span class="badge ${
                    row.volume_intensity === "SPIKE" ? "badge-spike" :
                    row.volume_intensity === "HIGH" ? "badge-high" :
                    row.volume_intensity === "WAITING" ? "badge-wait" :
                    "badge-normal"
                }">
                    ${row.volume_intensity}
                </span>
            </td>

            <!-- 🚨 STATUS (HEADLINE) -->
            <td class="${
                row.status === "ALERT" || row.status.startsWith("ABOVE")
                    ? "status-strong"
                    : "status-muted"
            }">
                ${row.status}
            </td>
        `;

        tr.onclick = () => openChart(row.symbol);
        tbody.appendChild(tr);
    });
}


/* ================= SYSTEM LOGS ================= */

async function fetchLogs() {
    const res = await fetch("/logs");
    const logs = await res.json();

    const logBox = document.getElementById("logs");
    logBox.innerHTML = "";

    logs.slice().reverse().forEach(log => {
        const key = `${log.time}-${log.message}`;

        const div = document.createElement("div");
        div.classList.add("log");

        const msg = log.message.toUpperCase();

        // 🔴 ALERT / SPIKE / INSTITUTIONAL
        if (
            msg.includes("ALERT") ||
            msg.includes("SPIKE") ||
            msg.includes("INSTITUTIONAL")
        ) {
            div.classList.add("log-alert");
        }

        // 🟡 STATUS CHANGES / ABOVE LEVELS
        else if (
            msg.includes("STATUS CHANGE") ||
            msg.includes("ABOVE")
        ) {
            div.classList.add("log-status");
        }

        // 🔵 CREATION / REMOVAL / INFO
        else if (
            msg.includes("CREATED") ||
            msg.includes("REMOVED")
        ) {
            div.classList.add("log-info");
        }

        // ⚪ DEFAULT
        else {
            div.classList.add("log-default");
        }

        div.textContent = `[${log.time}] ${log.message}`;
        logBox.appendChild(div);

        if (
            !seenLogs.has(key) &&
            (
                log.message.includes("STATUS CHANGE") ||
                log.message.includes("ALERT CREATED") ||
                log.message.includes("ALERT TRIGGERED")
            )
        ) {
            seenLogs.add(key);
            showToast(log.message, "info");
        }
    });
}

/* ================= ALERT CREATION ================= */

async function createAlert() {
    const symbol = document.getElementById("alert-symbol").value;
    const operator = document.getElementById("alert-operator").value;
    const rightType = document.getElementById("alert-right-type").value;
    const rightValueRaw = document.getElementById("alert-right-value").value;

    const payload = {
        symbol,
        operator,
        right_type: rightType
    };

    if (rightType === "FIXED" || rightType === "MULTIPLIER_WEEKLY") {
        if (!rightValueRaw) {
            showToast("Please enter a value / multiplier", "warn");
            return;
        }
        payload.right_value = parseFloat(rightValueRaw);
    }

    await fetch("/add-alert", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    });

    showToast(`Alert created for ${symbol}`, "success");

    document.getElementById("alert-right-value").value = "";
}

/* ================= VOLUME COMPARISON ================= */

function compareVolume() {
    const symbol = document.getElementById("compare-symbol").value;
    const row = latestData.find(r => r.symbol === symbol);

    if (!row || !row.weekly_avg || !row.monthly_avg) {
        document.getElementById("compare-result").innerHTML =
            "Insufficient data for comparison";
        return;
    }

    const weeklyDiff = ((row.live_volume - row.weekly_avg) / row.weekly_avg) * 100;
    const monthlyDiff = ((row.live_volume - row.monthly_avg) / row.monthly_avg) * 100;

    document.getElementById("compare-result").innerHTML = `
        <div>Live vs Weekly Avg: <b>${weeklyDiff.toFixed(2)}%</b></div>
        <div>Live vs Monthly Avg: <b>${monthlyDiff.toFixed(2)}%</b></div>
    `;
}

/* ================= CHART ================= */

let chart = null;
let volumeSeries = null;

async function openChart(symbol) {
    document.getElementById("chartModal").classList.remove("hidden");
    document.getElementById("chartTitle").textContent = `${symbol} – Volume`;

    const container = document.getElementById("chartContainer");
    container.innerHTML = "";

    chart = LightweightCharts.createChart(container, {
        width: container.clientWidth,
        height: container.clientHeight,
        layout: {
            background: { color: "#020617" },
            textColor: "#d1d5db",
            fontSize: 12,
            fontFamily: "Inter, system-ui"
        },
        grid: {
            vertLines: { color: "#1f2937" },
            horzLines: { color: "#1f2937" },
        },
        crosshair: {
            mode: LightweightCharts.CrosshairMode.Normal,
        },
        timeScale: {
            timeVisible: true,
            secondsVisible: false,
        },
        rightPriceScale: {
            scaleMargins: { top: 0.2, bottom: 0.2 },
        },
    });

    // ✅ STANDALONE API (FIXED)
    volumeSeries = chart.addSeries(
        LightweightCharts.HistogramSeries,
        {
            color: "#3b82f6",
            priceFormat: { type: "volume" },
        }
    );

    const res = await fetch(`/historical/${symbol}`);

if (!res.ok) {
    console.error("Failed to load historical data for", symbol);
    return;
}

const text = await res.text();

// 🔥 Prevent JSON parse crash
if (!text.startsWith("[")) {
    console.error("Invalid historical response:", text);
    return;
}

const historical = JSON.parse(text);

    volumeSeries.setData(historical);
    chart.timeScale().fitContent();
}
function closeChart() {
    document.getElementById("chartModal").classList.add("hidden");
}

/* ================= HELPERS ================= */

function format(val) {
    if (val == null) return "-";
    return val.toLocaleString();
}

/* ================= POLLING ================= */

setInterval(fetchMarketData, 1000);
setInterval(fetchLogs, 1500);
setInterval(fetchActiveAlerts, 2000);