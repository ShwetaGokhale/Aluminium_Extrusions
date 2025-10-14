document.addEventListener('DOMContentLoaded', function () {
    const tableBody = document.getElementById('alloyTableBody');

    if (tableBody) {
        tableBody.addEventListener('click', function (e) {
            // Delete button
            const deleteBtn = e.target.closest('.delete-btn');
            if (deleteBtn) {
                const alloyId = deleteBtn.dataset.alloyId;
                const row = deleteBtn.closest('tr');
                const alloyCode = row.querySelector('td:nth-child(2)').textContent.trim();

                showConfirmationDialog(`Delete alloy "${alloyCode}"?`, async () => {
                    try {
                        const response = await fetch(`/extrusions/api/alloys/${alloyId}/`, {
                            method: 'DELETE',
                            headers: {
                                'Content-Type': 'application/json',
                                'X-CSRFToken': getCSRFToken()
                            }
                        });
                        const result = await response.json();

                        if (result.success) {
                            row.remove();
                            showSuccessPopup("Alloy deleted successfully!");
                        } else {
                            alert(result.message || "Failed to delete alloy. Try again!");
                        }
                    } catch (err) {
                        console.error(err);
                        alert("An error occurred while deleting the alloy!");
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