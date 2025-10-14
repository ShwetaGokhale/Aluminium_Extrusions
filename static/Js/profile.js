document.addEventListener("DOMContentLoaded", function () {
    const BASE_URL = "/extrusions";

    // DOM elements
    const addNewProfileBtn = document.getElementById("addNewProfileBtn");
    const addEditProfileModalOverlay = document.getElementById("addEditProfileModalOverlay");
    const closeAddEditProfileModalBtn = document.getElementById("closeAddEditProfileModalBtn");
    const addEditProfileModalTitle = document.getElementById("addEditProfileModalTitle");
    const profileAddEditForm = document.getElementById("profileAddEditForm");
    const profileModalIdInput = document.getElementById("profileModalIdInput");
    const categoryInput = document.getElementById("categoryInput");
    const profileNameInput = document.getElementById("profileNameInput");
    const sectionNoInput = document.getElementById("sectionNoInput");
    const lengthInput = document.getElementById("lengthInput");
    const widthInput = document.getElementById("widthInput");
    const thicknessInput = document.getElementById("thicknessInput");
    const weightTypeInput = document.getElementById("weightTypeInput");
    const weightValueInput = document.getElementById("weightValueInput");
    const shapeImageInput = document.getElementById("shapeImageInput");
    const dateAddedInput = document.getElementById("dateAddedInput");
    const saveProfileModalBtn = document.getElementById("saveProfileModalBtn");

    const deleteProfileModalOverlay = document.getElementById("deleteProfileModalOverlay");
    const confirmDeleteProfileBtn = document.getElementById("confirmDeleteProfileBtn");
    const cancelDeleteProfileBtn = document.getElementById("cancelDeleteProfileBtn");

    let selectedProfileId = null;

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

    // Fetch + Render Profiles
    async function fetchAndRenderProfiles() {
        try {
            const response = await fetch(`${BASE_URL}/api/profiles/`, { method: "GET" });
            if (!response.ok) throw new Error(`HTTP ${response.status}`);

            const data = await response.json();
            const profileTableBody = document.getElementById("profileTableBody");
            profileTableBody.innerHTML = "";

            if (data.success && data.profiles.length > 0) {
                let sNo = 1;
                data.profiles.forEach(profile => {
                    const row = profileTableBody.insertRow();
                    row.innerHTML = `
                        <td>${sNo++}</td>
                        <td>${profile.category || '-'}</td>
                        <td>${profile.profile_name}</td>
                        <td>${profile.section_no}</td>
                        <td>${profile.length_mm !== null ? profile.length_mm : '-'}</td>
                        <td>${profile.width_mm !== null ? profile.width_mm : '-'}</td>
                        <td>${profile.thickness_mm !== null ? profile.thickness_mm : '-'}</td>
                        <td>${profile.weight_type} - ${profile.weight_value || '-'}</td>
                        <td>${profile.shape_image ? `<img src="${profile.shape_image}" width="40">` : "-"}</td>
                        <td class="date-column">${profile.date_added}</td>
                        <td class="actions-column">
                            <button class="editProfileBtn edit-btn"
                                data-id="${profile.id}"
                                data-category="${profile.category || ''}"
                                data-name="${profile.profile_name}"
                                data-section="${profile.section_no}"
                                data-length="${profile.length_mm || ''}"
                                data-width="${profile.width_mm || ''}"
                                data-thickness="${profile.thickness_mm || ''}"
                                data-weight-type="${profile.weight_type_key || ''}"
                                data-weight-value="${profile.weight_value || ''}"
                                data-date="${profile.date_added}">
                                <i class="fa-solid fa-pen-to-square"></i>
                            </button>
                            <button class="delete-btn" data-profile-id="${profile.id}">
                                <i class="fa-solid fa-trash"></i>
                            </button>
                        </td>
                    `;
                });
                attachEditDeleteListeners();
            } else {
                profileTableBody.innerHTML = `<tr><td colspan="11" class="empty-row">No profiles found.</td></tr>`;
            }
        } catch (error) {
            console.error("Fetch error:", error);
            showSuccessPopup("Error loading profiles.");
        }
    }

    // Add new profile event
    addNewProfileBtn.addEventListener("click", () => {
        addEditProfileModalTitle.textContent = "Add New Profile";
        addEditProfileModalTitle.className = 'text-3xl font-bold italic mb-4 text-purple-800 text-center';
        profileModalIdInput.value = "";
        categoryInput.value = "";
        profileNameInput.value = "";
        sectionNoInput.value = "";
        lengthInput.value = "";
        widthInput.value = "";
        thicknessInput.value = "";
        weightTypeInput.value = "";
        weightValueInput.value = "";
        shapeImageInput.value = "";
        dateAddedInput.value = new Date().toISOString().split("T")[0];
        saveProfileModalBtn.textContent = "Save Profile";
        addEditProfileModalOverlay.style.display = "flex";
    });

    // Close modal event
    closeAddEditProfileModalBtn.addEventListener("click", () => {
        addEditProfileModalOverlay.style.display = "none";
        profileAddEditForm.reset();
    });

    // Close modal when clicking overlay
    addEditProfileModalOverlay.addEventListener("click", (e) => {
        if (e.target === addEditProfileModalOverlay) {
            addEditProfileModalOverlay.style.display = "none";
            profileAddEditForm.reset();
        }
    });

    function attachEditDeleteListeners() {
        document.querySelectorAll(".editProfileBtn").forEach(button => {
            button.onclick = function () {
                addEditProfileModalTitle.textContent = "Edit Profile";
                addEditProfileModalTitle.className = 'text-3xl font-bold italic mb-4 text-purple-800 text-center';
                profileModalIdInput.value = this.dataset.id;
                categoryInput.value = this.dataset.category;
                profileNameInput.value = this.dataset.name;
                sectionNoInput.value = this.dataset.section;
                lengthInput.value = this.dataset.length;
                widthInput.value = this.dataset.width;
                thicknessInput.value = this.dataset.thickness;
                weightTypeInput.value = this.dataset.weightType;
                weightValueInput.value = this.dataset.weightValue;
                shapeImageInput.value = "";
                dateAddedInput.value = this.dataset.date;
                saveProfileModalBtn.textContent = "Update Profile";
                addEditProfileModalOverlay.style.display = "flex";
            };
        });

        document.querySelectorAll(".delete-btn").forEach(button => {
            button.onclick = function () {
                selectedProfileId = this.getAttribute("data-profile-id");
                deleteProfileModalOverlay.style.display = "flex";
            };
        });
    }

    // Submit Add/Edit form
    profileAddEditForm.addEventListener("submit", async function (e) {
        e.preventDefault();
        const formData = new FormData(profileAddEditForm);
        const profileId = profileModalIdInput.value;

        let url = profileId
            ? `${BASE_URL}/api/profiles/${profileId}/`
            : `${BASE_URL}/api/profiles/`;

        try {
            const response = await fetch(url, {
                method: "POST",
                headers: { "X-CSRFToken": getCSRFToken() },
                body: formData
            });

            const data = await response.json();

            if (data.success) {
                showSuccessPopup(profileId ? "Profile updated!" : "Profile added!");
                addEditProfileModalOverlay.style.display = "none";
                profileAddEditForm.reset();
                fetchAndRenderProfiles();
            } else {
                showSuccessPopup(data.message || "Error saving profile.");
            }
        } catch (error) {
            console.error("Save error:", error);
            showSuccessPopup("Error saving profile.");
        }
    });

    // Delete confirmation
    confirmDeleteProfileBtn.addEventListener("click", async () => {
        if (!selectedProfileId) return;
        try {
            const response = await fetch(`${BASE_URL}/api/profiles/${selectedProfileId}/`, {
                method: "DELETE",
                headers: { "X-CSRFToken": getCSRFToken() }
            });
            const result = await response.json();

            if (result.success) {
                showSuccessPopup("Profile deleted successfully!");
            } else {
                showSuccessPopup("Delete failed.");
            }
            deleteProfileModalOverlay.style.display = "none";
            fetchAndRenderProfiles();
        } catch (error) {
            console.error("Delete error:", error);
            showSuccessPopup("Error deleting profile.");
        } finally {
            selectedProfileId = null;
        }
    });

    // Cancel delete
    cancelDeleteProfileBtn.addEventListener("click", () => {
        deleteProfileModalOverlay.style.display = "none";
        selectedProfileId = null;
    });

    // Close delete modal when clicking overlay
    deleteProfileModalOverlay.addEventListener("click", (e) => {
        if (e.target === deleteProfileModalOverlay) {
            deleteProfileModalOverlay.style.display = "none";
            selectedProfileId = null;
        }
    });

    // Initialize by fetching profiles
    fetchAndRenderProfiles();
});