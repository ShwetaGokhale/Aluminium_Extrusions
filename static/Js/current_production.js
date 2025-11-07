// Timestamp update logic
function updateTimestamp() {
    const now = new Date();
    const formatted = now.toLocaleString('en-IN', {
        day: '2-digit', month: 'short', year: 'numeric',
        hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false
    });
    document.getElementById('lastUpdated').textContent = formatted;
}
updateTimestamp();
setInterval(updateTimestamp, 1000);

// Fullscreen handling
let userClicked = false;
function openFullscreen() {
    const elem = document.documentElement;
    if (elem.requestFullscreen) elem.requestFullscreen();
    else if (elem.webkitRequestFullscreen) elem.webkitRequestFullscreen();
    else if (elem.msRequestFullscreen) elem.msRequestFullscreen();
}
document.body.addEventListener("click", function () {
    userClicked = true;
    if (!document.fullscreenElement) {
        openFullscreen();
    }
});

// ✅ View sensor details (modified from viewOrderDetails)
function viewOrderDetails(sensorName) {
    if (!sensorName) {
        alert('Sensor name not found');
        return;
    }

    const filterContainer = document.getElementById('filterCardsContainer');
    const detailView = document.getElementById('orderDetailView');

    filterContainer.classList.add('hidden');
    detailView.classList.remove('hidden');

    document.getElementById('detailOrderNo').textContent = sensorName;
    document.getElementById('detailLoadingState').classList.remove('hidden');
    document.getElementById('detailNoDataState').classList.add('hidden');
    document.getElementById('detailTableBody').innerHTML = '';

    // Fetch order details based on sensor name
    let url = '/current_production/sensor-details/?sensor_name=' + encodeURIComponent(sensorName);

    fetch(url)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayOrderDetails(data.order_details);
            } else {
                throw new Error(data.message || 'Error loading data');
            }
        })
        .catch(error => {
            alert('Failed to load order details: ' + error.message);
            closeOrderDetail();
        });
}

// Display order details in table
function displayOrderDetails(orderDetails) {
    document.getElementById('detailLoadingState').classList.add('hidden');
    const tableBody = document.getElementById('detailTableBody');
    const noDataState = document.getElementById('detailNoDataState');

    if (!orderDetails || orderDetails.length === 0) {
        noDataState.classList.remove('hidden');
        return;
    }

    tableBody.innerHTML = orderDetails.map((detail, index) => `
        <tr class="${index % 2 === 0 ? 'bg-gray-800' : 'bg-gray-900'} hover:bg-gray-700 transition-colors duration-150 fade-in">
            <td class="px-8 py-5 text-gray-300 text-lg font-medium">${detail.order_no}</td>
            <td class="px-8 py-5 text-blue-400 text-lg font-semibold">${detail.die_name}</td>
            <td class="px-8 py-5 text-yellow-400 text-lg font-medium text-center">${detail.date}</td>
            <td class="px-8 py-5 text-green-400 text-lg font-bold text-center">${detail.time}</td>
            <td class="px-8 py-5 text-teal-400 text-lg font-bold text-center">${detail.press}</td>
            <td class="px-8 py-5 text-purple-400 text-xl font-bold text-center">${detail.length}</td>
        </tr>`).join('');
}

// Close detail view
function closeOrderDetail() {
    document.getElementById('orderDetailView').classList.add('hidden');
    document.getElementById('filterCardsContainer').classList.remove('hidden');
}

// ✅ Instant Profile Count Logic (updated to sensor cards)
async function updateProfileCounts() {
    const cards = document.querySelectorAll("[data-sensor]");
    for (let card of cards) {
        const sensorName = card.getAttribute("data-sensor");
        const countEl = card.querySelector(".profileCountValue");
        if (!sensorName || !countEl) continue;
        try {
            const res = await fetch(`/current_production/sensor-details/?sensor_name=${encodeURIComponent(sensorName)}`);
            const data = await res.json();
            if (data.success && data.order_details) {
                countEl.textContent = data.order_details.length;
            } else {
                countEl.textContent = "0";
            }
        } catch (e) {
            countEl.textContent = "Err";
        }
    }
}

// Auto-update counts every 10 seconds
updateProfileCounts();
setInterval(updateProfileCounts, 10000);
