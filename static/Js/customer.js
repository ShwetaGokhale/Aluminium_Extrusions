document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("customerForm");
    const customerIdDisplay = document.getElementById("customer_id_display");
    const dateField = document.getElementById("date");

    // ---------------- Set Today's Date ----------------
    if (!window.editMode && dateField) {
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

    // ---------------- Fetch Next Customer ID ----------------
    async function fetchNextCustomerId() {
        if (window.editMode) return; // Don't fetch in edit mode
        
        try {
            const response = await fetch('/extrusions/api/customers/?action=get_next_id');
            const data = await response.json();
            
            if (data.success && data.next_customer_id) {
                if (customerIdDisplay) {
                    customerIdDisplay.value = data.next_customer_id;
                }
            }
        } catch (error) {
            console.error('Error fetching next Customer ID:', error);
        }
    }

    // ---------------- Form Submission (No Validation) ----------------
    if (form) {
        form.addEventListener("submit", async function (e) {
            e.preventDefault();

            const formData = new FormData(form);

            let payload = {
                date: formData.get("date"),
                name: formData.get("name") || "",
                customer_type: formData.get("customer_type") || "",
                contact_no: formData.get("contact_no") || "",
                contact_person: formData.get("contact_person") || "",
                address: formData.get("address") || ""
            };

            // Debug: Log payload
            console.log("Payload being sent:", payload);

            try {
                let url, method;
                if (window.editMode) {
                    url = `/extrusions/api/customers/${window.customerId}/`;
                    method = "POST";
                } else {
                    url = "/extrusions/api/customers/";
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
                        showMessage("success", "Customer updated successfully!");
                        // Redirect to list page after 1 second
                        setTimeout(() => window.location.href = '/extrusions/customers/', 1000);
                    } else if (result.created) {
                        showMessage("success", `Customer created successfully! Customer ID: ${result.customer.customer_id}`);
                        // Redirect to list page after 1 second
                        setTimeout(() => window.location.href = '/extrusions/customers/', 1000);
                    } else {
                        showMessage("success", "Customer saved successfully!");
                        // Redirect to list page after 1 second
                        setTimeout(() => window.location.href = '/extrusions/customers/', 1000);
                    }
                } else {
                    showMessage("error", result.message || "Failed to save customer");
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

    // Initial load: Fetch next Customer ID if in create mode
    if (!window.editMode) {
        fetchNextCustomerId();
    }
});