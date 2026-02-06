let latestData = [];
let dropdownInitialized = false;
let lastToastId = 0;

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

async function fetchMarketData() {
    const res = await fetch("/data");
    let data = await res.json();

    latestData = data;

    data.sort((a, b) => {
        if (a.is_red_alert && !b.is_red_alert) return -1;
        if (!a.is_red_alert && b.is_red_alert) return 1;
        return 0;
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

        if (row.is_red_alert) tr.className = "alert-row";

        tr.innerHTML = `
            <td>${row.symbol}</td>
            <td class="num">${format(row.live_volume)}</td>
            <td class="num">${format(row.prev_day)}</td>
            <td class="num">${format(row.weekly_avg)}</td>
            <td class="num">${format(row.monthly_avg)}</td>
            <td class="num">${row.volume_intensity}</td>
            <td>${row.user_alert_hit ? "ALERT" : "NORMAL"}</td>
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
        div.className = "log";
        div.textContent = `[${log.time}] ${log.message}`;
        logBox.appendChild(div);

        if (!seenLogs.has(key) &&
            (log.message.includes("ALERT CREATED") ||
             log.message.includes("ALERT TRIGGERED"))) {

            seenLogs.add(key);
            showToast(log.message, "danger");
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
        },
        grid: {
            vertLines: { color: "#1f2937" },
            horzLines: { color: "#1f2937" },
        },
        timeScale: {
            timeVisible: true,
            secondsVisible: false,
        }
    });

    volumeSeries = chart.addSeries(
        LightweightCharts.HistogramSeries,
        {
            color: "#3b82f6",
            priceFormat: { type: "volume" },
        }
    );

    const res = await fetch(`/historical/${symbol}`);
    const historical = await res.json();

    volumeSeries.setData(historical);
    chart.timeScale().fitContent();
}

function closeChart() {
    document.getElementById("chartModal").classList.add("hidden");
}

function format(val) {
    if (val == null) return "-";
    return val.toLocaleString();
}

setInterval(fetchMarketData, 1000);
setInterval(fetchLogs, 1500);