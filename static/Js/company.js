document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("companyForm");
    const shiftsBody = document.getElementById("shiftsTableBody");
    const pressesBody = document.getElementById("pressesTableBody");
    const dateField = document.getElementById("date");

    // ---------------- Set today's date as default (non-editable) ----------------
    if (dateField && !dateField.value) {
        const today = new Date().toISOString().split('T')[0];
        dateField.value = today;
    }

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

    // ---------------- Initialize Example Rows ----------------
    function initExampleRows() {
        if (!window.editMode) {
            if (shiftsBody) {
                shiftsBody.innerHTML = `
                    <tr class="example-row" style="background:#f9f9f9; color:#888;">
                        <td><input type="text" placeholder="Morning Shift" disabled></td>
                        <td><input type="text" placeholder="9:00 AM - 5:00 PM" disabled></td>
                        <td></td>
                    </tr>
                `;
            }
            if (pressesBody) {
                pressesBody.innerHTML = `
                    <tr class="example-row" style="background:#f9f9f9; color:#888;">
                        <td><input type="text" placeholder="Hydraulic Press 1" disabled></td>
                        <td><input type="text" placeholder="500 tons" disabled></td>
                        <td></td>
                    </tr>
                `;
            }
        }
    }

    // ---------------- Load Edit Data ----------------
    function loadEditData() {
        if (window.editMode && window.shiftsData && window.pressesData) {
            window.shiftsData.forEach(shift => addShiftRow(shift));
            window.pressesData.forEach(press => addPressRow(press));
        }
    }

    // ---------------- Add/Delete Rows Of Shifts ----------------
    function addShiftRow(data = {}) {
        const row = document.createElement("tr");
        if (data.id) row.dataset.id = data.id;

        row.innerHTML = `
            <td><input type="text" name="shift_name[]" placeholder="Enter shift name" value="${data.name || ''}"></td>
            <td><input type="text" name="shift_timing[]" placeholder="e.g., 9:00 AM - 5:00 PM" value="${data.timing || ''}"></td>
            <td>
                <button type="button" class="delete-row">
                    <i class="fa-solid fa-trash"></i>
                </button>
            </td>
        `;

        const exampleRow = shiftsBody.querySelector(".example-row");
        if (exampleRow) exampleRow.remove();

        shiftsBody.appendChild(row);
    }

    // ---------------- Add/Delete Rows Of Presses ----------------
    function addPressRow(data = {}) {
        const row = document.createElement("tr");
        if (data.id) row.dataset.id = data.id;

        row.innerHTML = `
            <td><input type="text" name="press_name[]" placeholder="Enter press name" value="${data.name || ''}"></td>
            <td><input type="text" name="press_capacity[]" placeholder="e.g., 500 tons, 1000 kg/hr" value="${data.capacity || ''}"></td>
            <td>
                <button type="button" class="delete-row">
                    <i class="fa-solid fa-trash"></i>
                </button>
            </td>
        `;

        const exampleRow = pressesBody.querySelector(".example-row");
        if (exampleRow) exampleRow.remove();

        pressesBody.appendChild(row);
    }

    // ---------------- Add Row Buttons Of Shifts ----------------
    document.getElementById("addShiftBtn")?.addEventListener("click", e => {
        e.preventDefault();
        addShiftRow();
    });

    // ---------------- Add Row Buttons Of Presses ----------------
    document.getElementById("addPressBtn")?.addEventListener("click", e => {
        e.preventDefault();
        addPressRow();
    });

    // ---------------- Delete Row Buttons Of Shifts & Presses ----------------
    document.addEventListener("click", function (e) {
        const btn = e.target.closest(".delete-row");
        if (btn) {
            e.target.closest("tr").remove();

            if (shiftsBody && shiftsBody.children.length === 0 && !window.editMode) {
                shiftsBody.innerHTML = `
                    <tr class="example-row" style="background:#f9f9f9; color:#888;">
                        <td><input type="text" placeholder="Morning Shift" disabled></td>
                        <td><input type="text" placeholder="9:00 AM - 5:00 PM" disabled></td>
                        <td></td>
                    </tr>
                `;
            }

            if (pressesBody && pressesBody.children.length === 0 && !window.editMode) {
                pressesBody.innerHTML = `
                    <tr class="example-row" style="background:#f9f9f9; color:#888;">
                        <td><input type="text" placeholder="Hydraulic Press 1" disabled></td>
                        <td><input type="text" placeholder="500 tons" disabled></td>
                        <td></td>
                    </tr>
                `;
            }
        }
    });

    // ---------------- Validate Form ----------------
    function validateForm() {
        const name = document.getElementById("name").value.trim();

        if (!name) {
            showMessage("error", "Company name is required");
            return false;
        }

        return true;
    }

    if (form) {
        form.addEventListener("submit", async function (e) {
            e.preventDefault();

            if (!validateForm()) return;

            const formData = new FormData(form);

            let payload = {
                name: formData.get("name"),
                date: formData.get("date"),
                description: formData.get("description") || "",
                address: formData.get("address") || "",
                contact_no: formData.get("contact_no") || "",
                shifts: [],
                presses: []
            };

            if (shiftsBody) {
                shiftsBody.querySelectorAll("tr:not(.example-row)").forEach(row => {
                    const nameInput = row.querySelector("input[name='shift_name[]']");
                    const timingInput = row.querySelector("input[name='shift_timing[]']");

                    if (nameInput && timingInput && nameInput.value.trim() && timingInput.value.trim()) {
                        payload.shifts.push({
                            id: row.dataset.id || null,
                            name: nameInput.value.trim(),
                            timing: timingInput.value.trim()
                        });
                    }
                });
            }

            if (pressesBody) {
                pressesBody.querySelectorAll("tr:not(.example-row)").forEach(row => {
                    const nameInput = row.querySelector("input[name='press_name[]']");
                    const capacityInput = row.querySelector("input[name='press_capacity[]']");

                    if (nameInput && capacityInput && nameInput.value.trim() && capacityInput.value.trim()) {
                        payload.presses.push({
                            id: row.dataset.id || null,
                            name: nameInput.value.trim(),
                            capacity: capacityInput.value.trim()
                        });
                    }
                });
            }

            // Debug: Log payload
            console.log("Payload being sent:", payload);

            try {
                let url, method;
                if (window.editMode) {
                    url = `/extrusions/api/companies/${window.companyId}/`;
                    method = "POST";
                } else {
                    url = "/extrusions/api/companies/";
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
                    } else if (responseText.includes('csrfmiddlewaretoken')) {
                        showMessage("error", "CSRF token error. Please refresh the page.");
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
                        showMessage("success", "Company updated successfully!");
                        // Redirect to list page after 1 second
                        setTimeout(() => window.location.href = '/extrusions/companies/', 1000);
                    } else if (result.created) {
                        showMessage("success", "Company created successfully!");
                        // Redirect to list page after 1 second
                        setTimeout(() => window.location.href = '/extrusions/companies/', 1000);
                    } else {
                        showMessage("success", "Company saved successfully!");
                        // Redirect to list page after 1 second
                        setTimeout(() => window.location.href = '/extrusions/companies/', 1000);
                    }
                } else {
                    showMessage("error", "Error: " + (result.message || "Failed to save"));
                    console.error("Server error:", result);
                }

            } catch (err) {
                console.error("Fetch error:", err);
                if (err.name === 'TypeError' && err.message.includes('fetch')) {
                    showMessage("error", "Network error. Check if server is running.");
                } else {
                    showMessage("error", "Request failed: " + err.message);
                }
            }
        });
    }

    // ---------------- Initialize ----------------
    initExampleRows();
    loadEditData();
});