document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("dieForm");
    const dieIdDisplay = document.getElementById("die_id_display");

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

    // ---------------- Fetch Next Die ID ----------------
    async function fetchNextDieId() {
        if (window.editMode) return; // Don't fetch in edit mode

        try {
            const response = await fetch('/extrusions/api/dies/?action=get_next_id');
            const data = await response.json();

            if (data.success && data.next_die_id) {
                if (dieIdDisplay) {
                    dieIdDisplay.value = data.next_die_id;
                }
            }
        } catch (error) {
            console.error('Error fetching next Die ID:', error);
        }
    }

    // ---------------- Validate Form ----------------
    function validateForm() {
        const date = document.getElementById("date").value;
        const dieNo = document.getElementById("die_no").value.trim();
        const dieName = document.getElementById("die_name").value.trim();
        const noOfCavity = document.getElementById("no_of_cavity").value;
        const reqWeight = document.getElementById("req_weight").value;
        const size = document.getElementById("size").value.trim();
        const dieMaterial = document.getElementById("die_material").value;
        const hardness = document.getElementById("hardness").value.trim();
        const type = document.getElementById("type").value;

        if (!date) {
            showMessage("error", "Date is required");
            return false;
        }

        if (!dieNo) {
            showMessage("error", "Die No is required");
            return false;
        }

        // Check for placeholder or invalid values
        if (dieNo.toLowerCase().includes('die -') || dieNo.trim() === '' || dieNo.length < 2) {
            showMessage("error", "Please enter a valid Die No (minimum 2 characters)");
            return false;
        }

        if (!dieName) {
            showMessage("error", "Die Name is required");
            return false;
        }

        if (!noOfCavity) {
            showMessage("error", "No of Cavity is required");
            return false;
        }

        if (!reqWeight || parseFloat(reqWeight) <= 0) {
            showMessage("error", "Valid Req Weight is required (must be greater than 0)");
            return false;
        }

        if (!size) {
            showMessage("error", "Size is required");
            return false;
        }

        if (!dieMaterial) {
            showMessage("error", "Die Material is required");
            return false;
        }

        if (!hardness) {
            showMessage("error", "Hardness is required");
            return false;
        }

        if (!type) {
            showMessage("error", "Type is required");
            return false;
        }

        return true;
    }

    if (form) {
        form.addEventListener("submit", async function (e) {
            e.preventDefault();

            if (!validateForm()) return;

            const formData = new FormData(form);

            // Debug: Log form data
            console.log("Form Data being sent:");
            for (let [key, value] of formData.entries()) {
                console.log(key, ":", value);
            }

            try {
                let url, method;
                if (window.editMode) {
                    url = `/extrusions/api/dies/${window.dieId}/`;
                    method = "POST";
                } else {
                    url = "/extrusions/api/dies/";
                    method = "POST";
                }

                const response = await fetch(url, {
                    method: method,
                    headers: {
                        "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]')?.value || ''
                    },
                    body: formData
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
                    } else if (responseText.includes('csrfmiddlewaretoken')) {
                        showMessage("error", "CSRF token error. Please refresh the page.");
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
                        showMessage("success", "Die updated successfully!");
                        // Redirect to list page after 1 second
                        setTimeout(() => window.location.href = '/extrusions/dies/', 1000);
                    } else if (result.created) {
                        showMessage("success", `Die created successfully! Die ID: ${result.die.die_id}`);
                        // Redirect to list page after 1 second
                        setTimeout(() => window.location.href = '/extrusions/dies/', 1000);
                    } else {
                        showMessage("success", "Die saved successfully!");
                        // Redirect to list page after 1 second
                        setTimeout(() => window.location.href = '/extrusions/dies/', 1000);
                    }
                } else {
                    // Display the actual error message from server
                    showMessage("error", result.message || "Failed to save");
                    console.error("Server error:", result);
                }

            } catch (err) {
                if (err.name === 'TypeError' && err.message.includes('fetch')) {
                    showMessage("error", "Network error. Check if server is running.");
                } else {
                    showMessage("error", "Request failed: " + err.message);
                }
                console.error("Fetch error:", err);
            }
        });
    }

    // Preview image on file select
    const imageInput = document.getElementById('image');
    if (imageInput) {
        imageInput.addEventListener('change', function (e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function (event) {
                    let preview = document.querySelector('.image-preview');
                    if (!preview) {
                        preview = document.createElement('div');
                        preview.className = 'image-preview mt-2';
                        imageInput.parentNode.appendChild(preview);
                    }
                    preview.innerHTML = `<img src="${event.target.result}" alt="Preview" style="max-width: 150px; border-radius: 8px;">`;
                };
                reader.readAsDataURL(file);
            }
        });
    }

    // Initial load: Fetch next Die ID if in create mode
    if (!window.editMode) {
        fetchNextDieId();
    }
});