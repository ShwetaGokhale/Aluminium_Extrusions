document.addEventListener('DOMContentLoaded', function () {
    const tableBody = document.getElementById('requisitionTableBody');
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
                const requisitionId = deleteBtn.dataset.requisitionId;
                const row = deleteBtn.closest('tr');
                
                // Get requisition number for confirmation message
                let requisitionNo = '';
                const cells = row.querySelectorAll('td');
                if (cells.length > 1) {
                    requisitionNo = cells[1].textContent.trim();
                }

                showConfirmationDialog(`Delete requisition "${requisitionNo}"?`, async () => {
                    try {
                        const response = await fetch(`/order/requisitions/delete/${requisitionId}/`, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                'X-CSRFToken': getCSRFToken()
                            }
                        });
                        const result = await response.json();

                        if (result.success) {
                            showSuccessPopup("Requisition deleted successfully!");
                            // Reload page after short delay
                            setTimeout(() => {
                                window.location.reload();
                            }, 1000);
                        } else {
                            alert(result.message || "Failed to delete requisition. Try again!");
                        }
                    } catch (err) {
                        console.error(err);
                        alert("An error occurred while deleting the requisition!");
                    }
                });
                return;
            }
        });
    }

    // ✅ Print selected requisitions
    if (printSelectedBtn) {
        printSelectedBtn.addEventListener('click', function () {
            const selectedIds = getSelectedRowIds();
            if (selectedIds.length > 0) {
                // Create a comma-separated string of IDs for bulk printing
                const idsParam = selectedIds.join(',');
                // Use the print requisition URL with ids parameter
                const printUrl = `/order/print-requisition/?ids=${idsParam}`;
                window.open(printUrl, '_blank');
            } else {
                alert('Please select at least one requisition to print.');
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

    // Helper Functions
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
        
        // Use visibility toggle instead of display toggle to prevent layout shift
        if (selectedCheckboxes.length > 0) {
            printSelectedBtn.classList.remove('hidden');
        } else {
            printSelectedBtn.classList.add('hidden');
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

// CSRF Token function
function getCSRFToken() {
    const name = 'csrftoken';
    const cookie = document.cookie.split('; ').find(r => r.startsWith(name + '='));
    return cookie ? cookie.split('=')[1] : null;
}

// Confirmation dialog
function showConfirmationDialog(message, onConfirm) {
    const overlay = document.getElementById('confirmationModalOverlay');
    const messageElement = document.getElementById('confirmationMessage');
    
    if (!overlay) return;
    
    if (messageElement) {
        messageElement.textContent = message;
    }

    overlay.style.display = 'flex';
    
    const yesBtn = document.getElementById('confirmYesBtn');
    const noBtn = document.getElementById('confirmNoBtn');

    // Clone buttons to remove previous event listeners
    const newYesBtn = yesBtn.cloneNode(true);
    const newNoBtn = noBtn.cloneNode(true);
    yesBtn.parentNode.replaceChild(newYesBtn, yesBtn);
    noBtn.parentNode.replaceChild(newNoBtn, noBtn);

    // Add new event listeners
    newYesBtn.onclick = () => { 
        overlay.style.display = 'none'; 
        onConfirm(); 
    };
    
    newNoBtn.onclick = () => { 
        overlay.style.display = 'none'; 
    };
    
    // Close on overlay click
    overlay.onclick = (e) => { 
        if (e.target === overlay) {
            overlay.style.display = 'none'; 
        }
    };
}

// Success popup
function showSuccessPopup(msg) {
    const popup = document.getElementById('successPopup');
    
    if (!popup) return;
    
    popup.textContent = msg;
    popup.classList.add('show');
    
    setTimeout(() => {
        popup.classList.remove('show');
    }, 2500);
}