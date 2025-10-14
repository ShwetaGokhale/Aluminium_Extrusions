document.addEventListener('DOMContentLoaded', function () {
    const tableBody = document.getElementById('dieTableBody');

    if (tableBody) {
        tableBody.addEventListener('click', function (e) {
            // Delete button
            const deleteBtn = e.target.closest('.delete-btn');
            if (deleteBtn) {
                const dieId = deleteBtn.dataset.dieId;
                const row = deleteBtn.closest('tr');
                const dieNo = row.querySelector('td:nth-child(2)').textContent.trim();

                showConfirmationDialog(`Delete die "${dieNo}"?`, async () => {
                    try {
                        const response = await fetch(`/extrusions/api/dies/${dieId}/`, {
                            method: 'DELETE',
                            headers: {
                                'Content-Type': 'application/json',
                                'X-CSRFToken': getCSRFToken()
                            }
                        });
                        const result = await response.json();

                        if (result.success) {
                            row.remove();
                            showSuccessPopup(result.message || "Die deleted successfully!");
                            
                            // Update serial numbers
                            updateSerialNumbers();
                        } else {
                            alert(result.message || "Failed to delete die. Try again!");
                        }
                    } catch (err) {
                        console.error(err);
                        alert("An error occurred while deleting the die!");
                    }
                });
                return;
            }

            // View details button
            const viewBtn = e.target.closest('.view-btn');
            if (viewBtn) {
                const dieId = viewBtn.dataset.dieId;
                showDieDetails(dieId);
                return;
            }
        });
    }

    // Update serial numbers after deletion
    function updateSerialNumbers() {
        const rows = tableBody.querySelectorAll('tr');
        rows.forEach((row, index) => {
            const firstCell = row.querySelector('td:first-child');
            if (firstCell && !row.querySelector('td[colspan]')) {
                firstCell.textContent = index + 1;
            }
        });
    }

    // Close die details modal
    const closeDetailsModal = document.getElementById('closeDetailsModal');
    if (closeDetailsModal) {
        closeDetailsModal.addEventListener('click', function () {
            document.getElementById('dieDetailsModal').style.display = 'none';
        });
    }

    // Close modal when clicking overlay
    const dieDetailsModal = document.getElementById('dieDetailsModal');
    if (dieDetailsModal) {
        dieDetailsModal.addEventListener('click', function (e) {
            if (e.target === dieDetailsModal) {
                dieDetailsModal.style.display = 'none';
            }
        });
    }

    // Show die details in modal
    async function showDieDetails(dieId) {
        try {
            const response = await fetch(`/extrusions/api/dies/${dieId}/`);
            const result = await response.json();

            if (result.success) {
                const die = result.die;

                const detailsContent = document.getElementById('dieDetailsContent');
                detailsContent.innerHTML = `
                    <div class="detail-section">
                        <h4>Die Information</h4>
                        <div class="detail-item">
                            <span class="detail-label">Die ID:</span>
                            <span class="detail-value">${die.die_id}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Date:</span>
                            <span class="detail-value">${die.date}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Die No:</span>
                            <span class="detail-value">${die.die_no}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Die Name:</span>
                            <span class="detail-value">${die.die_name}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Store Location:</span>
                            <span class="detail-value">${die.store_location}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Press:</span>
                            <span class="detail-value">${die.press_name}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Supplier:</span>
                            <span class="detail-value">${die.supplier_name}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Project No:</span>
                            <span class="detail-value">${die.project_no || 'N/A'}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Date of Receipt:</span>
                            <span class="detail-value">${die.date_of_receipt || 'N/A'}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">No of Cavity:</span>
                            <span class="detail-value">${die.no_of_cavity}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Req Weight:</span>
                            <span class="detail-value">${die.req_weight}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Size:</span>
                            <span class="detail-value">${die.size}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Die Material:</span>
                            <span class="detail-value">${die.die_material}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Hardness:</span>
                            <span class="detail-value">${die.hardness}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Type:</span>
                            <span class="detail-value">${die.type}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Description:</span>
                            <span class="detail-value">${die.description || 'N/A'}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Remark:</span>
                            <span class="detail-value">${die.remark || 'N/A'}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Created:</span>
                            <span class="detail-value">${die.created_at}</span>
                        </div>
                    </div>

                    ${die.image_url ? `
                        <div class="detail-section">
                            <h4>Die Image</h4>
                            <div class="die-image">
                                <img src="${die.image_url}" alt="Die Image">
                            </div>
                        </div>
                    ` : ''}
                `;

                document.getElementById('dieDetailsModal').style.display = 'flex';
            } else {
                alert('Failed to load die details.');
            }
        } catch (err) {
            console.error(err);
            alert('An error occurred while loading die details.');
        }
    }
});

// CSRF Token function
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