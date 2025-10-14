document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("dieRequisitionForm");
    const dieRequisitionIdDisplay = document.getElementById("die_requisition_id_display");
    const customerRequisitionNo = document.getElementById("customer_requisition_no");
    const sectionNo = document.getElementById("section_no");
    const sectionName = document.getElementById("section_name");
    const wtRange = document.getElementById("wt_range");
    const dieNo = document.getElementById("die_no");
    const dieName = document.getElementById("die_name");
    const presentWt = document.getElementById("present_wt");
    const noOfCavity = document.getElementById("no_of_cavity");

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

    // ---------------- Fetch Next Die Requisition ID ----------------
    async function fetchNextDieRequisitionId() {
        if (window.editMode) return; // Don't fetch in edit mode
        
        try {
            const response = await fetch('/planning/api/die-requisitions/?action=get_next_id');
            const data = await response.json();
            
            if (data.success && data.next_die_requisition_id) {
                if (dieRequisitionIdDisplay) {
                    dieRequisitionIdDisplay.value = data.next_die_requisition_id;
                }
            }
        } catch (error) {
            console.error('Error fetching next Die Requisition ID:', error);
        }
    }

    // ---------------- Auto-populate Section fields ----------------
    if (customerRequisitionNo) {
        customerRequisitionNo.addEventListener("change", async function() {
            const requisitionId = this.value;
            
            // Clear section dropdown
            sectionNo.innerHTML = '<option value="">Select Section</option>';
            sectionName.value = '';
            wtRange.value = '';
            
            if (!requisitionId) {
                sectionNo.disabled = true;
                return;
            }

            try {
                const response = await fetch(`/planning/api/die-requisitions/?action=get_requisition_orders&requisition_id=${requisitionId}`);
                const data = await response.json();
                
                if (data.success && data.orders && data.orders.length > 0) {
                    sectionNo.disabled = false;
                    
                    data.orders.forEach(order => {
                        const option = document.createElement('option');
                        option.value = order.section_no_id;
                        option.textContent = order.section_no;
                        option.dataset.sectionName = order.section_name;
                        option.dataset.wtRange = order.wt_range;
                        sectionNo.appendChild(option);
                    });
                } else {
                    showMessage("error", "No sections found for this requisition");
                    sectionNo.disabled = true;
                }
            } catch (error) {
                console.error('Error fetching requisition orders:', error);
                showMessage("error", "Error loading sections");
                sectionNo.disabled = true;
            }
        });
    }

    // ---------------- Auto-populate Section Name and WT Range ----------------
    if (sectionNo) {
        sectionNo.addEventListener("change", function() {
            const selectedOption = this.options[this.selectedIndex];
            
            if (selectedOption.value) {
                sectionName.value = selectedOption.dataset.sectionName || '';
                wtRange.value = selectedOption.dataset.wtRange || '';
            } else {
                sectionName.value = '';
                wtRange.value = '';
            }
        });
    }

    // ---------------- Auto-populate Die fields ----------------
    if (dieNo) {
        dieNo.addEventListener("change", async function() {
            const dieId = this.value;
            
            // Clear die fields
            dieName.value = '';
            presentWt.value = '';
            noOfCavity.value = '';
            
            if (!dieId) return;

            try {
                const response = await fetch(`/planning/api/die-requisitions/?action=get_die_details&die_id=${dieId}`);
                const data = await response.json();
                
                if (data.success && data.die) {
                    dieName.value = data.die.die_name || '';
                    presentWt.value = data.die.req_weight || '';
                    noOfCavity.value = data.die.no_of_cavity || '';
                } else {
                    showMessage("error", "Error loading die details");
                }
            } catch (error) {
                console.error('Error fetching die details:', error);
                showMessage("error", "Error loading die details");
            }
        });
    }

    // ---------------- Validate Form ----------------
    function validateForm() {
        const date = document.getElementById("date").value;
        const press = document.getElementById("press").value;
        const shift = document.getElementById("shift").value;
        const staffName = document.getElementById("staff_name").value;
        const custReqNo = document.getElementById("customer_requisition_no").value;
        const section = document.getElementById("section_no").value;
        const die = document.getElementById("die_no").value;
        const cutLength = document.getElementById("cut_length").value;

        if (!date) {
            showMessage("error", "Date is required");
            return false;
        }

        if (!press) {
            showMessage("error", "Press is required");
            return false;
        }

        if (!shift) {
            showMessage("error", "Shift is required");
            return false;
        }

        if (!staffName) {
            showMessage("error", "Staff Name is required");
            return false;
        }

        if (!custReqNo) {
            showMessage("error", "Customer Requisition No is required");
            return false;
        }

        if (!section) {
            showMessage("error", "Section No is required");
            return false;
        }

        if (!die) {
            showMessage("error", "Die No is required");
            return false;
        }

        if (!cutLength || parseFloat(cutLength) <= 0) {
            showMessage("error", "Valid Cut Length is required (must be greater than 0)");
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
                shift: formData.get("shift"),
                staff_name: formData.get("staff_name"),
                customer_requisition_no: formData.get("customer_requisition_no"),
                section_no: formData.get("section_no"),
                section_name: formData.get("section_name") || "",
                wt_range: formData.get("wt_range") || "",
                die_no: formData.get("die_no"),
                die_name: formData.get("die_name") || "",
                present_wt: formData.get("present_wt") || "0",
                no_of_cavity: formData.get("no_of_cavity") || "",
                cut_length: formData.get("cut_length") || "",
                remark: formData.get("remark") || ""
            };

            // Debug: Log payload
            console.log("Payload being sent:", payload);

            try {
                let url, method;
                if (window.editMode) {
                    url = `/planning/api/die-requisitions/${window.requisitionId}/`;
                    method = "POST";
                } else {
                    url = "/planning/api/die-requisitions/";
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
                        showMessage("success", "Die Requisition updated successfully!");
                        // Redirect to list page after 1 second
                        setTimeout(() => window.location.href = '/planning/die-requisitions/', 1000);
                    } else if (result.created) {
                        showMessage("success", `Die Requisition created successfully! ID: ${result.requisition.die_requisition_id}`);
                        // Redirect to list page after 1 second
                        setTimeout(() => window.location.href = '/planning/die-requisitions/', 1000);
                    } else {
                        showMessage("success", "Die Requisition saved successfully!");
                        // Redirect to list page after 1 second
                        setTimeout(() => window.location.href = '/planning/die-requisitions/', 1000);
                    }
                } else {
                    showMessage("error", result.message || "Failed to save die requisition");
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

    // Initial load: Fetch next Die Requisition ID if in create mode
    if (!window.editMode) {
        fetchNextDieRequisitionId();
    } else {
        // In edit mode, trigger change events to populate dependent fields
        if (customerRequisitionNo && customerRequisitionNo.value) {
            customerRequisitionNo.dispatchEvent(new Event('change'));
        }
        if (dieNo && dieNo.value) {
            dieNo.dispatchEvent(new Event('change'));
        }
    }
});