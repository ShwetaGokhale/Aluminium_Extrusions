document.addEventListener("DOMContentLoaded", function () {
    // ✅ FIXED: Change this to match your URL pattern
    const BASE_URL = "/extrusions";  

    const addNewPressBtn = document.getElementById('addNewPressBtn');
    const addEditPressModalOverlay = document.getElementById("addEditPressModalOverlay");
    const closeAddEditPressModalBtn = document.getElementById("closeAddEditPressModalBtn");
    const addEditPressModalTitle = document.getElementById('addEditPressModalTitle');
    const pressAddEditForm = document.getElementById('pressAddEditForm');
    const pressModalIdInput = document.getElementById('pressModalIdInput');
    const pressModalNameInput = document.getElementById('pressModalNameInput');
    const pressModalDateInput = document.getElementById('pressModalDateInput');
    const savePressModalBtn = document.getElementById('savePressModalBtn');

    const deletePressModalOverlay = document.getElementById("deletePressModalOverlay");
    const confirmDeletePressBtn = document.getElementById("confirmDeletePressBtn");
    const cancelDeletePressBtn = document.getElementById("cancelDeletePressBtn");

    let selectedPressId = null;

    function getCSRFToken() {
        const cookieValue = document.cookie.split('; ').find(row => row.startsWith('csrftoken='));
        return cookieValue ? cookieValue.split('=')[1] : '';
    }

    function showSuccessPopup(message) {
        const popup = document.getElementById('successPopup');
        popup.textContent = message;
        popup.classList.add('show');
        setTimeout(() => {
            popup.classList.remove('show');
        }, 3000);
    }

    async function fetchAndRenderPresses() {
        try {
            // ✅ This will now call: /extrusions/api/presses/
            const response = await fetch(`${BASE_URL}/api/presses/`, {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' },
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();

            const pressTableBody = document.getElementById('pressTableBody');
            pressTableBody.innerHTML = '';

            if (data.success && data.presses.length > 0) {
                let sNo = 1;
                data.presses.forEach(press => {
                    const row = pressTableBody.insertRow();
                    row.innerHTML = `
                        <td>${sNo++}</td>
                        <td>${press.press_name}</td>
                        <td class="date-column">${press.date_added}</td>
                        <td class="actions-column">
                            <button class="editPressBtn edit-btn"
                                data-id="${press.id}"
                                data-name="${press.press_name}"
                                data-date="${press.date_added}">
                                <i class="fa-solid fa-pen-to-square"></i>
                            </button>
                            <button class="delete-btn" data-press-id="${press.id}">
                                <i class="fa-solid fa-trash"></i>
                            </button>
                        </td>
                    `;
                });
                attachEditDeleteListeners();
            } else {
                pressTableBody.innerHTML = '<tr><td colspan="6" class="empty-row">No presses found.</td></tr>';
            }
        } catch (error) {
            console.error('Fetch error:', error);
            showSuccessPopup(`Error loading presses: ${error.message}`);
        }
    }

    addNewPressBtn.addEventListener('click', function () {
        addEditPressModalTitle.textContent = 'Add New Press';
        // ✅ Add Tailwind classes to style like <h2 class="text-3xl font-bold italic mb-4 text-purple-800 text-center">
        addEditPressModalTitle.className = 'text-3xl font-bold italic mb-4 text-purple-800 text-center';
        pressModalIdInput.value = '';
        pressModalNameInput.value = '';
        pressModalDateInput.value = new Date().toISOString().slice(0, 10);
        savePressModalBtn.textContent = 'Add Press';
        addEditPressModalOverlay.style.display = 'flex';
    });

    closeAddEditPressModalBtn.addEventListener('click', () => {
        addEditPressModalOverlay.style.display = 'none';
        pressAddEditForm.reset();
    });

    function attachEditDeleteListeners() {
        document.querySelectorAll(".editPressBtn").forEach(button => {
            button.onclick = function () {
                addEditPressModalTitle.textContent = 'Edit Press';
                addEditPressModalTitle.className = 'text-3xl font-bold italic mb-4 text-purple-800 text-center';
                pressModalIdInput.value = this.dataset.id;
                pressModalNameInput.value = this.dataset.name;
                pressModalDateInput.value = this.dataset.date;
                savePressModalBtn.textContent = 'Update Press';
                addEditPressModalOverlay.style.display = "flex";
            };
        });
        
        document.querySelectorAll('.delete-btn').forEach(button => {
            button.onclick = function () {
                selectedPressId = this.getAttribute("data-press-id");
                deletePressModalOverlay.style.display = "flex";
            };
        });
    }

    pressAddEditForm.addEventListener('submit', async function (e) {
        e.preventDefault();
        const formData = new FormData(pressAddEditForm);
        const pressId = pressModalIdInput.value;
        const payload = {
            press_name: formData.get('press_name'),
            date_added: formData.get('date_added'),
        };

        // ✅ Updated URLs to match Django patterns
        const url = pressId
            ? `${BASE_URL}/api/presses/${pressId}/`  // For editing
            : `${BASE_URL}/api/presses/`;          // For adding

        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();

            if (data.success) {
                showSuccessPopup(pressId ? "Press updated successfully!" : "Press added successfully!");
                addEditPressModalOverlay.style.display = "none";
                pressAddEditForm.reset();
                fetchAndRenderPresses();
            } else {
                showSuccessPopup(data.message || "Error saving press.");
            }
        } catch (error) {
            console.error("Error:", error);
            showSuccessPopup(`Error saving press: ${error.message}`);
        }
    });

    confirmDeletePressBtn.addEventListener("click", async () => {
        if (!selectedPressId) return;

        try {
            // ✅ Updated delete URL
            const response = await fetch(`${BASE_URL}/api/presses/${selectedPressId}/`, {
                method: "DELETE",  // ✅ Changed to DELETE method
                headers: {
                    'X-CSRFToken': getCSRFToken(),
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const result = await response.json();

            if (result.success) {
                showSuccessPopup("Press deleted successfully.");
            } else {
                showSuccessPopup("Delete failed: " + (result.error || "Unknown error"));
            }
            
            deletePressModalOverlay.style.display = "none";
            fetchAndRenderPresses();
        } catch (error) {
            console.error("Delete error:", error);
            showSuccessPopup(`Error deleting press: ${error.message}`);
            deletePressModalOverlay.style.display = "none";
        } finally {
            selectedPressId = null;
        }
    });

    cancelDeletePressBtn.addEventListener("click", () => {
        deletePressModalOverlay.style.display = "none";
        selectedPressId = null;
    });

    // Initialize the page
    fetchAndRenderPresses();
});