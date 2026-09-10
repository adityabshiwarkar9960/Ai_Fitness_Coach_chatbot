/**
 * FitCoach AI - Fitness & Nutrition Calculators Controller
 */

let macroChartInstance = null;

document.addEventListener("DOMContentLoaded", () => {
    // 1. TDEE & Macro Calculator Form
    const tdeeForm = document.getElementById("tdee-calc-form");
    if (tdeeForm) {
        tdeeForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const weight = document.getElementById("tdee-weight").value;
            const height = document.getElementById("tdee-height").value;
            const age = document.getElementById("tdee-age").value;
            const gender = document.getElementById("tdee-gender").value;
            const activity_level = document.getElementById("tdee-activity").value;
            const goal = document.getElementById("tdee-goal").value;
            const dietary_preference = document.getElementById("tdee-diet").value;

            try {
                const res = await fetch("/api/calculate", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        type: "bmr_tdee", weight, height, age, gender, activity_level, goal, dietary_preference
                    })
                });
                const data = await res.json();
                if (data.success) {
                    renderTdeeResults(data);
                }
            } catch (err) {
                console.error("TDEE calculation error:", err);
            }
        });
    }

    // 2. One-Rep Max Form
    const ormForm = document.getElementById("orm-calc-form");
    if (ormForm) {
        ormForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const weight = document.getElementById("orm-weight").value;
            const reps = document.getElementById("orm-reps").value;

            try {
                const res = await fetch("/api/calculate", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        type: "one_rep_max", weight, reps
                    })
                });
                const data = await res.json();
                if (data.success) {
                    renderOrmResults(data.result);
                }
            } catch (err) {
                console.error("1RM calculation error:", err);
            }
        });
    }

    // 3. Hydration Form
    const waterForm = document.getElementById("water-calc-form");
    if (waterForm) {
        waterForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const weight = document.getElementById("water-weight").value;
            const activity_level = document.getElementById("water-activity").value;

            try {
                const res = await fetch("/api/calculate", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        type: "water", weight, activity_level
                    })
                });
                const data = await res.json();
                if (data.success) {
                    renderWaterResults(data.result);
                }
            } catch (err) {
                console.error("Water calculation error:", err);
            }
        });
    }

    // 4. Heart Rate Form
    const hrForm = document.getElementById("hr-calc-form");
    if (hrForm) {
        hrForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const age = document.getElementById("hr-age").value;

            try {
                const res = await fetch("/api/calculate", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        type: "heart_rate", age
                    })
                });
                const data = await res.json();
                if (data.success) {
                    renderHrResults(data.result);
                }
            } catch (err) {
                console.error("Heart rate calculation error:", err);
            }
        });
    }
});

function renderTdeeResults(data) {
    document.getElementById("res-bmr").innerText = `${data.bmr} kcal`;
    document.getElementById("res-tdee").innerText = `${data.tdee} kcal`;
    document.getElementById("res-target-cals").innerText = `${data.macros.target_calories} kcal`;

    document.getElementById("res-protein-g").innerText = `${data.macros.protein_g}g`;
    document.getElementById("res-carbs-g").innerText = `${data.macros.carbs_g}g`;
    document.getElementById("res-fats-g").innerText = `${data.macros.fats_g}g`;

    document.getElementById("tdee-results-card").classList.remove("d-none");

    // Render / Update Chart.js Macro Pie Chart
    const ctx = document.getElementById("macroPieChart");
    if (ctx && window.Chart) {
        if (macroChartInstance) {
            macroChartInstance.destroy();
        }
        macroChartInstance = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Protein', 'Carbohydrates', 'Healthy Fats'],
                datasets: [{
                    data: [data.macros.protein_cal, data.macros.carbs_cal, data.macros.fats_cal],
                    backgroundColor: ['#00F5A0', '#00D9F5', '#FF6B35'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { color: '#cbd5e1', font: { family: 'Inter', size: 12 } }
                    }
                },
                cutout: '70%'
            }
        });
    }
}

function renderOrmResults(data) {
    document.getElementById("res-1rm").innerText = `${data.one_rep_max} kg`;
    const tbody = document.getElementById("orm-table-body");
    if (tbody) {
        tbody.innerHTML = "";
        data.table.forEach(row => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td><strong>${row.pct}%</strong></td>
                <td>${row.reps} Rep${row.reps > 1 ? 's' : ''}</td>
                <td class="text-gradient-emerald fw-bold">${row.weight} kg</td>
            `;
            tbody.appendChild(tr);
        });
    }
    document.getElementById("orm-results-card").classList.remove("d-none");
}

function renderWaterResults(data) {
    document.getElementById("res-water-liters").innerText = `${data.liters} L`;
    document.getElementById("res-water-glasses").innerText = `${data.glasses} glasses`;
    document.getElementById("res-water-oz").innerText = `${data.ounces} oz`;
    document.getElementById("water-results-card").classList.remove("d-none");
}

function renderHrResults(data) {
    document.getElementById("res-max-hr").innerText = `${data.max_heart_rate} BPM`;
    const container = document.getElementById("hr-zones-list");
    if (container) {
        container.innerHTML = "";
        data.zones.forEach(z => {
            const card = document.createElement("div");
            card.className = "p-3 mb-2 rounded bg-dark border border-secondary border-opacity-25";
            card.innerHTML = `
                <div class="d-flex justify-content-between align-items-center mb-1">
                    <span class="fw-bold text-white">Zone ${z.zone}: ${z.name} (${z.pct})</span>
                    <span class="badge bg-success bg-opacity-25 text-success border border-success border-opacity-50">${z.min_hr} - ${z.max_hr} BPM</span>
                </div>
                <small class="text-muted">${z.benefit}</small>
            `;
            container.appendChild(card);
        });
    }
    document.getElementById("hr-results-card").classList.remove("d-none");
}
