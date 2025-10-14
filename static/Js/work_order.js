document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("workOrderForm");
    const goodsBody = document.getElementById("goodsTableBody");
    const financeBody = document.getElementById("financeTableBody");

    // ---------------- Popup Message ----------------
    function showMessage(type, text) {
        const popup = document.getElementById("popupMessage");
        if (!popup) return;

        popup.textContent = text;
        popup.className = "popup-message"; // reset
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
            if (goodsBody) {
                goodsBody.innerHTML = `
                    <tr class="example-row" style="background:#f9f9f9; color:#888;">
                        <td><input type="text" placeholder="A101" disabled></td>
                        <td><input type="text" placeholder="10-20" disabled></td>
                        <td><input type="number" placeholder="5.5" disabled></td>
                        <td><input type="text" placeholder="T6" disabled></td>
                        <td><input type="text" placeholder="Box" disabled></td>
                        <td><input type="number" placeholder="100" disabled></td>
                        <td><input type="number" placeholder="10" disabled></td>
                        <td><input type="number" placeholder="1000" disabled></td>
                        <td><input type="number" placeholder="5000" disabled></td>
                        <td></td>
                    </tr>
                `;
            }
            if (financeBody) {
                financeBody.innerHTML = `
                    <tr class="example-row" style="background:#f9f9f9; color:#888;">
                        <td><input type="number" placeholder="1000" disabled></td>
                        <td><input type="text" placeholder="SGST" disabled></td>
                        <td><input type="number" placeholder="0.08" disabled></td>
                        <td><input type="number" placeholder="1080" disabled></td>
                        <td></td>
                    </tr>
                `;
            }
        }
    }

    // ---------------- Load Edit Data ----------------
    function loadEditData() {
        if (window.editMode && window.goodsData && window.financeData) {
            window.goodsData.forEach(good => addGoodsRow(good));
            window.financeData.forEach(finance => addFinanceRow(finance));
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
    const input = document.getElementById("customerSearchInput");
    const dropdown = document.getElementById("customerDropdownList");
    const hiddenId = document.getElementById("id_customer");
    const contactField = document.getElementById("customerContact");
    const addressField = document.getElementById("customerAddress");

    if (input && dropdown && hiddenId) {
        attachDropdown(input, dropdown, hiddenId, (item) => {
            if (contactField) contactField.value = item.dataset.contact || '';
            if (addressField) addressField.value = item.dataset.address || '';
        });
    }

    // ---------------- Add Goods Row ----------------
    function addGoodsRow(data = {}) {
        const sectionOptions = window.sectionOptions || [];
        const alloyOptions = window.alloyOptions || [];

        const row = document.createElement("tr");
        if (data.id) row.dataset.id = data.id;   // keep DB id for update

        row.innerHTML = `
            <td>
              <div class="custom-searchable-select-wrapper">
                <input type="text" class="searchable-input section-input" placeholder="Search Section" 
                       value="${data.section_no__section_no || ''}">
                <i class="fa-solid fa-chevron-down dropdown-icon"></i>
                <input type="hidden" name="section_no[]" value="${data.section_no__id || ''}">
                <div class="custom-dropdown-list section-dropdown">
                  ${sectionOptions.map(opt => `<div class="dropdown-item" data-value="${opt[0]}">${opt[1]}</div>`).join("")}
                </div>
              </div>
            </td>
            <td><input type="text" name="wt_range[]" value="${data.wt_range || ''}"></td>
            <td><input type="number" step="0.01" name="cut_length[]" value="${data.cut_length || ''}"></td>
            <td>
              <div class="custom-searchable-select-wrapper">
                <input type="text" class="searchable-input alloy-input" placeholder="Search Alloy"
                       value="${data.alloy_temper__alloy_name || ''}">
                <i class="fa-solid fa-chevron-down dropdown-icon"></i>
                <input type="hidden" name="alloy_temper[]" value="${data.alloy_temper__id || ''}">
                <div class="custom-dropdown-list alloy-dropdown">
                  ${alloyOptions.map(opt => `<div class="dropdown-item" data-value="${opt.id}">${opt.alloy_name}</div>`).join("")}
                </div>
              </div>
            </td>
            <td><input type="text" name="pack[]" value="${data.pack || ''}"></td>
            <td><input type="number" name="qty[]" value="${data.qty || ''}"></td>
            <td><input type="number" name="total_pack[]" value="${data.total_pack || ''}"></td>
            <td><input type="number" name="total_no[]" value="${data.total_no || ''}"></td>
            <td><input type="number" step="0.01" name="amount[]" value="${data.amount || ''}"></td>
            <td>
                <button type="button" class="delete-row">
                    <i class="fa-solid fa-trash"></i>
                </button>
            </td>
        `;

        const exampleRow = goodsBody.querySelector(".example-row");
        if (exampleRow) exampleRow.remove();

        goodsBody.appendChild(row);

        attachDropdown(row.querySelector(".section-input"), row.querySelector(".section-dropdown"), row.querySelector("input[name='section_no[]']"));
        attachDropdown(row.querySelector(".alloy-input"), row.querySelector(".alloy-dropdown"), row.querySelector("input[name='alloy_temper[]']"));
    }

    // ---------------- Add Finance Row ----------------
    function addFinanceRow(data = {}) {
        const row = document.createElement("tr");
        if (data.id) row.dataset.id = data.id;   // keep DB id for update

        row.innerHTML = `
            <td><input type="number" step="0.01" name="fin_amount[]" value="${data.amount || ''}"></td>
            <td>
                <select name="fin_tax_type[]">
                    <option value="SGST" ${data.tax_type === 'SGST' ? 'selected' : ''}>SGST</option>
                    <option value="CGST" ${data.tax_type === 'CGST' ? 'selected' : ''}>CGST</option>
                    <option value="IGST" ${data.tax_type === 'IGST' ? 'selected' : ''}>IGST</option>
                </select>
            </td>
            <td><input type="number" step="0.01" name="fin_tax_amount[]" readonly></td>
            <td><input type="number" step="0.01" name="fin_total_amount[]" readonly></td>
            <td>
                <button type="button" class="delete-row">
                    <i class="fa-solid fa-trash"></i>
                </button>
            </td>
        `;

        const exampleRow = financeBody.querySelector(".example-row");
        if (exampleRow) exampleRow.remove();

        financeBody.appendChild(row);

        const amountInput = row.querySelector("input[name='fin_amount[]']");
        const taxType = row.querySelector("select[name='fin_tax_type[]']");
        const taxAmount = row.querySelector("input[name='fin_tax_amount[]']");
        const totalAmount = row.querySelector("input[name='fin_total_amount[]']");

        function recalc() {
            let amount = parseFloat(amountInput.value) || 0;
            let tax = 0;
            if (taxType.value === "SGST" || taxType.value === "CGST") tax = amount * 0.08;
            else if (taxType.value === "IGST") tax = amount * 0.18;
            taxAmount.value = tax.toFixed(2);
            totalAmount.value = (amount + tax).toFixed(2);
        }

        amountInput.addEventListener("input", recalc);
        taxType.addEventListener("change", recalc);
        
        if (data.amount) recalc();
    }

    // ---------------- Add Row Buttons ----------------
    document.getElementById("addGoodsBtn")?.addEventListener("click", e => { e.preventDefault(); addGoodsRow(); });
    document.getElementById("addFinanceBtn")?.addEventListener("click", e => { e.preventDefault(); addFinanceRow(); });

    // ---------------- Delete Row ----------------
    document.addEventListener("click", function (e) {
        const btn = e.target.closest(".delete-row");
        if (btn) e.target.closest("tr").remove();
    });

    // ---------------- Submit Form ----------------
    if (form) {
        form.addEventListener("submit", async function (e) {
            e.preventDefault();
            const formData = new FormData(form);

            let payload = {
                customer: formData.get("customer"),
                contact_no: formData.get("contact_no"),
                address: formData.get("address"),
                sales_manager: formData.get("sales_manager"),
                payment_terms: formData.get("payment_terms"),
                expiry_date: formData.get("expiry_date"),
                dispatch_date: formData.get("dispatch_date"),
                delivery_date: formData.get("delivery_date"),
                delivery_address: formData.get("delivery_address"),
                goods: [],
                finance: []
            };

            if (goodsBody) {
                goodsBody.querySelectorAll("tr:not(.example-row)").forEach(row => {
                    const sectionInput = row.querySelector("input[name='section_no[]']");
                    if (sectionInput) {
                        payload.goods.push({
                            id: row.dataset.id || null,  // <-- include DB id
                            section_no: sectionInput.value || '',
                            wt_range: row.querySelector("input[name='wt_range[]']")?.value || '',
                            cut_length: row.querySelector("input[name='cut_length[]']")?.value || '',
                            alloy_temper: row.querySelector("input[name='alloy_temper[]']")?.value || '',
                            pack: row.querySelector("input[name='pack[]']")?.value || '',
                            qty: row.querySelector("input[name='qty[]']")?.value || '',
                            total_pack: row.querySelector("input[name='total_pack[]']")?.value || '',
                            total_no: row.querySelector("input[name='total_no[]']")?.value || '',
                            amount: row.querySelector("input[name='amount[]']")?.value || "0"
                        });
                    }
                });
            }

            if (financeBody) {
                financeBody.querySelectorAll("tr:not(.example-row)").forEach(row => {
                    const amountInput = row.querySelector("input[name='fin_amount[]']");
                    if (amountInput) {
                        payload.finance.push({
                            id: row.dataset.id || null,  // <-- include DB id
                            amount: amountInput.value || "0",
                            tax_type: row.querySelector("select[name='fin_tax_type[]']")?.value || 'SGST',
                        });
                    }
                });
            }

            try {
                let url, method;
                if (window.editMode) {
                    url = `/order/workorders/edit/${window.workOrderId}/`;
                    method = "POST";
                } else {
                    url = "/order/api/workorders/";
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
                        showMessage("success", "Work Order updated successfully!");
                        setTimeout(() => window.location.href = '/order/workorders/', 1500);
                    } else if (result.created) {
                        showMessage("success", "Work Order created successfully!");
                        form.reset(); initExampleRows();
                    } else {
                        showMessage("success", "Work Order saved successfully!");
                        if (window.editMode) {
                            setTimeout(() => window.location.href = '/order/workorders/', 1500);
                        } else {
                            form.reset(); initExampleRows();
                        }
                    }
                } else {
                    showMessage("error", "❌ Error: " + (result.message || "Failed to save"));
                }
            } catch (err) {
                showMessage("error", "❌ Request failed: " + err.message);
            }
        });
    }

    // ---------------- Initialize ----------------
    initExampleRows();
    loadEditData();
});
