document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("dailyProductionReportForm");
    const reportIdDisplay = document.getElementById("report_id_display");
    const onlineProductionReport = document.getElementById("online_production_report");
    
    // Form fields
    const dieNo = document.getElementById("die_no");
    const sectionNo = document.getElementById("section_no");
    const sectionName = document.getElementById("section_name");
    const cavity = document.getElementById("cavity");
    const startTime = document.getElementById("start_time");
    const endTime = document.getElementById("end_time");
    const billetSize = document.getElementById("billet_size");
    const noOfBillet = document.getElementById("no_of_billet");
    const inputQty = document.getElementById("input_qty");
    const cutLength = document.getElementById("cut_length");
    const wtPerPiece = document.getElementById("wt_per_piece");
    const noOfOkPcs = document.getElementById("no_of_ok_pcs");
    const output = document.getElementById("output");
    const recovery = document.getElementById("recovery");
    const nopBp = document.getElementById("nop_bp");
    const nopBa = document.getElementById("nop_ba");
    const nrt = document.getElementById("nrt");

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

    // ---------------- Fetch Next Report ID ----------------
    async function fetchNextReportId() {
        if (window.editMode) return;

        try {
            const response = await fetch('/production/api/daily-production-reports/?action=get_next_id');
            const data = await response.json();

            if (data.success && data.next_report_id) {
                if (reportIdDisplay) {
                    reportIdDisplay.value = data.next_report_id;
                }
            }
        } catch (error) {
            console.error('Error fetching next Report ID:', error);
        }
    }

    // ---------------- Calculate Recovery ----------------
    function calculateRecovery() {
        const inputValue = parseFloat(inputQty.value);
        const outputValue = parseFloat(output.value);

        if (!inputValue || !outputValue || inputValue <= 0) {
            recovery.value = '';
            return;
        }

        // Formula: (output / input) * 100
        const recoveryValue = (outputValue / inputValue) * 100;
        recovery.value = recoveryValue.toFixed(2);
    }

    // ---------------- Calculate NRT (Net Run Time) ----------------
    function calculateNRT() {
        const startTimeValue = startTime.value;
        const endTimeValue = endTime.value;

        if (!startTimeValue || !endTimeValue) {
            nrt.value = '';
            return;
        }

        // Parse time values
        const [startHours, startMinutes] = startTimeValue.split(':').map(Number);
        const [endHours, endMinutes] = endTimeValue.split(':').map(Number);

        // Convert to minutes
        let startTotalMinutes = startHours * 60 + startMinutes;
        let endTotalMinutes = endHours * 60 + endMinutes;

        // Handle case where end time is on next day
        if (endTotalMinutes < startTotalMinutes) {
            endTotalMinutes += 24 * 60; // Add 24 hours
        }

        // Calculate difference in minutes
        const diffMinutes = endTotalMinutes - startTotalMinutes;

        // Convert to hours
        const hours = (diffMinutes / 60).toFixed(2);
        nrt.value = hours;
    }

    // Add event listeners for auto-calculations
    if (inputQty) {
        inputQty.addEventListener('input', calculateRecovery);
    }

    if (output) {
        output.addEventListener('input', calculateRecovery);
    }

    if (startTime) {
        startTime.addEventListener('change', calculateNRT);
    }

    if (endTime) {
        endTime.addEventListener('change', calculateNRT);
    }

    // Calculate on page load if editing
    if (window.editMode) {
        calculateRecovery();
        calculateNRT();
    }

    // ---------------- Auto-populate fields from Online Production Report ----------------
    if (onlineProductionReport) {
        onlineProductionReport.addEventListener("change", async function () {
            const reportId = this.value;

            // Clear all fields
            clearDependentFields();

            if (!reportId) return;

            try {
                const response = await fetch(`/production/api/daily-production-reports/?action=get_online_report_details&online_report_id=${reportId}`);
                const data = await response.json();

                if (data.success && data.details) {
                    const details = data.details;

                    dieNo.value = details.die_no || '';
                    sectionNo.value = details.section_no || '';
                    sectionName.value = details.section_name || '';
                    cavity.value = details.cavity || '';
                    startTime.value = details.start_time || '';
                    endTime.value = details.end_time || '';
                    billetSize.value = details.billet_size || '';
                    noOfBillet.value = details.no_of_billet || '';
                    inputQty.value = details.input_qty || '';
                    cutLength.value = details.cut_length || '';
                    wtPerPiece.value = details.wt_per_piece || '';
                    noOfOkPcs.value = details.no_of_ok_pcs || '';
                    output.value = details.output || '';
                    nopBp.value = details.nop_bp || '';
                    nopBa.value = details.nop_ba || '';

                    // Trigger calculations
                    calculateRecovery();
                    calculateNRT();
                } else {
                    showMessage("error", data.message || "Error loading online production report details");
                }
            } catch (error) {
                console.error('Error fetching online production report details:', error);
                showMessage("error", "Error loading online production report details");
            }
        });
    }

    function clearDependentFields() {
        dieNo.value = '';
        sectionNo.value = '';
        sectionName.value = '';
        cavity.value = '';
        startTime.value = '';
        endTime.value = '';
        billetSize.value = '';
        noOfBillet.value = '';
        inputQty.value = '';
        cutLength.value = '';
        wtPerPiece.value = '';
        noOfOkPcs.value = '';
        output.value = '';
        recovery.value = '';
        nopBp.value = '';
        nopBa.value = '';
        nrt.value = '';
    }

    // ---------------- Validate Form ----------------
    function validateForm() {
        const dateValue = document.getElementById("date").value;
        const onlineReportValue = document.getElementById("online_production_report").value;

        if (!dateValue) {
            showMessage("error", "Date is required");
            return false;
        }

        if (!onlineReportValue) {
            showMessage("error", "Die No (Online Production Report) is required");
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
                date: formData.get("date") || null,
                online_production_report: formData.get("online_production_report") || null,
                die_no: formData.get("die_no") || "",
                section_no: formData.get("section_no") || "",
                section_name: formData.get("section_name") || "",
                cavity: formData.get("cavity") || "",
                start_time: formData.get("start_time") || null,
                end_time: formData.get("end_time") || null,
                billet_size: formData.get("billet_size") || "",
                no_of_billet: formData.get("no_of_billet") ? parseInt(formData.get("no_of_billet")) : null,
                input_qty: formData.get("input_qty") ? parseFloat(formData.get("input_qty")) : null,
                cut_length: formData.get("cut_length") || "",
                wt_per_piece: formData.get("wt_per_piece") ? parseFloat(formData.get("wt_per_piece")) : null,
                no_of_ok_pcs: formData.get("no_of_ok_pcs") ? parseInt(formData.get("no_of_ok_pcs")) : null,
                output: formData.get("output") ? parseFloat(formData.get("output")) : null,
                nop_bp: formData.get("nop_bp") ? parseInt(formData.get("nop_bp")) : null,
                nop_ba: formData.get("nop_ba") ? parseInt(formData.get("nop_ba")) : null
            };

            console.log("Payload being sent:", payload);

            try {
                let url, method;
                if (window.editMode) {
                    url = `/production/api/daily-production-reports/${window.reportId}/`;
                    method = "POST";
                } else {
                    url = "/production/api/daily-production-reports/";
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
                        showMessage("success", "Daily Production Report updated successfully!");
                        setTimeout(() => window.location.href = '/production/daily-production-reports/', 1000);
                    } else if (result.created) {
                        showMessage("success", `Daily Production Report created successfully! ID: ${result.report.report_id}`);
                        setTimeout(() => window.location.href = '/production/daily-production-reports/', 1000);
                    } else {
                        showMessage("success", "Daily Production Report saved successfully!");
                        setTimeout(() => window.location.href = '/production/daily-production-reports/', 1000);
                    }
                } else {
                    showMessage("error", result.message || "Failed to save daily production report");
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
        fetchNextReportId();
    }

});