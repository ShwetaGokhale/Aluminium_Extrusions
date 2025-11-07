// Timestamp update logic
function updateTimestamp() {
    const now = new Date();
    const formatted = now.toLocaleString('en-IN', {
        day: '2-digit',
        month: 'short',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
    });
    document.getElementById('lastUpdated').textContent = formatted;
}
updateTimestamp();
setInterval(updateTimestamp, 1000);

// Fullscreen handling
let userClicked = false;

// Request fullscreen mode on user interaction 
function openFullscreen() {
    const elem = document.documentElement;
    if (elem.requestFullscreen) elem.requestFullscreen();
    else if (elem.webkitRequestFullscreen) elem.webkitRequestFullscreen();
    else if (elem.msRequestFullscreen) elem.msRequestFullscreen();
}

// Listen for any click on the body to enter fullscreen
document.body.addEventListener("click", function () {
    userClicked = true;
    if (!document.fullscreenElement) {
        openFullscreen();
    }
});

document.addEventListener("fullscreenchange", function () {
    // When user presses ESC, fullscreen exits.
    // When they click again, fullscreen reactivates (handled above)
});

// Helper function to get status badge styling
function getStatusBadge(status) {
    const statusConfig = {
        'in_progress': {
            bg: 'bg-yellow-500',
            text: 'text-white',
            icon: 'fa-play-circle',
            label: 'In Progress',
            pulse: true
        },
        'completed': {
            bg: 'bg-green-500',
            text: 'text-white',
            icon: 'fa-check-circle',
            label: 'Completed'
        },
        'on_hold': {
            bg: 'bg-blue-500',
            text: 'text-white',
            icon: 'fa-pause-circle',
            label: 'On Hold'
        },
        'cancelled': {
            bg: 'bg-red-500',
            text: 'text-white',
            icon: 'fa-times-circle',
            label: 'Cancelled'
        }
    };

    const config = statusConfig[status] || statusConfig['in_progress'];
    const pulseClass = config.pulse ? 'animate-pulse' : '';

    return `
        <span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-bold ${config.bg} ${config.text} ${pulseClass}">
            <i class="fa ${config.icon} mr-2"></i>${config.label}
        </span>
    `;
}


// Press detail logic
function showPressDetail(pressId, pressName) {
    const cardsContainer = document.getElementById('pressCardsContainer');
    const detailView = document.getElementById('pressDetailView');
    cardsContainer.classList.add('hidden');
    detailView.classList.remove('hidden');
    document.getElementById('detailPressName').textContent = pressName;
    document.getElementById('detailPressTitle').textContent = 'Production Monitoring';
    document.getElementById('detailLoadingState').classList.remove('hidden');
    document.getElementById('detailNoDataState').classList.add('hidden');
    document.getElementById('detailTableBody').innerHTML = '';

    fetch(`/dashboard_new/press/${pressId}/production/`)
        .then(response => response.json())
        .then(data => {
            if (data.success) displayDetailedProduction(data.production_data);
            else throw new Error(data.message || 'Error');
        })
        .catch(error => {
            alert('Failed to load production data: ' + error.message);
            closePressDetail();
        });
}

function displayDetailedProduction(productionData) {
    document.getElementById('detailLoadingState').classList.add('hidden');
    const tableBody = document.getElementById('detailTableBody');
    const noDataState = document.getElementById('detailNoDataState');

    if (!productionData || productionData.length === 0) {
        noDataState.classList.remove('hidden');
        return;
    }

    tableBody.innerHTML = productionData.map((plan, index) => `
        <tr class="${index % 2 === 0 ? 'bg-gray-800' : 'bg-gray-900'} hover:bg-gray-700 transition-colors duration-150 fade-in">
            <td class="px-8 py-5 text-gray-300 text-lg font-medium">${plan.order_no}</td>
            <td class="px-8 py-5 text-blue-400 text-lg font-semibold">${plan.die_no}</td>
            <td class="px-8 py-5 text-yellow-400 text-lg font-medium text-center">${plan.cut_length}</td>
            <td class="px-8 py-5 text-green-400 text-xl font-bold text-center">${plan.planned_qty}</td>
            <td class="px-8 py-5 text-teal-400 text-xl font-bold text-center">-</td>
            <td class="px-8 py-5 text-purple-400 text-xl font-bold text-center">-</td>
            <td class="px-8 py-5 text-center">${getStatusBadge(plan.status)}</td>
        </tr>
    `).join('');
}

function closePressDetail() {
    document.getElementById('pressDetailView').classList.add('hidden');
    document.getElementById('pressCardsContainer').classList.remove('hidden');
}