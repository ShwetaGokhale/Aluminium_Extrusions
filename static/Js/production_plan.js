document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("productionPlanForm");
    const productionPlanIdDisplay = document.getElementById("production_plan_id_display");
    const dateField = document.getElementById("date");
    const custRequisitionId = document.getElementById("cust_requisition_id");
    const customerName = document.getElementById("customer_name");
    const dieRequisition = document.getElementById("die_requisition");
    const dieNo = document.getElementById("die_no");
    const wtRange = document.getElementById("wt_range");
    const cutLength = document.getElementById("cut_length");
    const wtPerPiece = document.getElementById("wt_per_piece");

    // ---------------- Set Today's Date ----------------
    if (!window.editMode && dateField && !dateField.value) {
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

    // ---------------- Fetch Next Production Plan ID ----------------
    async function fetchNextProductionPlanId() {
        if (window.editMode) return; // Don't fetch in edit mode
        
        try {
            const response = await fetch('/planning/api/production-plans/?action=get_next_id');
            const data = await response.json();
            
            if (data.success && data.next_production_plan_id) {
                if (productionPlanIdDisplay) {
                    productionPlanIdDisplay.value = data.next_production_plan_id;
                }
            }
        } catch (error) {
            console.error('Error fetching next Production Plan ID:', error);
        }
    }

    // ---------------- Auto-populate Customer Name ----------------
    if (custRequisitionId) {
        custRequisitionId.addEventListener("change", async function () {
            const requisitionId = this.value;

            customerName.value = '';

            if (!requisitionId) return;

            try {
                const response = await fetch(`/planning/api/production-plans/?action=get_customer_name&requisition_id=${requisitionId}`);
                const data = await response.json();

                if (data.success && data.customer_name) {
                    customerName.value = data.customer_name;
                } else {
                    showMessage("error", "Error loading customer name");
                }
            } catch (error) {
                console.error('Error fetching customer name:', error);
                showMessage("error", "Error loading customer name");
            }
        });
    }

    // ---------------- Auto-populate Die Requisition fields ----------------
    if (dieRequisition) {
        dieRequisition.addEventListener("change", async function () {
            const dieReqId = this.value;

            dieNo.value = '';
            wtRange.value = '';
            cutLength.value = '';
            wtPerPiece.value = '';

            if (!dieReqId) return;

            try {
                const response = await fetch(`/planning/api/production-plans/?action=get_die_requisition_details&die_requisition_id=${dieReqId}`);
                const data = await response.json();

                if (data.success && data.die_requisition) {
                    dieNo.value = data.die_requisition.die_no || '';
                    wtRange.value = data.die_requisition.wt_range || '';
                    cutLength.value = data.die_requisition.cut_length || '';
                    wtPerPiece.value = data.die_requisition.present_wt || '';
                } else {
                    showMessage("error", "Error loading die requisition details");
                }
            } catch (error) {
                console.error('Error fetching die requisition details:', error);
                showMessage("error", "Error loading die requisition details");
            }
        });
    }

    // ---------------- Validate Form (Only Press is required) ----------------
    function validateForm() {
        const press = document.getElementById("press").value;

        if (!press) {
            showMessage("error", "Press is required");
            return false;
        }

        return true;
    }

    // ---------------- Form Submit ----------------
    if (form) {
        form.addEventListener("submit", async function (e) {
            e.preventDefault();

            if (!validateForm()) return;

            const formData = new FormData(form);

            let payload = {
                date: formData.get("date"),
                press: formData.get("press"),
                shift: formData.get("shift") || "",
                cust_requisition_id: formData.get("cust_requisition_id") || "",
                customer_name: formData.get("customer_name") || "",
                die_requisition: formData.get("die_requisition") || "",
                die_no: formData.get("die_no") || "",
                wt_range: formData.get("wt_range") || "",
                cut_length: formData.get("cut_length") || "",
                wt_per_piece: formData.get("wt_per_piece") || "0",
                qty: formData.get("qty") || ""
            };

            console.log("Payload being sent:", payload);

            try {
                let url, method;
                if (window.editMode) {
                    url = `/planning/api/production-plans/${window.planId}/`;
                    method = "POST";
                } else {
                    url = "/planning/api/production-plans/";
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
                console.log("Response:", responseText);

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
                        showMessage("success", "Production Plan updated successfully!");
                        // Redirect to list page after 1 second
                        setTimeout(() => window.location.href = '/planning/production-plans/', 1000);
                    } else if (result.created) {
                        showMessage("success", `Production Plan created successfully! ID: ${result.plan.production_plan_id}`);
                        // Redirect to list page after 1 second
                        setTimeout(() => window.location.href = '/planning/production-plans/', 1000);
                    } else {
                        showMessage("success", "Production Plan saved successfully!");
                        // Redirect to list page after 1 second
                        setTimeout(() => window.location.href = '/planning/production-plans/', 1000);
                    }
                } else {
                    showMessage("error", result.message || "Failed to save production plan");
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

    // ---------------- Initial Load ----------------
    if (!window.editMode) {
        fetchNextProductionPlanId();
    } else {
        if (custRequisitionId && custRequisitionId.value) {
            custRequisitionId.dispatchEvent(new Event('change'));
        }
        if (dieRequisition && dieRequisition.value) {
            dieRequisition.dispatchEvent(new Event('change'));
        }
    }
});