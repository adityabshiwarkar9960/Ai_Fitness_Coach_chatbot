/**
 * FitCoach AI - Workout & Diet Plan Generator Client Controller
 */

let currentWorkoutPlan = null;
let currentDietPlan = null;

document.addEventListener("DOMContentLoaded", () => {
    // Configure Marked
    if (window.marked) {
        marked.setOptions({ breaks: true, gfm: true });
    }

    // ==========================================
    // WORKOUT PLAN GENERATOR
    // ==========================================
    const workoutForm = document.getElementById("workout-gen-form");
    const workoutLoading = document.getElementById("workout-loading");
    const workoutResultContainer = document.getElementById("workout-result-container");
    const workoutContentDiv = document.getElementById("workout-plan-content");
    const saveWorkoutBtn = document.getElementById("save-workout-btn");

    if (workoutForm) {
        workoutForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            
            const goal = document.getElementById("workout-goal").value;
            const experience_level = document.getElementById("workout-level").value;
            const days_per_week = document.getElementById("workout-days").value;
            const equipment = document.getElementById("workout-equipment").value;
            const injury_notes = document.getElementById("workout-injury").value.trim() || "None";

            if (workoutLoading) workoutLoading.classList.remove("d-none");
            if (workoutResultContainer) workoutResultContainer.classList.add("d-none");

            try {
                const response = await fetch("/api/generate-workout", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        goal, experience_level, days_per_week, equipment, injury_notes
                    })
                });

                const data = await response.json();
                if (workoutLoading) workoutLoading.classList.add("d-none");

                if (data.success && data.plan) {
                    currentWorkoutPlan = data.plan;
                    currentWorkoutPlan.goal = goal;
                    currentWorkoutPlan.experience_level = experience_level;
                    currentWorkoutPlan.days_per_week = days_per_week;
                    currentWorkoutPlan.equipment = equipment;

                    if (workoutContentDiv) {
                        workoutContentDiv.innerHTML = marked.parse(data.plan.content);
                    }
                    if (workoutResultContainer) {
                        workoutResultContainer.classList.remove("d-none");
                        workoutResultContainer.scrollIntoView({ behavior: "smooth" });
                    }
                    if (window.showToast) showToast("Workout plan generated successfully!", "success");
                } else {
                    alert("Error: " + (data.error || "Failed to generate workout plan"));
                }
            } catch (err) {
                if (workoutLoading) workoutLoading.classList.add("d-none");
                console.error("Workout generation error:", err);
                alert("An error occurred while communicating with the server.");
            }
        });
    }

    if (saveWorkoutBtn) {
        saveWorkoutBtn.addEventListener("click", async () => {
            if (!currentWorkoutPlan) return;
            try {
                const res = await fetch("/api/save-workout", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        title: currentWorkoutPlan.title,
                        goal: currentWorkoutPlan.goal,
                        experience_level: currentWorkoutPlan.experience_level,
                        days_per_week: currentWorkoutPlan.days_per_week,
                        equipment: currentWorkoutPlan.equipment,
                        plan_content: currentWorkoutPlan.content,
                        structured_data: currentWorkoutPlan.structured
                    })
                });
                const data = await res.json();
                if (data.success) {
                    saveWorkoutBtn.innerHTML = '<i class="fa-solid fa-check me-1"></i> Saved to Library';
                    saveWorkoutBtn.classList.replace("btn-fit-primary", "btn-success");
                    saveWorkoutBtn.disabled = true;
                    if (window.showToast) showToast("Saved to your Library!", "success");
                }
            } catch (err) {
                console.error("Save workout error:", err);
            }
        });
    }


    // ==========================================
    // DIET & MEAL PLAN GENERATOR
    // ==========================================
    const dietForm = document.getElementById("diet-gen-form");
    const dietLoading = document.getElementById("diet-loading");
    const dietResultContainer = document.getElementById("diet-result-container");
    const dietContentDiv = document.getElementById("diet-plan-content");
    const saveDietBtn = document.getElementById("save-diet-btn");

    if (dietForm) {
        dietForm.addEventListener("submit", async (e) => {
            e.preventDefault();

            const goal = document.getElementById("diet-goal").value;
            const diet_type = document.getElementById("diet-type").value;
            const target_calories = document.getElementById("diet-calories").value;
            const allergies = document.getElementById("diet-allergies").value.trim() || "None";
            const meals_per_day = document.getElementById("diet-meals").value;

            if (dietLoading) dietLoading.classList.remove("d-none");
            if (dietResultContainer) dietResultContainer.classList.add("d-none");

            try {
                const response = await fetch("/api/generate-diet", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        goal, diet_type, target_calories, allergies, meals_per_day
                    })
                });

                const data = await response.json();
                if (dietLoading) dietLoading.classList.add("d-none");

                if (data.success && data.plan) {
                    currentDietPlan = data.plan;
                    currentDietPlan.goal = goal;
                    currentDietPlan.diet_type = diet_type;

                    if (dietContentDiv) {
                        dietContentDiv.innerHTML = marked.parse(data.plan.content);
                    }
                    if (dietResultContainer) {
                        dietResultContainer.classList.remove("d-none");
                        dietResultContainer.scrollIntoView({ behavior: "smooth" });
                    }
                    if (window.showToast) showToast("Meal plan generated successfully!", "success");
                } else {
                    alert("Error: " + (data.error || "Failed to generate diet plan"));
                }
            } catch (err) {
                if (dietLoading) dietLoading.classList.add("d-none");
                console.error("Diet generation error:", err);
                alert("An error occurred while generating diet plan.");
            }
        });
    }

    if (saveDietBtn) {
        saveDietBtn.addEventListener("click", async () => {
            if (!currentDietPlan) return;
            try {
                const res = await fetch("/api/save-diet", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        title: currentDietPlan.title,
                        goal: currentDietPlan.goal,
                        diet_type: currentDietPlan.diet_type,
                        target_calories: currentDietPlan.target_calories,
                        protein_g: currentDietPlan.protein_g,
                        carbs_g: currentDietPlan.carbs_g,
                        fats_g: currentDietPlan.fats_g,
                        plan_content: currentDietPlan.content,
                        structured_data: currentDietPlan.structured
                    })
                });
                const data = await res.json();
                if (data.success) {
                    saveDietBtn.innerHTML = '<i class="fa-solid fa-check me-1"></i> Saved to Library';
                    saveDietBtn.classList.replace("btn-fit-primary", "btn-success");
                    saveDietBtn.disabled = true;
                    if (window.showToast) showToast("Meal plan saved to Library!", "success");
                }
            } catch (err) {
                console.error("Save diet error:", err);
            }
        });
    }
});

// Helper: Print / Export plan container
function printPlan(elementId) {
    const content = document.getElementById(elementId);
    if (!content) return;
    const printWindow = window.open('', '', 'height=700,width=900');
    printWindow.document.write('<html><head><title>FitCoach AI Plan</title>');
    printWindow.document.write('<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">');
    printWindow.document.write('<style>body { font-family: sans-serif; padding: 30px; color: #111; } table { width: 100%; margin: 15px 0; border-collapse: collapse; } th, td { border: 1px solid #ddd; padding: 8px; text-align: left; } th { background-color: #f2f2f2; } </style>');
    printWindow.document.write('</head><body>');
    printWindow.document.write(content.innerHTML);
    printWindow.document.write('</body></html>');
    printWindow.document.close();
    printWindow.focus();
    setTimeout(() => {
        printWindow.print();
        printWindow.close();
    }, 500);
}
