/**
 * FitCoach AI - Progress Tracker Controller
 */

let progressChartInstance = null;

document.addEventListener("DOMContentLoaded", () => {
    const progressForm = document.getElementById("progress-log-form");

    // Initialize date picker to today
    const dateInput = document.getElementById("log-date");
    if (dateInput && !dateInput.value) {
        dateInput.value = new Date().toISOString().split('T')[0];
    }

    if (progressForm) {
        progressForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const log_date = document.getElementById("log-date").value;
            const weight = document.getElementById("log-weight").value;
            const body_fat = document.getElementById("log-body-fat").value;
            const chest = document.getElementById("log-chest").value;
            const waist = document.getElementById("log-waist").value;
            const arms = document.getElementById("log-arms").value;
            const notes = document.getElementById("log-notes").value;

            try {
                const res = await fetch("/api/progress", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        log_date, weight, body_fat, chest, waist, arms, notes
                    })
                });

                const data = await res.json();
                if (data.success) {
                    if (window.showToast) showToast("Progress entry logged!", "success");
                    setTimeout(() => window.location.reload(), 800);
                } else {
                    alert("Error: " + (data.error || "Failed to log progress"));
                }
            } catch (err) {
                console.error("Progress log error:", err);
            }
        });
    }

    // Initialize Progress Chart if data exists
    initProgressChart();
});

async function initProgressChart() {
    const ctx = document.getElementById("progressChart");
    if (!ctx || !window.Chart) return;

    try {
        const res = await fetch("/api/progress");
        const data = await res.json();

        if (data.success && data.logs && data.logs.length > 0) {
            const labels = data.logs.map(l => l.log_date);
            const weights = data.logs.map(l => l.weight);
            const bodyFats = data.logs.map(l => l.body_fat || null);

            progressChartInstance = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [
                        {
                            label: 'Weight (kg)',
                            data: weights,
                            borderColor: '#00F5A0',
                            backgroundColor: 'rgba(0, 245, 160, 0.1)',
                            borderWidth: 3,
                            fill: true,
                            tension: 0.35,
                            yAxisID: 'y'
                        },
                        {
                            label: 'Body Fat (%)',
                            data: bodyFats,
                            borderColor: '#FF6B35',
                            backgroundColor: 'transparent',
                            borderWidth: 2,
                            borderDash: [5, 5],
                            tension: 0.35,
                            yAxisID: 'y1'
                        }
                    ]
                },
                options: {
                    responsive: true,
                    interaction: { mode: 'index', intersect: false },
                    scales: {
                        x: {
                            grid: { color: 'rgba(255, 255, 255, 0.05)' },
                            ticks: { color: '#94a3b8' }
                        },
                        y: {
                            type: 'linear',
                            display: true,
                            position: 'left',
                            title: { display: true, text: 'Weight (kg)', color: '#00F5A0' },
                            grid: { color: 'rgba(255, 255, 255, 0.05)' },
                            ticks: { color: '#94a3b8' }
                        },
                        y1: {
                            type: 'linear',
                            display: true,
                            position: 'right',
                            title: { display: true, text: 'Body Fat (%)', color: '#FF6B35' },
                            grid: { drawOnChartArea: false },
                            ticks: { color: '#94a3b8' }
                        }
                    },
                    plugins: {
                        legend: {
                            labels: { color: '#cbd5e1', font: { family: 'Inter', size: 12 } }
                        }
                    }
                }
            });
        }
    } catch (err) {
        console.error("Init progress chart error:", err);
    }
}

async function deleteProgressEntry(logId) {
    if (!confirm("Delete this progress entry?")) return;
    try {
        const res = await fetch(`/api/progress/${logId}`, { method: "DELETE" });
        const data = await res.json();
        if (data.success) {
            const row = document.getElementById(`log-row-${logId}`);
            if (row) row.remove();
            if (window.showToast) showToast("Entry deleted", "info");
        }
    } catch (err) {
        console.error("Delete progress error:", err);
    }
}
