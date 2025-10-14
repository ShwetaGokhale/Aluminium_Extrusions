document.addEventListener("DOMContentLoaded", function () {
    const tableBody = document.getElementById("productionPlanTableBody");
    const modalOverlay = document.getElementById("confirmationModalOverlay");
    const confirmYesBtn = document.getElementById("confirmYesBtn");
    const confirmNoBtn = document.getElementById("confirmNoBtn");
    const confirmationMessage = document.getElementById("confirmationMessage");
    const successPopup = document.getElementById("successPopup");

    let currentIdToDelete = null;

    // ---------------- Show Success Popup ----------------
    function showSuccessPopup(message) {
        if (successPopup) {
            successPopup.textContent = message;
            successPopup.classList.add("show");
            setTimeout(() => successPopup.classList.remove("show"), 2500);
        }
    }

    // ---------------- Show Confirmation Modal ----------------
    function showConfirmationModal(message, onConfirm) {
        if (!modalOverlay) return;

        if (confirmationMessage) {
            confirmationMessage.textContent = message;
        }

        // Show modal using display flex
        modalOverlay.style.display = "flex";

        // Clone buttons to remove old event listeners
        const newYesBtn = confirmYesBtn.cloneNode(true);
        const newNoBtn = confirmNoBtn.cloneNode(true);
        confirmYesBtn.parentNode.replaceChild(newYesBtn, confirmYesBtn);
        confirmNoBtn.parentNode.replaceChild(newNoBtn, confirmNoBtn);

        // Add new event listeners
        newYesBtn.onclick = () => {
            modalOverlay.style.display = "none";
            if (onConfirm) onConfirm();
        };

        newNoBtn.onclick = () => {
            modalOverlay.style.display = "none";
            currentIdToDelete = null;
        };

        // Close on overlay click
        modalOverlay.onclick = (e) => {
            if (e.target === modalOverlay) {
                modalOverlay.style.display = "none";
                currentIdToDelete = null;
            }
        };
    }

    // ---------------- Handle Delete Button Clicks via Event Delegation ----------------
    if (tableBody) {
        tableBody.addEventListener("click", function (e) {
            const deleteBtn = e.target.closest(".delete-btn");

            if (deleteBtn) {
                e.preventDefault();
                e.stopPropagation();

                currentIdToDelete = deleteBtn.dataset.planId;

                if (!currentIdToDelete) {
                    console.error("No plan ID found");
                    return;
                }

                const row = deleteBtn.closest("tr");
                let productionPlanId = "";

                // Try to get production plan ID from table
                const cells = row.querySelectorAll("td");
                if (cells.length > 1) {
                    productionPlanId = cells[1].textContent.trim();
                }

                const message = productionPlanId
                    ? `Are you sure you want to delete Production Plan "${productionPlanId}"?`
                    : "Are you sure you want to delete this Production Plan?";

                showConfirmationModal(message, confirmDelete);
            }
        });
    }

    // ---------------- Confirm Delete Function ----------------
    async function confirmDelete() {
        if (!currentIdToDelete) {
            console.error("No ID to delete");
            return;
        }

        try {
            const response = await fetch(`/planning/production-plan/delete/${currentIdToDelete}/`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCSRFToken(),
                },
            });

            const data = await response.json();

            if (data.success) {
                showSuccessPopup(data.message || "Production Plan deleted successfully!");

                // Remove the row from table
                const row = document.querySelector(`tr[data-plan-id="${currentIdToDelete}"]`);
                if (row) {
                    row.style.transition = "opacity 0.3s ease";
                    row.style.opacity = "0";
                    setTimeout(() => {
                        row.remove();
                        // Update serial numbers
                        updateSerialNumbers();
                    }, 300);
                }

                currentIdToDelete = null;
            } else {
                alert(data.message || "Failed to delete production plan. Please try again.");
            }
        } catch (error) {
            console.error("Error deleting production plan:", error);
            alert("Network error while deleting production plan. Please try again.");
        }
    }

    // ---------------- Update Serial Numbers After Deletion ----------------
    function updateSerialNumbers() {
        const rows = tableBody.querySelectorAll("tr");
        rows.forEach((row, index) => {
            const firstCell = row.querySelector("td:first-child");
            if (firstCell && !row.querySelector("td[colspan]")) {
                firstCell.textContent = index + 1;
            }
        });
    }

    // ---------------- Get CSRF Token ----------------
    function getCSRFToken() {
        const name = "csrftoken";
        const cookie = document.cookie
            .split("; ")
            .find((r) => r.startsWith(name + "="));
        return cookie ? cookie.split("=")[1] : null;
    }
});