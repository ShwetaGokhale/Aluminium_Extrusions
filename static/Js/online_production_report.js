document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("productionReportForm");
    const productionIdDisplay = document.getElementById("production_id_display");
    const dateOfProduction = document.getElementById("date_of_production");
    const dieRequisition = document.getElementById("die_requisition");
    const dieNo = document.getElementById("die_no");
    const sectionNo = document.getElementById("section_no");
    const sectionName = document.getElementById("section_name");
    const wtPerPieceGeneral = document.getElementById("wt_per_piece_general");
    const noOfCavity = document.getElementById("no_of_cavity");
    const cutLength = document.getElementById("cut_length");
    const press = document.getElementById("press");
    const shift = document.getElementById("shift");
    const operator = document.getElementById("operator");
    const plannedQty = document.getElementById("planned_qty");
    const billetSize = document.getElementById("billet_size");
    const noOfBillet = document.getElementById("no_of_billet");
    const weight = document.getElementById("weight");
    const wtPerPieceOutput = document.getElementById("wt_per_piece_output");
    const noOfPieces = document.getElementById("no_of_pieces");
    const totalOutput = document.getElementById("total_output");

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

    // ---------------- Fetch Next Production ID ----------------
    async function fetchNextProductionId() {
        if (window.editMode) return;

        try {
            const response = await fetch('/production/api/online-production-reports/?action=get_next_id');
            const data = await response.json();

            if (data.success && data.next_production_id) {
                if (productionIdDisplay) {
                    productionIdDisplay.value = data.next_production_id;
                }
            }
        } catch (error) {
            console.error('Error fetching next Production ID:', error);
        }
    }

    // ---------------- Calculate Total Output ----------------
    function calculateTotalOutput() {
        const wtOutput = parseFloat(wtPerPieceOutput.value) || 0;
        const pieces = parseInt(noOfPieces.value) || 0;

        if (wtOutput > 0 && pieces > 0) {
            const total = (wtOutput * pieces).toFixed(2);
            totalOutput.value = total;
        } else {
            totalOutput.value = '';
        }
    }

    // Add event listeners for auto-calculation
    if (wtPerPieceOutput) {
        wtPerPieceOutput.addEventListener('input', calculateTotalOutput);
    }
    if (noOfPieces) {
        noOfPieces.addEventListener('input', calculateTotalOutput);
    }

    // ---------------- Load Die Requisitions by Date of Production ----------------
    if (dateOfProduction) {
        dateOfProduction.addEventListener("change", async function () {
            const date = this.value;

            // Clear die requisition dropdown
            dieRequisition.innerHTML = '<option value="">Select Die Requisition ID</option>';

            // Clear all dependent fields
            clearDependentFields();

            if (!date) return;

            try {
                const response = await fetch(`/production/api/online-production-reports/?action=get_die_requisitions_by_date&date_of_production=${date}`);
                const data = await response.json();

                if (data.success && data.die_requisitions.length > 0) {
                    data.die_requisitions.forEach(req => {
                        const option = document.createElement('option');
                        option.value = req.id;
                        option.textContent = req.die_requisition_id;
                        dieRequisition.appendChild(option);
                    });
                } else {
                    showMessage("error", "No die requisitions found for this date");
                }
            } catch (error) {
                console.error('Error fetching die requisitions:', error);
                showMessage("error", "Error loading die requisitions");
            }
        });
    }

    // ---------------- Auto-populate Die Requisition fields ----------------
    if (dieRequisition) {
        dieRequisition.addEventListener("change", async function () {
            const reqId = this.value;
            const dateProd = dateOfProduction.value;

            // Clear all fields
            clearDependentFields();

            if (!reqId || !dateProd) return;

            try {
                const response = await fetch(`/production/api/online-production-reports/?action=get_die_requisition_details&die_requisition_id=${reqId}&date_of_production=${dateProd}`);
                const data = await response.json();

                if (data.success && data.details) {
                    const details = data.details;

                    dieNo.value = details.die_no || '';
                    sectionNo.value = details.section_no || '';
                    sectionName.value = details.section_name || '';
                    wtPerPieceGeneral.value = details.wt_per_piece || '';
                    noOfCavity.value = details.no_of_cavity || '';
                    cutLength.value = details.cut_length || '';
                    press.value = details.press || '';
                    shift.value = details.shift || '';
                    operator.value = details.operator || '';
                    plannedQty.value = details.planned_qty || '';
                    billetSize.value = details.billet_size || '';
                    noOfBillet.value = details.no_of_billet || '';
                } else {
                    showMessage("error", "Error loading die requisition details");
                }
            } catch (error) {
                console.error('Error fetching die requisition details:', error);
                showMessage("error", "Error loading die requisition details");
            }
        });
    }

    function clearDependentFields() {
        dieNo.value = '';
        sectionNo.value = '';
        sectionName.value = '';
        wtPerPieceGeneral.value = '';
        noOfCavity.value = '';
        cutLength.value = '';
        press.value = '';
        shift.value = '';
        operator.value = '';
        plannedQty.value = '';
        billetSize.value = '';
        noOfBillet.value = '';
    }

    // ---------------- Custom Clock Picker Implementation ----------------
    let selectedHour = 12;
    let selectedMinute = 0;
    let selectedPeriod = 'AM';

    function convertTo12Hour(time24) {
        if (!time24) return { hour: 12, minute: 0, period: 'AM' };
        const [hours, minutes] = time24.split(':').map(Number);
        let hour = hours;
        let period = 'AM';
        return { hour, minute: minutes, period };
    }

    function convertTo24Hour(hour, minute, period) {
        let hour24 = parseInt(hour);
        return `${String(hour24).padStart(2, '0')}:${String(minute).padStart(2, '0')}`;
    }

    function format12Hour(hour, minute, period) {
        return `${String(hour).padStart(2, '0')}:${String(minute).padStart(2, '0')} ${period}`;
    }

    function createClockPicker(inputElement, hiddenInput) {
        if (hiddenInput.value) {
            const time12 = convertTo12Hour(hiddenInput.value);
            selectedHour = time12.hour;
            selectedMinute = time12.minute;
            selectedPeriod = time12.period;
        }

        const existingPicker = document.querySelector('.clock-picker-modal');
        if (existingPicker) existingPicker.remove();

        const modal = document.createElement('div');
        modal.className = 'clock-picker-modal active';

        const rect = inputElement.getBoundingClientRect();
        modal.style.position = 'absolute';
        modal.style.left = rect.left + 'px';
        modal.style.top = (rect.bottom + 5) + 'px';

        modal.innerHTML = `
            <div class="clock-picker-container">
                <div class="clock-picker-header">
                    <h4>Select Time</h4>
                    <div class="clock-display">${format12Hour(selectedHour, selectedMinute, selectedPeriod)}</div>
                    <div class="period-selector">
                        <button class="period-btn ${selectedPeriod === 'AM' ? 'active' : ''}" data-period="AM">AM</button>
                        <button class="period-btn ${selectedPeriod === 'PM' ? 'active' : ''}" data-period="PM">PM</button>
                    </div>
                </div>
                <div class="clock-face" id="clockFace">
                    <div class="clock-center"></div>
                </div>
                <div class="minute-input-container">
                    <label>Minutes:</label>
                    <input type="number" id="minuteInput" min="0" max="59" value="${selectedMinute}" />
                </div>
                <div class="clock-picker-actions">
                    <button class="clock-cancel-btn">Cancel</button>
                    <button class="clock-ok-btn">OK</button>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        const clockFace = modal.querySelector('#clockFace');
        const clockDisplay = modal.querySelector('.clock-display');
        const minuteInput = modal.querySelector('#minuteInput');

        for (let i = 1; i <= 12; i++) {
            const angle = (i * 30 - 90) * (Math.PI / 180);
            const x = 85 + 70 * Math.cos(angle);
            const y = 85 + 70 * Math.sin(angle);

            const number = document.createElement('div');
            number.className = 'clock-number';
            if (i === selectedHour) number.classList.add('selected');
            number.textContent = i;
            number.style.left = `${x - 15}px`;
            number.style.top = `${y - 15}px`;
            number.dataset.hour = i;

            number.addEventListener('click', function () {
                selectedHour = parseInt(this.dataset.hour);
                modal.querySelectorAll('.clock-number').forEach(n => n.classList.remove('selected'));
                this.classList.add('selected');
                updateDisplay();
            });

            clockFace.appendChild(number);
        }

        function updateDisplay() {
            clockDisplay.textContent = format12Hour(selectedHour, selectedMinute, selectedPeriod);
        }

        modal.querySelectorAll('.period-btn').forEach(btn => {
            btn.addEventListener('click', function () {
                selectedPeriod = this.dataset.period;
                modal.querySelectorAll('.period-btn').forEach(b => b.classList.remove('active'));
                this.classList.add('active');
                updateDisplay();
            });
        });

        minuteInput.addEventListener('input', function () {
            let value = parseInt(this.value) || 0;
            if (value > 59) value = 59;
            if (value < 0) value = 0;
            this.value = value;
            selectedMinute = value;
            updateDisplay();
        });

        modal.querySelector('.clock-cancel-btn').addEventListener('click', () => modal.remove());

        modal.querySelector('.clock-ok-btn').addEventListener('click', () => {
            const time24 = convertTo24Hour(selectedHour, selectedMinute, selectedPeriod);
            const time12 = format12Hour(selectedHour, selectedMinute, selectedPeriod);

            hiddenInput.value = time24;
            inputElement.value = time12;

            modal.remove();
        });

        setTimeout(() => {
            document.addEventListener('click', function closeOnClickOutside(e) {
                if (!modal.contains(e.target) && !inputElement.contains(e.target)) {
                    modal.remove();
                    document.removeEventListener('click', closeOnClickOutside);
                }
            });
        }, 100);
    }

    function setupTimeInput(timeInputId) {
        const originalInput = document.getElementById(timeInputId);
        if (!originalInput) return;

        const wrapper = document.createElement('div');
        wrapper.className = 'time-input-wrapper';

        const displayInput = document.createElement('input');
        displayInput.type = 'text';
        displayInput.placeholder = 'Select time';
        displayInput.readOnly = true;

        if (originalInput.value) {
            const time12 = convertTo12Hour(originalInput.value);
            displayInput.value = format12Hour(time12.hour, time12.minute, time12.period);
        }

        const clockIcon = document.createElement('span');
        clockIcon.className = 'clock-icon';
        clockIcon.innerHTML = '🕐';

        wrapper.appendChild(displayInput);
        wrapper.appendChild(clockIcon);

        originalInput.parentNode.insertBefore(wrapper, originalInput);
        originalInput.type = 'hidden';

        displayInput.addEventListener('click', () => {
            createClockPicker(displayInput, originalInput);
        });
    }

    setupTimeInput('start_time');
    setupTimeInput('end_time');

    // ---------------- Validate Form ----------------
    function validateForm() {
        const pressValue = document.getElementById("press").value;
        const status = document.getElementById("status").value;
        const dateProdValue = document.getElementById("date_of_production").value;
        const dieReqValue = document.getElementById("die_requisition").value;

        if (!dateProdValue) {
            showMessage("error", "Date of Production is required");
            return false;
        }

        if (!dieReqValue) {
            showMessage("error", "Die Requisition ID is required");
            return false;
        }

        if (!pressValue) {
            showMessage("error", "Press is required");
            return false;
        }

        if (!status) {
            showMessage("error", "Status is required");
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
                date_of_production: formData.get("date_of_production") || null,
                die_requisition: formData.get("die_requisition") || null,
                die_no: formData.get("die_no") || "",
                section_no: formData.get("section_no") || "",
                section_name: formData.get("section_name") || "",
                wt_per_piece_general: formData.get("wt_per_piece_general") ? parseFloat(formData.get("wt_per_piece_general")) : null,
                no_of_cavity: formData.get("no_of_cavity") || "",
                cut_length: formData.get("cut_length") || "",
                press: formData.get("press"),
                shift: formData.get("shift") || null,
                operator: formData.get("operator") || null,
                planned_qty: formData.get("planned_qty") ? parseInt(formData.get("planned_qty")) : null,
                start_time: formData.get("start_time") || null,
                end_time: formData.get("end_time") || null,
                billet_size: formData.get("billet_size") || "",
                no_of_billet: formData.get("no_of_billet") ? parseInt(formData.get("no_of_billet")) : null,
                weight: formData.get("weight") ? parseFloat(formData.get("weight")) : null,
                input_qty: formData.get("input_qty") ? parseFloat(formData.get("input_qty")) : null,
                wt_per_piece_output: formData.get("wt_per_piece_output") ? parseFloat(formData.get("wt_per_piece_output")) : null,
                no_of_pieces: formData.get("no_of_pieces") ? parseInt(formData.get("no_of_pieces")) : null,
                status: formData.get("status")
            };


            console.log("Payload being sent:", payload);

            try {
                let url, method;
                if (window.editMode) {
                    url = `/production/api/online-production-reports/${window.reportId}/`;
                    method = "POST";
                } else {
                    url = "/production/api/online-production-reports/";
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
                        showMessage("success", "Online Production Report updated successfully!");
                        setTimeout(() => window.location.href = '/production/online-production-reports/', 1000);
                    } else if (result.created) {
                        showMessage("success", `Online Production Report created successfully! ID: ${result.report.production_id}`);
                        setTimeout(() => window.location.href = '/production/online-production-reports/', 1000);
                    } else {
                        showMessage("success", "Online Production Report saved successfully!");
                        setTimeout(() => window.location.href = '/production/online-production-reports/', 1000);
                    }
                } else {
                    showMessage("error", result.message || "Failed to save production report");
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

    // ---------------- Initial Load -----------------
    if (!window.editMode) {
        fetchNextProductionId();
    }

});