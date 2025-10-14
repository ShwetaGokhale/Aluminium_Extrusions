document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("alloyForm");
    const alloyIdDisplay = document.getElementById("alloy_id_display");

    // ---------------- Popup Message ----------------
    function showMessage(type, text) {
        const popup = document.getElementById("popupMessage");
        if (!popup) return;

        popup.textContent = text;
        popup.className = "popup-message";
        if (type === "error") popup.classList.add("error");

        popup.classList.remove("hidden");
        requestAnimationFrame(() => popup.classList.add("show"));

        setTimeout(() => {
            popup.classList.remove("show");
            setTimeout(() => popup.classList.add("hidden"), 500);
        }, 3000);
    }

    // ---------------- Fetch Next Alloy ID ----------------
    async function fetchNextAlloyId() {
        if (window.editMode) return; // Don't fetch in edit mode
        
        try {
            const response = await fetch('/extrusions/api/alloys/?action=get_next_id');
            const data = await response.json();
            
            if (data.success && data.next_alloy_id) {
                if (alloyIdDisplay) {
                    alloyIdDisplay.value = data.next_alloy_id;
                }
            }
        } catch (error) {
            console.error('Error fetching next Alloy ID:', error);
        }
    }

    // ---------------- Validate Form ----------------
    function validateForm() {
        const date = document.getElementById("date").value;
        const alloyCode = document.getElementById("alloy_code").value.trim();
        const temperDesignation = document.getElementById("temper_designation").value.trim();
        const temperCode = document.getElementById("temper_code").value.trim();
        const tensileStrength = document.getElementById("tensile_strength").value.trim();
        const material = document.getElementById("material").value.trim();
        const siliconPercent = document.getElementById("silicon_percent").value.trim();
        const copperPercent = document.getElementById("copper_percent").value.trim();

        if (!date) {
            showMessage("error", "Date is required");
            return false;
        }

        if (!alloyCode) {
            showMessage("error", "Alloy Code is required");
            return false;
        }

        if (!temperDesignation) {
            showMessage("error", "Temper Designation is required");
            return false;
        }

        if (!temperCode) {
            showMessage("error", "Temper Code is required");
            return false;
        }

        if (!tensileStrength || parseFloat(tensileStrength) <= 0) {
            showMessage("error", "Valid Tensile Strength is required (must be greater than 0)");
            return false;
        }

        if (!material) {
            showMessage("error", "Material is required");
            return false;
        }

        if (!siliconPercent || parseFloat(siliconPercent) < 0 || parseFloat(siliconPercent) > 100) {
            showMessage("error", "Silicon percentage must be between 0 and 100");
            return false;
        }

        if (!copperPercent || parseFloat(copperPercent) < 0 || parseFloat(copperPercent) > 100) {
            showMessage("error", "Copper percentage must be between 0 and 100");
            return false;
        }

        return true;
    }

    if (form) {
        form.addEventListener("submit", async function (e) {
            e.preventDefault();

            if (!validateForm()) return;

            const formData = new FormData(form);

            // Convert FormData to JSON for API
            let payload = {
                date: formData.get("date"),
                alloy_code: formData.get("alloy_code"),
                temper_designation: formData.get("temper_designation"),
                temper_code: formData.get("temper_code"),
                tensile_strength: formData.get("tensile_strength"),
                material: formData.get("material"),
                silicon_percent: formData.get("silicon_percent"),
                copper_percent: formData.get("copper_percent")
            };

            // Debug: Log payload
            console.log("Payload being sent:", payload);

            await submitForm(payload);
        });
    }

    async function submitForm(payload) {
        try {
            let url, method;
            if (window.editMode) {
                url = `/extrusions/api/alloys/${window.alloyId}/`;
                method = "POST";
            } else {
                url = "/extrusions/api/alloys/";
                method = "POST";
            }

            const response = await fetch(url, {
                method: method,
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]')?.value || ''
                },
                body: JSON.stringify(payload)
            });

            const responseText = await response.text();
            console.log("Response:", responseText); // Debug log
            
            const contentType = response.headers.get('content-type');

            if (!contentType || !contentType.includes('application/json')) {
                if (response.status === 404) {
                    showMessage("error", "API endpoint not found. Check your URL configuration.");
                } else if (response.status === 500) {
                    showMessage("error", "Server error. Please try again later.");
                    console.error("Server error response:", responseText);
                } else {
                    showMessage("error", "Server returned an unexpected response.");
                    console.error("Unexpected response:", responseText);
                }
                return;
            }

            let result;
            try {
                result = JSON.parse(responseText);
            } catch (jsonError) {
                showMessage("error", "Invalid response from server");
                console.error("JSON Parse Error:", jsonError);
                return;
            }

            if (result.success) {
                if (result.updated) {
                    showMessage("success", "Alloy updated successfully!");
                    // Redirect to list page after 1 second
                    setTimeout(() => window.location.href = '/extrusions/alloys/', 1000);
                } else if (result.created) {
                    showMessage("success", `Alloy created successfully! Alloy ID: ${result.alloy.alloy_id}`);
                    // Redirect to list page after 1 second
                    setTimeout(() => window.location.href = '/extrusions/alloys/', 1000);
                } else {
                    showMessage("success", "Alloy saved successfully!");
                    // Redirect to list page after 1 second
                    setTimeout(() => window.location.href = '/extrusions/alloys/', 1000);
                }
            } else {
                showMessage("error", result.message || "Failed to save alloy");
                console.error("Server error:", result);
            }

        } catch (err) {
            console.error("Fetch error:", err);
            if (err.name === 'TypeError' && err.message.includes('fetch')) {
                showMessage("error", "Network error. Check if server is running.");
            } else {
                showMessage("error", "An error occurred. Please try again.");
            }
        }
    }

    // Initial load: Fetch next Alloy ID if in create mode
    if (!window.editMode) {
        fetchNextAlloyId();
    }
});