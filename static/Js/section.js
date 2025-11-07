document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("sectionForm");
    const sectionIdDisplay = document.getElementById("section_id_display");
    const dateField = document.getElementById("date");
    const imageInput = document.getElementById("section_image");
    const imagePreview = document.getElementById("imagePreview");
    const previewImg = document.getElementById("previewImg");

    // ---------------- Image Preview ----------------
    if (imageInput) {
        imageInput.addEventListener("change", function (e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function (event) {
                    previewImg.src = event.target.result;
                    imagePreview.classList.remove("hidden");
                };
                reader.readAsDataURL(file);
            } else {
                imagePreview.classList.add("hidden");
            }
        });
    }

    // ---------------- Popup Message ----------------
    function showMessage(type, text) {
        const popup = document.getElementById("popupMessage");
        if (!popup) return;

        popup.textContent = text;
        popup.className = "popup-message";
        if (type === "error") popup.classList.add("error");

        popup.classList.remove("hidden");
        requestAnimationFrame(() => popup.classList.add("show"));

        setTimeout(() => {
            popup.classList.remove("show");
            setTimeout(() => popup.classList.add("hidden"), 500);
        }, 3000);
    }

    // ---------------- Fetch Next Section ID ----------------
    async function fetchNextSectionId() {
        if (window.editMode) return; // Don't fetch in edit mode
        
        try {
            const response = await fetch('/extrusions/api/sections/?action=get_next_id');
            const data = await response.json();
            
            if (data.success && data.next_section_id) {
                if (sectionIdDisplay) {
                    sectionIdDisplay.value = data.next_section_id;
                }
            }
        } catch (error) {
            console.error('Error fetching next Section ID:', error);
        }
    }

    // ---------------- Set Today's Date ----------------
    function setTodayDate() {
        if (!window.editMode && dateField) {
            const today = new Date().toISOString().split('T')[0];
            dateField.value = today;
        }
    }

    // ---------------- Validate Form ----------------
    function validateForm() {
        const sectionNo = document.getElementById("section_no").value.trim();

        // Only Section No is required
        if (!sectionNo) {
            showMessage("error", "Section No is required");
            return false;
        }

        return true;
    }

    if (form) {
        form.addEventListener("submit", async function (e) {
            e.preventDefault();

            if (!validateForm()) return;

            const formData = new FormData(form);

            // Convert FormData to JSON for API
            let payload = {
                section_no: formData.get("section_no"),
                section_name: formData.get("section_name") || "",
                shape: formData.get("shape") || "",
                type: formData.get("type") || "",
                usage: formData.get("usage") || "",
                length_mm: formData.get("length_mm") || "0",
                width_mm: formData.get("width_mm") || "0",
                thickness_mm: formData.get("thickness_mm") || "0",
                ionized: formData.get("ionized") || "false"
            };

            // Note: Date is not included as it's auto-set on the server side

            // Debug: Log payload (without image)
            console.log("Payload being sent (without image):", payload);

            // Handle image file if present
            const imageFile = formData.get("section_image");
            if (imageFile && imageFile.size > 0) {
                // Convert image to base64 for JSON payload
                const reader = new FileReader();
                reader.onloadend = async function() {
                    payload.section_image_base64 = reader.result;
                    console.log("Image added to payload");
                    await submitForm(payload);
                };
                reader.readAsDataURL(imageFile);
            } else {
                await submitForm(payload);
            }
        });
    }

    async function submitForm(payload) {
        try {
            let url, method;
            if (window.editMode) {
                url = `/extrusions/api/sections/${window.sectionId}/`;
                method = "POST";
            } else {
                url = "/extrusions/api/sections/";
                method = "POST";
            }

            const response = await fetch(url, {
                method: method,
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]')?.value || ''
                },
                body: JSON.stringify(payload)
            });

            const responseText = await response.text();
            console.log("Response:", responseText); // Debug log
            
            const contentType = response.headers.get('content-type');

            if (!contentType || !contentType.includes('application/json')) {
                if (response.status === 404) {
                    showMessage("error", "API endpoint not found. Check your URL configuration.");
                } else if (response.status === 500) {
                    showMessage("error", "Server error. Please try again later.");
                    console.error("Server error response:", responseText);
                } else {
                    showMessage("error", "Server returned an unexpected response.");
                    console.error("Unexpected response:", responseText);
                }
                return;
            }

            let result;
            try {
                result = JSON.parse(responseText);
            } catch (jsonError) {
                showMessage("error", "Invalid response from server");
                console.error("JSON Parse Error:", jsonError);
                return;
            }

            if (result.success) {
                if (result.updated) {
                    showMessage("success", "Section updated successfully!");
                    // Redirect to list page after 1 second
                    setTimeout(() => window.location.href = '/extrusions/sections/', 1000);
                } else if (result.created) {
                    showMessage("success", `Section created successfully! Section ID: ${result.section.section_id}`);
                    // Redirect to list page after 1 second
                    setTimeout(() => window.location.href = '/extrusions/sections/', 1000);
                } else {
                    showMessage("success", "Section saved successfully!");
                    // Redirect to list page after 1 second
                    setTimeout(() => window.location.href = '/extrusions/sections/', 1000);
                }
            } else {
                showMessage("error", result.message || "Failed to save section");
                console.error("Server error:", result);
            }

        } catch (err) {
            console.error("Fetch error:", err);
            if (err.name === 'TypeError' && err.message.includes('fetch')) {
                showMessage("error", "Network error. Check if server is running.");
            } else {
                showMessage("error", "An error occurred. Please try again.");
            }
        }
    }

    // Initial load: Fetch next Section ID and set today's date if in create mode
    if (!window.editMode) {
        fetchNextSectionId();
        setTodayDate();
    }
});