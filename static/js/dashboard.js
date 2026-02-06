let latestData = [];
let dropdownInitialized = false;
let lastAlertSeen = null;

/* ================= MARKET DATA ================= */

async function fetchMarketData() {
    const res = await fetch("/data");
    let data = await res.json();

    latestData = data;
    
    // 🔥 Move user-alert-hit rows to top
    data.sort((a, b) => {
        if (a.user_alert_hit && !b.user_alert_hit) return -1;
        if (!a.user_alert_hit && b.user_alert_hit) return 1;
        return 0;
    });

    const tbody = document.getElementById("market-body");
    tbody.innerHTML = "";

    const alertSelect = document.getElementById("alert-symbol");
    const compareSelect = document.getElementById("compare-symbol");

    // Populate dropdowns only once
    if (!dropdownInitialized) {
        alertSelect.innerHTML = "";
        compareSelect.innerHTML = "";

        data.forEach(row => {
            const opt1 = document.createElement("option");
            opt1.value = row.symbol;
            opt1.textContent = row.symbol;
            alertSelect.appendChild(opt1);

            const opt2 = opt1.cloneNode(true);
            compareSelect.appendChild(opt2);
        });

        dropdownInitialized = true;
    }

    data.forEach(row => {
        const tr = document.createElement("tr");

        let statusClass = "status-normal";
        let statusText = "NORMAL";

        /* User alerts ONLY */
        if (row.user_alert_hit) {
            statusClass = "alert-row";
            statusText = "ALERT";
        }
        /* Full-day volume comparison ONLY */
        else if (row.weekly_avg && row.live_volume > row.weekly_avg * 1.5) {
            statusClass = "status-high";
            statusText = "VERY HIGH VOL";
        }
        else if (row.weekly_avg && row.live_volume > row.weekly_avg) {
            statusClass = "status-high";
            statusText = "HIGH VOL";
        }

        tr.className = statusClass;

        tr.innerHTML = `
            <td>${row.symbol}</td>
            <td class="num">${format(row.live_volume)}</td>
            <td class="num">${format(row.prev_day)}</td>
            <td class="num">${format(row.weekly_avg)}</td>
            <td class="num">${format(row.monthly_avg)}</td>
            <td class="num">${row.volume_intensity || "WAITING"}</td>
            <td class="${statusClass}">${statusText}</td>
        `;

        tr.addEventListener("click", () => openChart(row.symbol));
        tr.style.cursor = "pointer";

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
        const div = document.createElement("div");
        div.className = "log";
        div.textContent = `[${log.time}] ${log.message}`;
        logBox.appendChild(div);

        // 🔔 POPUP for new alert
        if (
            log.message.includes("ALERT TRIGGERED") &&
            log.message !== lastAlertSeen
        ) {
            lastAlertSeen = log.message;
            alert(log.message);
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
            alert("Please enter a value / multiplier");
            return;
        }
        payload.right_value = parseFloat(rightValueRaw);
    }

    await fetch("/add-alert", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    });

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

    const chart = LightweightCharts.createChart(container, {
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
        crosshair: {
            mode: LightweightCharts.CrosshairMode.Normal,
            vertLine: {
                color: "#64748b",
                width: 1,
                style: LightweightCharts.LineStyle.Dashed,
                labelBackgroundColor: "#020617",
            },
            horzLine: {
                color: "#64748b",
                width: 1,
                style: LightweightCharts.LineStyle.Dashed,
                labelBackgroundColor: "#020617",
            },
        },
        timeScale: {
            timeVisible: true,
            secondsVisible: false,
            borderColor: "#1f2937",
        },
        rightPriceScale: {
            scaleMargins: {
                top: 0.15,
                bottom: 0.15,
            },
            borderColor: "#1f2937",
        },
        handleScroll: {
            mouseWheel: true,
            pressedMouseMove: true,
        },
        handleScale: {
            axisPressedMouseMove: true,
            mouseWheel: true,
            pinch: true,
        },
    });

    const volumeSeries = chart.addSeries(
        LightweightCharts.HistogramSeries,
        {
            color: "#3b82f6",
            priceFormat: { type: "volume" },
            priceScaleId: "right",
        }
    );

    const res = await fetch(`/historical/${symbol}`);
    const historical = await res.json();

    if (!historical || historical.length === 0) {
        console.warn("No historical data for", symbol);
        return;
    }

    volumeSeries.setData(historical);
    chart.timeScale().fitContent();

    window.addEventListener("resize", () => {
        chart.applyOptions({
            width: container.clientWidth,
            height: container.clientHeight,
        });
    });
}
function closeChart() {
    document.getElementById("chartModal").classList.add("hidden");
}

/* ================= HELPERS ================= */

function format(val) {
    if (val === null || val === undefined) return "-";
    return val.toLocaleString();
}

/* ================= POLLING ================= */

setInterval(fetchMarketData, 1000);
setInterval(fetchLogs, 1500);