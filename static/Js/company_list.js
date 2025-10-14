document.addEventListener('DOMContentLoaded', function () {
    const tableBody = document.getElementById('companyTableBody');

    if (tableBody) {
        tableBody.addEventListener('click', function (e) {
            // Delete button
            const deleteBtn = e.target.closest('.delete-btn');
            if (deleteBtn) {
                const companyId = deleteBtn.dataset.companyId;
                const row = deleteBtn.closest('tr');
                const companyName = row.querySelector('td:nth-child(2)').textContent.trim();

                showConfirmationDialog(`Delete company "${companyName}"?`, async () => {
                    try {
                        const response = await fetch(`/extrusions/api/companies/${companyId}/`, {
                            method: 'DELETE',
                            headers: {
                                'Content-Type': 'application/json',
                                'X-CSRFToken': getCSRFToken()
                            }
                        });
                        const result = await response.json();

                        if (result.success) {
                            row.remove();
                            showSuccessPopup(result.message || "Company deleted successfully!");
                        } else {
                            alert(result.message || "Failed to delete company. Try again!");
                        }
                    } catch (err) {
                        console.error(err);
                        alert("An error occurred while deleting the company!");
                    }
                });
                return;
            }

            // View details button
            const viewBtn = e.target.closest('.view-btn');
            if (viewBtn) {
                const companyId = viewBtn.dataset.companyId;
                showCompanyDetails(companyId);
                return;
            }
        });
    }

    // Close company details modal
    const closeDetailsModal = document.getElementById('closeDetailsModal');
    if (closeDetailsModal) {
        closeDetailsModal.addEventListener('click', function () {
            document.getElementById('companyDetailsModal').style.display = 'none';
        });
    }

    // Close modal when clicking overlay
    const companyDetailsModal = document.getElementById('companyDetailsModal');
    if (companyDetailsModal) {
        companyDetailsModal.addEventListener('click', function (e) {
            if (e.target === companyDetailsModal) {
                companyDetailsModal.style.display = 'none';
            }
        });
    }

    // Show company details in modal
    async function showCompanyDetails(companyId) {
        try {
            const response = await fetch(`/extrusions/api/companies/${companyId}/`);
            const result = await response.json();

            if (result.success) {
                const company = result.company;
                const shifts = result.shifts;
                const presses = result.presses;

                const detailsContent = document.getElementById('companyDetailsContent');
                detailsContent.innerHTML = `
                    <div class="detail-section">
                        <h4>Company Information</h4>
                        <div class="detail-item">
                            <span class="detail-label">Name:</span>
                            <span class="detail-value">${company.name}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Contact No:</span>
                            <span class="detail-value">${company.contact_no}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Address:</span>
                            <span class="detail-value">${company.address}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Description:</span>
                            <span class="detail-value">${company.description || 'N/A'}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Created:</span>
                            <span class="detail-value">${company.created_at}</span>
                        </div>
                    </div>

                    <div class="shifts-presses-grid">
                        <div class="detail-section">
                            <h4>Shifts (${shifts.length})</h4>
                            ${shifts.length > 0 ? shifts.map(shift => `
                                <div class="shift-press-item">
                                    <strong>${shift.name}</strong><br>
                                    <small>${shift.timing}</small>
                                </div>
                            `).join('') : '<p>No shifts added yet.</p>'}
                        </div>

                        <div class="detail-section">
                            <h4>Presses (${presses.length})</h4>
                            ${presses.length > 0 ? presses.map(press => `
                                <div class="shift-press-item">
                                    <strong>${press.name}</strong><br>
                                    <small>Capacity: ${press.capacity}</small>
                                </div>
                            `).join('') : '<p>No presses added yet.</p>'}
                        </div>
                    </div>
                `;

                document.getElementById('companyDetailsModal').style.display = 'flex';
            } else {
                alert('Failed to load company details.');
            }
        } catch (err) {
            console.error(err);
            alert('An error occurred while loading company details.');
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