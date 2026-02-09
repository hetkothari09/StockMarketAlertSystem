
// GLOBAL STATE


let latestData = [];

// MARKET DATA (TABLE + SYMBOL DROPDOWNS)

async function fetchMarketData() {
    const res = await fetch("/data");
    const data = await res.json();

    latestData = data;

    const tbody = document.getElementById("market-body");
    tbody.innerHTML = "";

    const alertSelect = document.getElementById("alert-symbol");
    const compareSelect = document.getElementById("compare-symbol");

    alertSelect.innerHTML = "";
    compareSelect.innerHTML = "";

    data.forEach(row => {
        const tr = document.createElement("tr");

        let statusClass = "status-normal";
        let statusText = "NORMAL";

        if (row.alert_hit) {
            statusClass = "status-spike";
            statusText = "ALERT HIT";
        } else if (row.weekly_avg && row.live_volume > row.weekly_avg) {
            statusClass = "status-high";
            statusText = "HIGH VOL";
        }

        tr.innerHTML = `
            <td>${row.symbol}</td>
            <td>${format(row.live_volume)}</td>
            <td>${format(row.prev_day)}</td>
            <td>${format(row.weekly_avg)}</td>
            <td>${format(row.monthly_avg)}</td>
            <td class="${statusClass}">${statusText}</td>
        `;

        tbody.appendChild(tr);

        // Alert Symbol Dropdown
        const opt1 = document.createElement("option");
        opt1.value = row.symbol;
        opt1.textContent = row.symbol;
        alertSelect.appendChild(opt1);

        // Compare Symbol Dropdown
        const opt2 = document.createElement("option");
        opt2.value = row.symbol;
        opt2.textContent = row.symbol;
        compareSelect.appendChild(opt2);
    });
}


//LOGS

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
    });
}

// ALERT CREATION (ADVANCED VOLUME ALERT)


async function createAlert() {
    const symbol = document.getElementById("alert-symbol").value;
    const operator = document.getElementById("alert-operator").value;
    const rightType = document.getElementById("alert-right-type").value;
    const rightValueRaw = document.getElementById("alert-right-value").value;

    const payload = {
        symbol: symbol,
        operator: operator,
        right_type: rightType
    };

    // Only attach right_value when required
    if (rightType === "FIXED" || rightType === "MULTIPLIER_WEEKLY") {
        if (!rightValueRaw) {
            alert("Please enter a value or multiplier");
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


// VOLUME COMPARISON 

function compareVolume() {
    const symbol = document.getElementById("compare-symbol").value;
    const row = latestData.find(r => r.symbol === symbol);

    if (!row || row.live_volume === undefined || row.live_volume === null) {
        document.getElementById("compare-result").innerHTML =
            "Live volume not available";
        return;
    }

    if (row.live_volume <= 0) {
        document.getElementById("compare-result").innerHTML =
            "Market closed — live volume is zero";
        return;
    }

    const weeklyDiff =
        ((row.live_volume - row.weekly_avg) / row.weekly_avg) * 100;

    const monthlyDiff =
        ((row.live_volume - row.monthly_avg) / row.monthly_avg) * 100;

    document.getElementById("compare-result").innerHTML = `
        <div>Live vs Weekly Avg: <b>${weeklyDiff.toFixed(2)}%</b></div>
        <div>Live vs Monthly Avg: <b>${monthlyDiff.toFixed(2)}%</b></div>
    `;
}


function format(val) {
    if (val === null || val === undefined || val === 0) return "-";
    return val.toLocaleString();
}


setInterval(fetchMarketData, 1000);
setInterval(fetchLogs, 1500);
