document.addEventListener("DOMContentLoaded", function () {
    const BASE_URL = "/extrusions";

    // Buttons + Modals
    const addNewLotBtn = document.getElementById("addNewLotBtn");
    const addEditLotModalOverlay = document.getElementById("addEditLotModalOverlay");
    const closeAddEditLotModalBtn = document.getElementById("closeAddEditLotModalBtn");
    const addEditLotModalTitle = document.getElementById("addEditLotModalTitle");
    const lotAddEditForm = document.getElementById("lotAddEditForm");
    const lotModalIdInput = document.getElementById("lotModalIdInput");
    const lotCastInput = document.getElementById("lotCastInput");
    const lotPressInput = document.getElementById("lotPressInput");
    const lotDateInput = document.getElementById("lotDateInput");
    const lotAgingInput = document.getElementById("lotAgingInput");
    const lotNumberInput = document.getElementById("lotNumberInput");
    const lotDateAddedInput = document.getElementById("lotDateAddedInput");
    const generateLotBtn = document.getElementById("generateLotBtn");
    const saveLotModalBtn = document.getElementById("saveLotModalBtn");

    const deleteLotModalOverlay = document.getElementById("deleteLotModalOverlay");
    const confirmDeleteLotBtn = document.getElementById("confirmDeleteLotBtn");
    const cancelDeleteLotBtn = document.getElementById("cancelDeleteLotBtn");

    let selectedLotId = null;

    function getCSRFToken() {
        const cookieValue = document.cookie.split("; ").find(row => row.startsWith("csrftoken="));
        return cookieValue ? cookieValue.split("=")[1] : "";
    }

    function showSuccessPopup(message) {
        const popup = document.getElementById("successPopup");
        popup.textContent = message;
        popup.classList.add("show");
        setTimeout(() => popup.classList.remove("show"), 3000);
    }

    // Fetch & render Lots
    async function fetchAndRenderLots() {
        try {
            const response = await fetch(`${BASE_URL}/api/lots/`);
            const data = await response.json();
            const lotTableBody = document.getElementById("lotTableBody");
            lotTableBody.innerHTML = "";

            if (data.success && data.lots.length > 0) {
                let sNo = 1;
                data.lots.forEach(lot => {
                    const row = lotTableBody.insertRow();
                    row.innerHTML = `
                        <td>${sNo++}</td>
                        <td>${lot.cast_no}</td>
                        <td>${lot.press_no_name}</td>
                        <td>${lot.date_of_extrusion}</td>
                        <td>${lot.aging_no}</td>
                        <td>${lot.lot_number}</td>
                        <td class="date-column">${lot.date_added}</td>
                        <td class="actions-column">
                            <button class="editLotBtn edit-btn"
                                data-id="${lot.id}"
                                data-cast="${lot.cast_no}"
                                data-press="${lot.press_no}"
                                data-date="${lot.date_of_extrusion}"
                                data-aging="${lot.aging_no}"
                                data-number="${lot.lot_number}"
                                data-date-added="${lot.date_added}">
                                <i class="fa-solid fa-pen-to-square"></i>
                            </button>
                            <button class="delete-btn" data-lot-id="${lot.id}">
                                <i class="fa-solid fa-trash"></i>
                            </button>
                        </td>`;
                });
                attachEditDeleteListeners();
            } else {
                lotTableBody.innerHTML = `<tr><td colspan="8" class="empty-row">No lots found.</td></tr>`;
            }
        } catch (error) {
            console.error("Error fetching lots:", error);
            showSuccessPopup("Error loading lots.");
        }
    }

    // Open Add Modal
    addNewLotBtn.addEventListener("click", function () {
        addEditLotModalTitle.textContent = "Add New Lot";
        // ✅ Add Tailwind classes to style like <h2 class="text-3xl font-bold italic mb-4 text-purple-800 text-center">
        addEditLotModalTitle.className = 'text-3xl font-bold italic mb-4 text-purple-800 text-center';
        lotAddEditForm.reset();
        lotModalIdInput.value = "";
        lotDateInput.value = new Date().toISOString().slice(0, 10);
        saveLotModalBtn.textContent = "Add Lot";
        addEditLotModalOverlay.style.display = "flex";
    });

    closeAddEditLotModalBtn.addEventListener("click", () => {
        addEditLotModalOverlay.style.display = "none";
    });

    // Generate Lot Number
    generateLotBtn.addEventListener("click", () => {
        const cast = lotCastInput.value.trim();
        const press = lotPressInput.value;
        const date = lotDateInput.value.replaceAll("-", "");
        const aging = lotAgingInput.value.trim();
        if (cast && press && date && aging) {
            lotNumberInput.value = `${cast}-${press}-${date}-${aging}`;
        } else {
            alert("Please fill Cast No, Press, Date and Aging No before generating Lot Number.");
        }
    });

    // Save Lot
    lotAddEditForm.addEventListener("submit", async function (e) {
        e.preventDefault();
        const lotId = lotModalIdInput.value;
        const payload = {
            cast_no: lotCastInput.value,
            press_no: lotPressInput.value,
            date_of_extrusion: lotDateInput.value,
            aging_no: lotAgingInput.value,
            lot_number: lotNumberInput.value,
            date_added: lotDateAddedInput.value
        };

        const url = lotId
            ? `${BASE_URL}/api/lots/${lotId}/`
            : `${BASE_URL}/api/lots/`;

        try {
            const response = await fetch(url, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCSRFToken()
                },
                body: JSON.stringify(payload)
            });
            const data = await response.json();

            if (data.success) {
                showSuccessPopup(lotId ? "Lot updated!" : "Lot added!");
                addEditLotModalOverlay.style.display = "none";
                fetchAndRenderLots();
            } else {
                showSuccessPopup(data.message || "Error saving lot.");
            }
        } catch (error) {
            console.error("Error saving lot:", error);
            showSuccessPopup("Error saving lot.");
        }
    });

    // Attach edit/delete buttons
    function attachEditDeleteListeners() {
        document.querySelectorAll(".editLotBtn").forEach(button => {
            button.onclick = function () {
                addEditLotModalTitle.textContent = "Edit Lot";
                addEditLotModalTitle.className = 'text-3xl font-bold italic mb-4 text-purple-800 text-center';
                lotModalIdInput.value = this.dataset.id;
                lotCastInput.value = this.dataset.cast;
                lotPressInput.value = this.dataset.press;
                lotDateInput.value = this.dataset.date;
                lotAgingInput.value = this.dataset.aging;
                lotNumberInput.value = this.dataset.number;
                lotDateAddedInput.value = this.dataset.dateAdded || new Date().toISOString().slice(0, 10);
                saveLotModalBtn.textContent = "Update Lot";
                addEditLotModalOverlay.style.display = "flex";
            };
        });

        document.querySelectorAll(".delete-btn").forEach(button => {
            button.onclick = function () {
                selectedLotId = this.getAttribute("data-lot-id");
                deleteLotModalOverlay.style.display = "flex";
            };
        });
    }

    confirmDeleteLotBtn.addEventListener("click", async () => {
        if (!selectedLotId) return;
        try {
            const response = await fetch(`${BASE_URL}/api/lots/${selectedLotId}/`, {
                method: "DELETE",
                headers: { "X-CSRFToken": getCSRFToken() }
            });
            const result = await response.json();
            if (result.success) {
                showSuccessPopup("Lot deleted!");
                fetchAndRenderLots();
            } else {
                showSuccessPopup("Delete failed!");
            }
            deleteLotModalOverlay.style.display = "none";
        } catch (error) {
            console.error("Delete error:", error);
            showSuccessPopup("Error deleting lot.");
            deleteLotModalOverlay.style.display = "none";
        } finally {
            selectedLotId = null;
        }
    });

    cancelDeleteLotBtn.addEventListener("click", () => {
        deleteLotModalOverlay.style.display = "none";
        selectedLotId = null;
    });

    // Init
    fetchAndRenderLots();

    // Initially hide Generate button
    generateLotBtn.style.display = "none";

    function toggleGenerateButton() {
        // Treat date as empty if it's auto-filled with today's date
        const today = new Date().toISOString().slice(0, 10);

        const hasInput =
            lotCastInput.value.trim() !== "" ||
            lotPressInput.value.trim() !== "" ||
            (lotDateInput.value.trim() !== "" && lotDateInput.value !== today) ||
            lotAgingInput.value.trim() !== "";

        generateLotBtn.style.display = hasInput ? "inline-block" : "none";
    }

    // Attach listeners
    [lotCastInput, lotPressInput, lotDateInput, lotAgingInput].forEach(input => {
        input.addEventListener("input", toggleGenerateButton);
        input.addEventListener("change", toggleGenerateButton);
    });


});
