// Die details functionality
function showDieDetails(dieNo) {
    const modal = document.getElementById('dieDetailsModal');
    const modalDieName = document.getElementById('modalDieName');
    const tableBody = document.getElementById('dieDetailsTableBody');
    const loading = document.getElementById('dieDetailsLoading');
    const noData = document.getElementById('dieDetailsNoData');
    const content = document.getElementById('dieDetailsContent');

    // Show modal and reset states
    modal.classList.remove('hidden');
    modalDieName.textContent = `Die: ${dieNo}`;
    loading.classList.remove('hidden');
    noData.classList.add('hidden');
    content.classList.add('hidden');
    tableBody.innerHTML = '';

    // Fetch die details
    fetch(`/dashboard/die/${encodeURIComponent(dieNo)}/production/`)
        .then(response => response.json())
        .then(data => {
            loading.classList.add('hidden');

            if (data.success && data.production_data && data.production_data.length > 0) {
                content.classList.remove('hidden');
                displayDieProduction(data.production_data);
            } else {
                noData.classList.remove('hidden');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            loading.classList.add('hidden');
            noData.classList.remove('hidden');
        });
}

function displayDieProduction(productionData) {
    const tableBody = document.getElementById('dieDetailsTableBody');

    const statusBadges = {
        'planned': '<span class="px-3 py-1 rounded-full text-xs font-bold bg-blue-100 text-blue-800">Planned</span>',
        'running': '<span class="px-3 py-1 rounded-full text-xs font-bold bg-yellow-100 text-yellow-800">Running</span>',
        'completed': '<span class="px-3 py-1 rounded-full text-xs font-bold bg-green-100 text-green-800">Completed</span>',
        'discard': '<span class="px-3 py-1 rounded-full text-xs font-bold bg-red-100 text-red-800">Discard</span>'
    };

    tableBody.innerHTML = productionData.map((plan, index) => `
        <tr class="${index % 2 === 0 ? 'bg-white' : 'bg-gray-50'} hover:bg-blue-50 transition-colors">
            <td class="px-4 py-3 text-gray-700 font-medium">${plan.order_no}</td>
            <td class="px-4 py-3 text-blue-600 font-semibold">${plan.press_name}</td>
            <td class="px-4 py-3 text-center text-gray-700">${plan.cut_length}</td>
            <td class="px-4 py-3 text-center text-green-600 font-bold">${plan.planned_qty}</td>
            <td class="px-4 py-3 text-center">${statusBadges[plan.status] || statusBadges['planned']}</td>
        </tr>
    `).join('');
}

function closeDieDetails() {
    document.getElementById('dieDetailsModal').classList.add('hidden');
}

// Close modal on escape key
document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape') {
        closeDieDetails();
    }
});


// Dashboard animation on load
document.addEventListener("DOMContentLoaded", function () {
    const dashboard = document.querySelector(".dashboard-animate");
    if (dashboard) {
        setTimeout(() => {
            dashboard.classList.add("show");
        }, 100);
    }

    // Add die-card class to cards for animations
    const dieCards = document.querySelectorAll('.grid > div[onclick]');
    dieCards.forEach(card => {
        card.classList.add('die-card');
    });

    // Initialize production chart
    initializeProductionChart();
});

// Production Chart initialization
function initializeProductionChart() {
    const chartCanvas = document.getElementById('productionChart');
    if (!chartCanvas) return;

    const ctx = chartCanvas.getContext('2d');
    const productionChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['9 AM', '10 AM', '11 AM', '12 PM', '1 PM', '2 PM', '3 PM'],
            datasets: [{
                label: "Production Activity",
                data: [70, 75, 78, 76, 79, 80, 78],
                borderColor: 'rgba(99, 102, 241, 1)',
                backgroundColor: 'rgba(99, 102, 241, 0.1)',
                tension: 0.4,
                fill: true,
                pointRadius: 4,
                pointHoverRadius: 6,
                pointBackgroundColor: 'rgba(99, 102, 241, 1)',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: 'rgba(99, 102, 241, 1)',
                pointHoverBorderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        font: {
                            size: 12,
                            weight: 'bold'
                        },
                        color: '#374151',
                        padding: 15
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12,
                    titleFont: {
                        size: 14,
                        weight: 'bold'
                    },
                    bodyFont: {
                        size: 13
                    },
                    cornerRadius: 8,
                    displayColors: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        stepSize: 10,
                        font: {
                            size: 11
                        },
                        color: '#6b7280'
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)',
                        drawBorder: false
                    }
                },
                x: {
                    ticks: {
                        font: {
                            size: 11
                        },
                        color: '#6b7280'
                    },
                    grid: {
                        display: false,
                        drawBorder: false
                    }
                }
            },
            interaction: {
                intersect: false,
                mode: 'index'
            }
        }
    });
}

