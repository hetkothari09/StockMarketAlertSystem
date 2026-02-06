document.getElementById("alertForm").addEventListener("submit", async (e) => {
  e.preventDefault();

  const formData = new FormData(e.target);
  const payload = Object.fromEntries(formData.entries());

  payload.is_active = true;
  payload.threshold_value = parseFloat(payload.threshold_value);

  await fetch("/add/alerts", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });

  alert("Alert created successfully!");
});
