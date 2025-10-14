document.addEventListener('DOMContentLoaded', function () {
    const tableBody = document.getElementById('workOrderTableBody');
    const printSelectedBtn = document.getElementById('printSelectedBtn');
    const selectAllCheckbox = document.getElementById('selectAllCheckbox');

    if (tableBody) {
        tableBody.addEventListener('click', function (e) {
            // ✅ Row click selection
            if (!e.target.closest('.action-btn') &&
                !e.target.closest('input[type="checkbox"]') &&
                !e.target.closest('a')) {

                const row = e.target.closest('tr');
                if (row) {
                    const checkbox = row.querySelector('.row-checkbox');
                    if (checkbox) {
                        checkbox.checked = !checkbox.checked;
                        toggleRowSelection(row, checkbox.checked);
                        updatePrintButtonVisibility();
                        updateSelectAllState();
                    }
                }
            }

            // ✅ Checkbox clicks
            const checkbox = e.target.closest('.row-checkbox');
            if (checkbox) {
                const row = checkbox.closest('tr');
                toggleRowSelection(row, checkbox.checked);
                updatePrintButtonVisibility();
                updateSelectAllState();
                return;
            }

            // ✅ Delete button
            const deleteBtn = e.target.closest('.delete-btn');
            if (deleteBtn) {
                const woid = deleteBtn.dataset.woid;
                showConfirmationDialog("Delete this work order?", async () => {
                    try {
                        const response = await fetch(`/order/workorders/delete/${woid}/`, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                'X-CSRFToken': getCSRFToken()
                            }
                        });
                        const result = await response.json();

                        if (result.success) {
                            const row = deleteBtn.closest('tr');
                            if (row) row.remove();
                            showSuccessPopup("Work Order deleted!");
                            updatePrintButtonVisibility();
                        } else {
                            alert(result.message || "Failed to delete. Try again!");
                        }
                    } catch (err) {
                        console.error(err);
                        alert("An error occurred!");
                    }
                });
                return;
            }
        });
    }

    // ✅ Print selected work orders - UPDATED FOR BULK PRINTING
    if (printSelectedBtn) {
        printSelectedBtn.addEventListener('click', function () {
            const selectedIds = getSelectedRowIds();
            if (selectedIds.length > 0) {
                // Create a comma-separated string of IDs for bulk printing
                const idsParam = selectedIds.join(',');
                // Use the existing print work order URL with ids parameter
                const printUrl = `/order/print-work-order/?ids=${idsParam}`;
                window.open(printUrl, '_blank');
            } else {
                alert('Please select at least one work order to print.');
            }
        });
    }

    // ✅ Select All checkbox
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function () {
            const checkboxes = document.querySelectorAll('.row-checkbox');
            checkboxes.forEach(checkbox => {
                const row = checkbox.closest('tr');
                checkbox.checked = selectAllCheckbox.checked;
                toggleRowSelection(row, checkbox.checked);
            });
            updatePrintButtonVisibility();
        });
    }

    // Helpers
    function toggleRowSelection(row, isSelected) {
        const checkbox = row.querySelector('.row-checkbox');
        if (isSelected) {
            row.classList.add('selected-row');
            checkbox.classList.remove('hidden');
            checkbox.classList.add('show-checkbox');
        } else {
            row.classList.remove('selected-row');
            checkbox.classList.add('hidden');
            checkbox.classList.remove('show-checkbox');
        }
    }

    function updatePrintButtonVisibility() {
        const selectedCheckboxes = document.querySelectorAll('.row-checkbox:checked');
        printSelectedBtn.classList.toggle('hidden', selectedCheckboxes.length === 0);
        if (selectedCheckboxes.length > 0) {
            printSelectedBtn.classList.add('flex');
        } else {
            printSelectedBtn.classList.remove('flex');
        }
    }

    function updateSelectAllState() {
        const allCheckboxes = document.querySelectorAll('.row-checkbox');
        const checked = document.querySelectorAll('.row-checkbox:checked');
        selectAllCheckbox.checked = (allCheckboxes.length > 0 && checked.length === allCheckboxes.length);
    }

    function getSelectedRowIds() {
        return Array.from(document.querySelectorAll('.row-checkbox:checked'))
            .map(cb => cb.value);
    }
});

// CSRF
function getCSRFToken() {
    const name = 'csrftoken';
    return document.cookie.split('; ').find(r => r.startsWith(name + '='))?.split('=')[1];
}

// Confirmation dialog
function showConfirmationDialog(message, onConfirm) {
    const overlay = document.getElementById('confirmationModalOverlay');
    const messageElement = document.getElementById('confirmationMessage');
    if (!overlay) return;
    if (messageElement) messageElement.textContent = message;

    overlay.style.display = 'flex';
    const yesBtn = document.getElementById('confirmYesBtn');
    const noBtn = document.getElementById('confirmNoBtn');

    const newYesBtn = yesBtn.cloneNode(true);
    const newNoBtn = noBtn.cloneNode(true);
    yesBtn.parentNode.replaceChild(newYesBtn, yesBtn);
    noBtn.parentNode.replaceChild(newNoBtn, noBtn);

    newYesBtn.onclick = () => { overlay.style.display = 'none'; onConfirm(); };
    newNoBtn.onclick = () => { overlay.style.display = 'none'; };
    overlay.onclick = (e) => { if (e.target === overlay) overlay.style.display = 'none'; };
}

// Success popup
function showSuccessPopup(msg) {
    const popup = document.getElementById('successPopup');
    if (!popup) return;
    popup.textContent = msg;
    popup.classList.add('show');
    setTimeout(() => popup.classList.remove('show'), 2500);
}