// Die details modal functionality
function showDieDetails(dieNo) {
    const modal = document.getElementById('dieDetailsModal');
    const modalDieName = document.getElementById('modalDieName');
    const tableBody = document.getElementById('dieDetailsTableBody');
    const loading = document.getElementById('dieDetailsLoading');
    const noData = document.getElementById('dieDetailsNoData');
    const content = document.getElementById('dieDetailsContent');

    if (!modal) {
        console.error('Modal element not found');
        return;
    }

    // Show modal and reset states
    modal.classList.remove('hidden');
    modalDieName.textContent = `Die: ${dieNo}`;
    loading.classList.remove('hidden');
    noData.classList.add('hidden');
    content.classList.add('hidden');
    tableBody.innerHTML = '';

    // Fetch die details
    fetch(`/dashboard/die/${encodeURIComponent(dieNo)}/production/`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            loading.classList.add('hidden');

            if (data.success && data.production_data && data.production_data.length > 0) {
                content.classList.remove('hidden');
                displayDieProduction(data.production_data);
            } else {
                noData.classList.remove('hidden');
            }
        })
        .catch(error => {
            console.error('Error fetching die details:', error);
            loading.classList.add('hidden');
            noData.classList.remove('hidden');

            // Show error message
            noData.innerHTML = `
                <div class="text-red-400 text-6xl mb-4">⚠️</div>
                <p class="text-gray-600 text-lg font-semibold">Error Loading Data</p>
                <p class="text-gray-500 text-sm mt-2">${error.message}</p>
            `;
        });
}

// Display production data in modal table
function displayDieProduction(productionData) {
    const tableBody = document.getElementById('dieDetailsTableBody');

    const statusBadges = {
        'planned': '<span class="px-3 py-1 rounded-full text-xs font-bold bg-blue-100 text-blue-800">📋 Planned</span>',
        'running': '<span class="px-3 py-1 rounded-full text-xs font-bold bg-yellow-100 text-yellow-800 animate-pulse">▶️ Running</span>',
        'completed': '<span class="px-3 py-1 rounded-full text-xs font-bold bg-green-100 text-green-800">✅ Completed</span>',
        'discard': '<span class="px-3 py-1 rounded-full text-xs font-bold bg-red-100 text-red-800">❌ Discard</span>'
    };

    tableBody.innerHTML = productionData.map((plan, index) => `
        <tr class="${index % 2 === 0 ? 'bg-white' : 'bg-gray-50'} hover:bg-blue-50 transition-colors duration-200" style="animation: fadeIn 0.3s ease ${index * 0.05}s both;">
            <td class="px-4 py-3 text-gray-700 font-medium">${escapeHtml(plan.order_no)}</td>
            <td class="px-4 py-3 text-blue-600 font-semibold">${escapeHtml(plan.press_name)}</td>
            <td class="px-4 py-3 text-center text-gray-700">${escapeHtml(plan.cut_length)}</td>
            <td class="px-4 py-3 text-center text-green-600 font-bold">${escapeHtml(plan.planned_qty)}</td>
            <td class="px-4 py-3 text-center">${statusBadges[plan.status] || statusBadges['planned']}</td>
        </tr>
    `).join('');
}

// Close die details modal
function closeDieDetails() {
    const modal = document.getElementById('dieDetailsModal');
    if (modal) {
        modal.classList.add('hidden');
    }
}

// Close modal on escape key
document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape') {
        closeDieDetails();
    }
});

// Close modal when clicking outside
document.getElementById('dieDetailsModal')?.addEventListener('click', function (event) {
    if (event.target === this) {
        closeDieDetails();
    }
});

// Utility function to escape HTML and prevent XSS
function escapeHtml(text) {
    if (text === null || text === undefined) return 'N/A';
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return String(text).replace(/[&<>"']/g, m => map[m]);
}

// Add smooth scroll behavior
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Auto-refresh data every 30 seconds (optional)
let autoRefreshInterval;

function startAutoRefresh() {
    autoRefreshInterval = setInterval(() => {
        // Reload the page to get fresh data
        location.reload();
    }, 30000); // 30 seconds
}

// Uncomment the line below to enable auto-refresh
// startAutoRefresh();

// Stop auto-refresh on page unload
window.addEventListener('beforeunload', () => {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
    }
});