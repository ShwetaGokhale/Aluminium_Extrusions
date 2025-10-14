document.addEventListener('DOMContentLoaded', function () {
    const tableBody = document.getElementById('staffTableBody');

    if (tableBody) {
        tableBody.addEventListener('click', function (e) {
            // Delete button
            const deleteBtn = e.target.closest('.delete-btn');
            if (deleteBtn) {
                const staffId = deleteBtn.dataset.staffId;
                const row = deleteBtn.closest('tr');
                const staffRegisterNo = row.querySelector('td:nth-child(2)').textContent.trim();
                const firstName = row.querySelector('td:nth-child(3)').textContent.trim();
                const lastName = row.querySelector('td:nth-child(4)').textContent.trim();
                const staffName = `${firstName} ${lastName}`;

                showConfirmationDialog(`Delete staff "${staffName}" (${staffRegisterNo})?`, async () => {
                    try {
                        const response = await fetch(`/extrusions/api/staff/${staffId}/`, {
                            method: 'DELETE',
                            headers: {
                                'Content-Type': 'application/json',
                                'X-CSRFToken': getCSRFToken()
                            }
                        });
                        const result = await response.json();

                        if (result.success) {
                            row.remove();
                            showSuccessPopup("Staff deleted successfully!");
                        } else {
                            alert(result.message || "Failed to delete staff. Try again!");
                        }
                    } catch (err) {
                        console.error(err);
                        alert("An error occurred while deleting the staff!");
                    }
                });
                return;
            }
        });
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