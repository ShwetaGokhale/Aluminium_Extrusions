document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("productionReportForm");
    const productionIdDisplay = document.getElementById("production_id_display");
    const productionPlanId = document.getElementById("production_plan_id");
    const customerName = document.getElementById("customer_name");
    const dieRequisitionId = document.getElementById("die_requisition_id");
    const dieNo = document.getElementById("die_no");
    const sectionNo = document.getElementById("section_no");
    const sectionName = document.getElementById("section_name");
    const wtPerPiece = document.getElementById("wt_per_piece");
    const pressNo = document.getElementById("press_no");
    const dateOfProduction = document.getElementById("date_of_production");
    const shift = document.getElementById("shift");
    const operator = document.getElementById("operator");
    const plannedQty = document.getElementById("planned_qty");
    const dateField = document.getElementById("date");

    // ---------------- Set today's date as default (for create mode) ----------------
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

    // ---------------- Auto-populate Production Plan fields ----------------
    if (productionPlanId) {
        productionPlanId.addEventListener("change", async function () {
            const planId = this.value;

            // Clear all auto-populated fields
            customerName.value = '';
            dieRequisitionId.value = '';
            dieNo.value = '';
            sectionNo.value = '';
            sectionName.value = '';
            wtPerPiece.value = '';
            pressNo.value = '';
            dateOfProduction.value = '';
            shift.value = '';
            operator.value = '';
            plannedQty.value = '';

            if (!planId) return;

            try {
                const response = await fetch(`/production/api/online-production-reports/?action=get_production_plan_details&production_plan_id=${planId}`);
                const data = await response.json();

                if (data.success && data.production_plan) {
                    customerName.value = data.production_plan.customer_name || '';
                    dieRequisitionId.value = data.production_plan.die_requisition_id || '';
                    dieNo.value = data.production_plan.die_no || '';
                    sectionNo.value = data.production_plan.section_no || '';
                    sectionName.value = data.production_plan.section_name || '';
                    wtPerPiece.value = data.production_plan.wt_per_piece || '';
                    pressNo.value = data.production_plan.press || '';
                    dateOfProduction.value = data.production_plan.date_of_production || '';
                    shift.value = data.production_plan.shift || '';
                    operator.value = data.production_plan.operator || '';
                    plannedQty.value = data.production_plan.planned_qty || '';
                } else {
                    showMessage("error", "Error loading production plan details");
                }
            } catch (error) {
                console.error('Error fetching production plan details:', error);
                showMessage("error", "Error loading production plan details");
            }
        });
    }

    // ---------------- Custom Clock Picker Implementation ----------------
    let currentTimePicker = null;
    let selectedHour = 12;
    let selectedMinute = 0;
    let selectedPeriod = 'AM';

    function convertTo12Hour(time24) {
        if (!time24) return { hour: 12, minute: 0, period: 'AM' };
        
        const [hours, minutes] = time24.split(':').map(Number);
        
        // Just use the hour as stored, no conversion
        let hour = hours;
        let period = 'AM'; // Default period
        
        return { hour, minute: minutes, period };
    }

    function convertTo24Hour(hour, minute, period) {
        // Just store the hour as selected, no conversion
        let hour24 = parseInt(hour);
        return `${String(hour24).padStart(2, '0')}:${String(minute).padStart(2, '0')}`;
    }

    function format12Hour(hour, minute, period) {
        return `${String(hour).padStart(2, '0')}:${String(minute).padStart(2, '0')} ${period}`;
    }

    function createClockPicker(inputElement, hiddenInput) {
        // Get existing time if any
        if (hiddenInput.value) {
            const time12 = convertTo12Hour(hiddenInput.value);
            selectedHour = time12.hour;
            selectedMinute = time12.minute;
            selectedPeriod = time12.period;
        }

        // Remove any existing picker
        const existingPicker = document.querySelector('.clock-picker-modal');
        if (existingPicker) {
            existingPicker.remove();
        }

        const modal = document.createElement('div');
        modal.className = 'clock-picker-modal active';
        
        // Position the modal near the input field
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

        // Create hour numbers
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

            number.addEventListener('click', function() {
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

        // Period selector
        modal.querySelectorAll('.period-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                selectedPeriod = this.dataset.period;
                modal.querySelectorAll('.period-btn').forEach(b => b.classList.remove('active'));
                this.classList.add('active');
                updateDisplay();
            });
        });

        // Minute input
        minuteInput.addEventListener('input', function() {
            let value = parseInt(this.value) || 0;
            if (value > 59) value = 59;
            if (value < 0) value = 0;
            this.value = value;
            selectedMinute = value;
            updateDisplay();
        });

        // Cancel button
        modal.querySelector('.clock-cancel-btn').addEventListener('click', () => {
            modal.remove();
        });

        // OK button
        modal.querySelector('.clock-ok-btn').addEventListener('click', () => {
            const time24 = convertTo24Hour(selectedHour, selectedMinute, selectedPeriod);
            const time12 = format12Hour(selectedHour, selectedMinute, selectedPeriod);
            
            hiddenInput.value = time24;
            inputElement.value = time12;
            
            modal.remove();
        });

        // Close on click outside
        setTimeout(() => {
            document.addEventListener('click', function closeOnClickOutside(e) {
                if (!modal.contains(e.target) && !inputElement.contains(e.target)) {
                    modal.remove();
                    document.removeEventListener('click', closeOnClickOutside);
                }
            });
        }, 100);
    }

    // Replace time inputs with custom picker
    function setupTimeInput(timeInputId) {
        const originalInput = document.getElementById(timeInputId);
        if (!originalInput) return;

        const wrapper = document.createElement('div');
        wrapper.className = 'time-input-wrapper';

        const displayInput = document.createElement('input');
        displayInput.type = 'text';
        displayInput.placeholder = 'Select time';
        displayInput.readOnly = true;
        
        // Set initial value if exists
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

    // Setup custom time pickers
    setupTimeInput('start_time');
    setupTimeInput('end_time');

    // ---------------- Validate Form ----------------
    function validateForm() {
        const pressNoValue = document.getElementById("press_no").value;
        const status = document.getElementById("status").value;

        if (!pressNoValue) {
            showMessage("error", "Press No is required");
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
                production_plan_id: formData.get("production_plan_id") || null,
                customer_name: formData.get("customer_name") || "",
                die_requisition_id: formData.get("die_requisition_id") || "",
                die_no: formData.get("die_no") || "",
                section_no: formData.get("section_no") || "",
                section_name: formData.get("section_name") || "",
                wt_per_piece: formData.get("wt_per_piece") || null,
                press_no: formData.get("press_no"),
                date_of_production: formData.get("date_of_production") || null,
                shift: formData.get("shift") || null,
                operator: formData.get("operator") || null,
                planned_qty: formData.get("planned_qty") || null,
                start_time: formData.get("start_time") || null,
                end_time: formData.get("end_time") || null,
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

    // ---------------- Initial Load ----------------
    if (!window.editMode) {
        fetchNextProductionId();
    } else {
        if (productionPlanId && productionPlanId.value) {
            productionPlanId.dispatchEvent(new Event('change'));
        }
    }
});