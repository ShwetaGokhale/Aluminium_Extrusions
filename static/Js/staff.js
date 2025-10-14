document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("staffForm");
    const staffIdDisplay = document.getElementById("staff_id_display");

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

    // ---------------- Fetch Next Staff ID ----------------
    async function fetchNextStaffId() {
        if (window.editMode) return; // Don't fetch in edit mode

        try {
            const response = await fetch('/extrusions/api/staff/?action=get_next_id');
            const data = await response.json();

            if (data.success && data.next_staff_id) {
                if (staffIdDisplay) {
                    staffIdDisplay.value = data.next_staff_id;
                }
            }
        } catch (error) {
            console.error('Error fetching next Staff ID:', error);
        }
    }

    // ---------------- Validate Form ----------------
    function validateForm() {
        const date = document.getElementById("date").value;
        const staffRegisterNo = document.getElementById("staff_register_no").value.trim();
        const firstName = document.getElementById("first_name").value.trim();
        const lastName = document.getElementById("last_name").value.trim();
        const address = document.getElementById("address").value.trim();
        const contactNo = document.getElementById("contact_no").value.trim();
        const designation = document.getElementById("designation").value.trim();
        const shiftAssigned = document.getElementById("shift_assigned").value.trim();

        if (!date) {
            showMessage("error", "Date is required");
            return false;
        }

        if (!staffRegisterNo) {
            showMessage("error", "Staff Register No is required");
            return false;
        }

        if (!firstName) {
            showMessage("error", "First Name is required");
            return false;
        }

        if (!lastName) {
            showMessage("error", "Last Name is required");
            return false;
        }

        if (!address) {
            showMessage("error", "Address is required");
            return false;
        }

        if (!contactNo) {
            showMessage("error", "Contact No is required");
            return false;
        }

        // Validate contact number format (basic validation)
        if (contactNo.length < 10) {
            showMessage("error", "Contact number must be at least 10 digits");
            return false;
        }

        if (!designation) {
            showMessage("error", "Designation is required");
            return false;
        }

        if (!shiftAssigned) {
            showMessage("error", "Shift Assigned is required");
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
                date: formData.get("date"),
                staff_register_no: formData.get("staff_register_no"),
                first_name: formData.get("first_name"),
                last_name: formData.get("last_name"),
                address: formData.get("address"),
                contact_no: formData.get("contact_no"),
                designation: formData.get("designation"),
                shift_assigned: formData.get("shift_assigned"),
                assigned_to_press: formData.get("assigned_to_press") || null
            };

            // Debug: Log payload
            console.log("Payload being sent:", payload);

            try {
                let url, method;
                if (window.editMode) {
                    url = `/extrusions/api/staff/${window.staffId}/`;
                    method = "POST";
                } else {
                    url = "/extrusions/api/staff/";
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
                        showMessage("success", "Staff updated successfully!");
                        // Redirect to list page after 1 second
                        setTimeout(() => window.location.href = '/extrusions/staff/', 1000);
                    } else if (result.created) {
                        showMessage("success", `Staff created successfully! Staff ID: ${result.staff.staff_id}`);
                        // Redirect to list page after 1 second
                        setTimeout(() => window.location.href = '/extrusions/staff/', 1000);
                    } else {
                        showMessage("success", "Staff saved successfully!");
                        // Redirect to list page after 1 second
                        setTimeout(() => window.location.href = '/extrusions/staff/', 1000);
                    }
                } else {
                    showMessage("error", result.message || "Failed to save staff");
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
        });
    }

    // Initial load: Fetch next Staff ID if in create mode
    if (!window.editMode) {
        fetchNextStaffId();
    }
});