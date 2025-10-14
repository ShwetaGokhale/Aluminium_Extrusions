document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("sectionForm");
    const sectionIdDisplay = document.getElementById("section_id_display");
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

    // ---------------- Validate Form ----------------
    function validateForm() {
        const date = document.getElementById("date").value;
        const sectionNo = document.getElementById("section_no").value.trim();
        const sectionName = document.getElementById("section_name").value.trim();
        const shape = document.getElementById("shape").value.trim();
        const type = document.getElementById("type").value.trim();
        const usage = document.getElementById("usage").value.trim();
        const lengthMm = document.getElementById("length_mm").value.trim();
        const widthMm = document.getElementById("width_mm").value.trim();
        const thicknessMm = document.getElementById("thickness_mm").value.trim();
        const ionized = document.querySelector('input[name="ionized"]:checked');

        if (!date) {
            showMessage("error", "Date is required");
            return false;
        }

        if (!sectionNo) {
            showMessage("error", "Section No is required");
            return false;
        }

        if (!sectionName) {
            showMessage("error", "Section Name is required");
            return false;
        }

        if (!shape) {
            showMessage("error", "Shape is required");
            return false;
        }

        if (!type) {
            showMessage("error", "Type is required");
            return false;
        }

        if (!usage) {
            showMessage("error", "Usage is required");
            return false;
        }

        if (!lengthMm || parseFloat(lengthMm) <= 0) {
            showMessage("error", "Valid Length in mm is required (must be greater than 0)");
            return false;
        }

        if (!widthMm || parseFloat(widthMm) <= 0) {
            showMessage("error", "Valid Width in mm is required (must be greater than 0)");
            return false;
        }

        if (!thicknessMm || parseFloat(thicknessMm) <= 0) {
            showMessage("error", "Valid Thickness in mm is required (must be greater than 0)");
            return false;
        }

        if (!ionized) {
            showMessage("error", "Please select Ionized option (Yes/No)");
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
                date: formData.get("date"),
                section_no: formData.get("section_no"),
                section_name: formData.get("section_name"),
                shape: formData.get("shape"),
                type: formData.get("type"),
                usage: formData.get("usage"),
                length_mm: formData.get("length_mm"),
                width_mm: formData.get("width_mm"),
                thickness_mm: formData.get("thickness_mm"),
                ionized: formData.get("ionized")
            };

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

    // Initial load: Fetch next Section ID if in create mode
    if (!window.editMode) {
        fetchNextSectionId();
    }
});