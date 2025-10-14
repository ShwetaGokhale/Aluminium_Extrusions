document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("requisitionForm");
    const ordersBody = document.getElementById("ordersTableBody");
    const requisitionIdDisplay = document.getElementById("requisition_id_display");

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
            if (ordersBody) {
                ordersBody.innerHTML = `
                    <tr class="example-row" style="background:#f9f9f9; color:#888;">
                        <td><input type="text" placeholder="A101" disabled></td>
                        <td><input type="text" placeholder="Section Name" disabled></td>
                        <td><input type="text" placeholder="10-20" disabled></td>
                        <td>
                            <select disabled>
                                <option>12ft</option>
                            </select>
                        </td>
                        <td><input type="number" placeholder="100" disabled></td>
                        <td></td>
                    </tr>
                `;
            }
        }
    }

    // ---------------- Load Edit Data ----------------
    function loadEditData() {
        if (window.editMode && window.ordersData) {
            ordersBody.innerHTML = "";  // Clear any existing rows
            window.ordersData.forEach(order => {
                // Convert order data to match addOrderRow format
                const orderData = {
                    id: order.id,
                    section_no__id: order.section_no || order.section_no__id,
                    section_no__section_no: order.section_no_name || order.section_no__section_no,
                    section_no__section_name: order.section_name || order.section_no__section_name,
                    wt_range: order.wt_range,
                    cut_length: order.cut_length,
                    qty_in_no: order.qty_in_no
                };
                addOrderRow(orderData);
            });
        }
    }

    // ---------------- Fetch Next Requisition ID ----------------
    async function fetchNextRequisitionId() {
        if (window.editMode) return;

        try {
            const response = await fetch('/order/api/requisitions/?action=get_next_id');
            const data = await response.json();

            if (data.success && data.next_requisition_id) {
                if (requisitionIdDisplay) {
                    requisitionIdDisplay.value = data.next_requisition_id;
                }
            }
        } catch (error) {
            console.error('Error fetching next Requisition ID:', error);
        }
    }

    // ---------------- Dropdown Utility ----------------
    function attachDropdown(input, dropdown, hiddenInput, callback) {
        if (!input || !dropdown) return;
        const wrapper = input.parentElement;
        const icon = wrapper.querySelector(".dropdown-icon");
        let focus = -1;

        function openDropdown() {
            dropdown.classList.add("open");
            dropdown.style.display = "block";
            if (icon) icon.classList.add("open");
            input.focus();
        }

        function closeDropdown() {
            dropdown.classList.remove("open");
            if (icon) icon.classList.remove("open");
            setTimeout(() => dropdown.style.display = "none", 250);
        }

        input.addEventListener("click", openDropdown);
        if (icon) icon.addEventListener("click", (e) => {
            e.stopPropagation();
            dropdown.classList.contains("open") ? closeDropdown() : openDropdown();
        });

        input.addEventListener("input", () => {
            let filter = input.value.toLowerCase();
            let items = dropdown.querySelectorAll(".dropdown-item");
            focus = -1;
            items.forEach(item => item.style.display = item.textContent.toLowerCase().includes(filter) ? "block" : "none");
            openDropdown();
        });

        input.addEventListener("keydown", (e) => {
            let items = dropdown.querySelectorAll(".dropdown-item:not([style*='display: none'])");
            if (!items.length) return;

            if (e.key === "ArrowDown") { focus = (focus + 1) % items.length; setActive(items); e.preventDefault(); }
            else if (e.key === "ArrowUp") { focus = (focus - 1 + items.length) % items.length; setActive(items); e.preventDefault(); }
            else if (e.key === "Enter") { e.preventDefault(); if (focus > -1) items[focus].click(); }
        });

        function setActive(items) {
            items.forEach(item => item.classList.remove("active"));
            if (focus >= 0) { items[focus].classList.add("active"); items[focus].scrollIntoView({ block: "nearest" }); }
        }

        dropdown.querySelectorAll(".dropdown-item").forEach(item => {
            item.addEventListener("click", () => {
                input.value = item.textContent.trim();
                if (hiddenInput) hiddenInput.value = item.dataset.id || item.dataset.value;
                if (callback) callback(item);
                closeDropdown();
            });
        });

        document.addEventListener("click", (e) => {
            if (!e.target.closest(".custom-searchable-select-wrapper")) closeDropdown();
        });
    }

    // ---------------- Customer Dropdown ----------------
    const customerInput = document.getElementById("customerSearchInput");
    const customerDropdown = document.getElementById("customerDropdownList");
    const customerHiddenId = document.getElementById("id_customer");
    const contactField = document.getElementById("customerContact");
    const addressField = document.getElementById("customerAddress");

    if (customerInput && customerDropdown && customerHiddenId) {
        attachDropdown(customerInput, customerDropdown, customerHiddenId, (item) => {
            if (contactField) contactField.value = item.dataset.contact || '';
            if (addressField) addressField.value = item.dataset.address || '';
        });
    }

    // ---------------- Sales Manager Dropdown ----------------
    const salesManagerInput = document.getElementById("salesManagerSearchInput");
    const salesManagerDropdown = document.getElementById("salesManagerDropdownList");
    const salesManagerHiddenId = document.getElementById("id_sales_manager");

    if (salesManagerInput && salesManagerDropdown && salesManagerHiddenId) {
        attachDropdown(salesManagerInput, salesManagerDropdown, salesManagerHiddenId);
    }

    // ---------------- Add Order Row ----------------
    function addOrderRow(data = {}) {
        const sectionOptions = window.sectionOptions || [];

        const row = document.createElement("tr");
        if (data.id) row.dataset.id = data.id;

        row.innerHTML = `
            <td>
              <div class="custom-searchable-select-wrapper">
                <input type="text" class="searchable-input section-input" placeholder="Search Section" 
                       value="${data.section_no__section_no || ''}">
                <i class="fa-solid fa-chevron-down dropdown-icon"></i>
                <input type="hidden" name="section_no[]" value="${data.section_no__id || ''}">
                <div class="custom-dropdown-list section-dropdown">
                  ${sectionOptions.map(opt => `<div class="dropdown-item" data-value="${opt.id}" data-name="${opt.section_name}">${opt.section_no}</div>`).join("")}
                </div>
              </div>
            </td>
            <td><input type="text" class="section-name-display" value="${data.section_no__section_name || ''}" readonly style="background-color: #f0f0f0;"></td>
            <td><input type="text" name="wt_range[]" value="${data.wt_range || ''}" placeholder="e.g., 10-20"></td>
            <td>
                <select name="cut_length[]">
                    <option value="">Select</option>
                    <option value="12ft" ${data.cut_length === '12ft' ? 'selected' : ''}>12ft</option>
                    <option value="16ft" ${data.cut_length === '16ft' ? 'selected' : ''}>16ft</option>
                    <option value="18ft" ${data.cut_length === '18ft' ? 'selected' : ''}>18ft</option>
                </select>
            </td>
            <td><input type="number" name="qty_in_no[]" value="${data.qty_in_no || ''}" min="1"></td>
            <td>
                <button type="button" class="delete-row">
                    <i class="fa-solid fa-trash"></i>
                </button>
            </td>
        `;

        const exampleRow = ordersBody.querySelector(".example-row");
        if (exampleRow) exampleRow.remove();

        ordersBody.appendChild(row);

        // Attach section dropdown with section name update
        const sectionInput = row.querySelector(".section-input");
        const sectionDropdown = row.querySelector(".section-dropdown");
        const sectionHidden = row.querySelector("input[name='section_no[]']");
        const sectionNameDisplay = row.querySelector(".section-name-display");

        attachDropdown(sectionInput, sectionDropdown, sectionHidden, (item) => {
            if (sectionNameDisplay) {
                sectionNameDisplay.value = item.dataset.name || '';
            }
        });
    }

    // ---------------- Add Order Button ----------------
    document.getElementById("addOrderBtn")?.addEventListener("click", e => { 
        e.preventDefault(); 
        addOrderRow(); 
    });

    // ---------------- Delete Row ----------------
    document.addEventListener("click", function (e) {
        const btn = e.target.closest(".delete-row");
        if (btn) {
            const row = e.target.closest("tr");
            if (row) row.remove();
            
            // Show example row if no orders left
            if (ordersBody.querySelectorAll("tr:not(.example-row)").length === 0 && !window.editMode) {
                initExampleRows();
            }
        }
    });

    // ---------------- Validate Form ----------------
    function validateForm(formData, orders) {
        const date = formData.get("date");
        const requisitionNo = formData.get("requisition_no");
        const customer = formData.get("customer");
        const salesManager = formData.get("sales_manager");

        if (!date) {
            showMessage("error", "Date is required");
            return false;
        }

        if (!requisitionNo || requisitionNo.trim() === '') {
            showMessage("error", "Customer Requisition No is required");
            return false;
        }

        if (!customer) {
            showMessage("error", "Please select a Customer");
            return false;
        }

        if (!salesManager) {
            showMessage("error", "Please select a Sales Manager");
            return false;
        }

        if (orders.length === 0) {
            showMessage("error", "Please add at least one order");
            return false;
        }

        return true;
    }

    // ---------------- Submit Form ----------------
    if (form) {
        form.addEventListener("submit", async function (e) {
            e.preventDefault();
            const formData = new FormData(form);

            let payload = {
                date: formData.get("date"),
                requisition_no: formData.get("requisition_no"),
                customer: formData.get("customer"),
                contact_no: formData.get("contact_no") || '',
                address: formData.get("address") || '',
                sales_manager: formData.get("sales_manager"),
                expiry_date: formData.get("expiry_date") || null,
                dispatch_date: formData.get("dispatch_date") || null,
                orders: []
            };

            if (ordersBody) {
                ordersBody.querySelectorAll("tr:not(.example-row)").forEach(row => {
                    const sectionInput = row.querySelector("input[name='section_no[]']");
                    const wtRange = row.querySelector("input[name='wt_range[]']");
                    const cutLength = row.querySelector("select[name='cut_length[]']");
                    const qtyInNo = row.querySelector("input[name='qty_in_no[]']");

                    if (sectionInput && wtRange && cutLength && qtyInNo) {
                        if (sectionInput.value && wtRange.value && cutLength.value && qtyInNo.value) {
                            payload.orders.push({
                                id: row.dataset.id || null,
                                section_no: sectionInput.value,
                                wt_range: wtRange.value,
                                cut_length: cutLength.value,
                                qty_in_no: qtyInNo.value
                            });
                        }
                    }
                });
            }

            // Validate
            if (!validateForm(formData, payload.orders)) {
                return;
            }

            try {
                let url, method;
                if (window.editMode) {
                    url = `/order/api/requisitions/${window.requisitionId}/`;
                    method = "POST";
                } else {
                    url = "/order/api/requisitions/";
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
                
                const result = await response.json();
                
                if (result.success) {
                    if (result.updated) {
                        showMessage("success", "Requisition updated successfully!");
                        setTimeout(() => window.location.href = '/order/requisitions/', 1500);
                    } else if (result.created) {
                        showMessage("success", `Requisition created successfully! ID: ${result.requisition.requisition_id}`);
                        setTimeout(() => window.location.href = '/order/requisitions/', 1500);
                    } else {
                        showMessage("success", "Requisition saved successfully!");
                        setTimeout(() => window.location.href = '/order/requisitions/', 1500);
                    }
                } else {
                    showMessage("error", "Error: " + (result.message || "Failed to save"));
                }
            } catch (err) {
                console.error('Submit error:', err);
                showMessage("error", "Request failed: " + err.message);
            }
        });
    }

    // ---------------- Set Default Dates ----------------
    const today = new Date().toISOString().split('T')[0];
    const dateInput = document.getElementById("date");
    const expiryDateInput = document.getElementById("expiry_date");
    const dispatchDateInput = document.getElementById("dispatch_date");
    
    if (!window.editMode) {
        if (dateInput && !dateInput.value) dateInput.value = today;
        if (expiryDateInput && !expiryDateInput.value) expiryDateInput.value = today;
        if (dispatchDateInput && !dispatchDateInput.value) dispatchDateInput.value = today;
    }

    // ---------------- Initialize ----------------
    initExampleRows();
    loadEditData();
    
    if (!window.editMode) {
        fetchNextRequisitionId();
    }
});