document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("supplierForm");
    const supplierIdDisplay = document.getElementById("supplier_id_display");

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

    // ---------------- Fetch Next Supplier ID ----------------
    async function fetchNextSupplierId() {
        if (window.editMode) return; // Don't fetch in edit mode
        
        try {
            const response = await fetch('/extrusions/api/suppliers/?action=get_next_id');
            const data = await response.json();
            
            if (data.success && data.next_supplier_id) {
                if (supplierIdDisplay) {
                    supplierIdDisplay.value = data.next_supplier_id;
                }
            }
        } catch (error) {
            console.error('Error fetching next Supplier ID:', error);
        }
    }

    // ---------------- Validate Form ----------------
    function validateForm() {
        const date = document.getElementById("date").value;
        const name = document.getElementById("name").value.trim();
        const supplierType = document.getElementById("supplier_type").value.trim();
        const contactNo = document.getElementById("contact_no").value.trim();
        const address = document.getElementById("address").value.trim();

        if (!date) {
            showMessage("error", "Date is required");
            return false;
        }

        if (!name) {
            showMessage("error", "Supplier name is required");
            return false;
        }

        if (!supplierType) {
            showMessage("error", "Supplier type is required");
            return false;
        }

        if (!contactNo) {
            showMessage("error", "Contact number is required");
            return false;
        }

        // Validate contact number format (basic validation)
        if (contactNo.length < 10) {
            showMessage("error", "Contact number must be at least 10 digits");
            return false;
        }

        if (!address) {
            showMessage("error", "Address is required");
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
                name: formData.get("name"),
                supplier_type: formData.get("supplier_type"),
                contact_no: formData.get("contact_no"),
                contact_person: formData.get("contact_person") || "",
                address: formData.get("address")
            };

            // Debug: Log payload
            console.log("Payload being sent:", payload);

            try {
                let url, method;
                if (window.editMode) {
                    url = `/extrusions/api/suppliers/${window.supplierId}/`;
                    method = "POST";
                } else {
                    url = "/extrusions/api/suppliers/";
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
                        showMessage("success", "Supplier updated successfully!");
                        // Redirect to list page after 1 second
                        setTimeout(() => window.location.href = '/extrusions/suppliers/', 1000);
                    } else if (result.created) {
                        showMessage("success", `Supplier created successfully! Supplier ID: ${result.supplier.supplier_id}`);
                        // Redirect to list page after 1 second
                        setTimeout(() => window.location.href = '/extrusions/suppliers/', 1000);
                    } else {
                        showMessage("success", "Supplier saved successfully!");
                        // Redirect to list page after 1 second
                        setTimeout(() => window.location.href = '/extrusions/suppliers/', 1000);
                    }
                } else {
                    showMessage("error", result.message || "Failed to save supplier");
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

    // Initial load: Fetch next Supplier ID if in create mode
    if (!window.editMode) {
        fetchNextSupplierId();
    }
});