// ==================== DASHBOARD JAVASCRIPT ====================

// ▶ Auto color recovery %
document.querySelectorAll('.stat-item .stat-value').forEach(item => {
    let text = item.innerText.trim();

    // check if it ends with %
    if (text.endsWith("%")) {
        let num = parseFloat(text.replace("%", ""));

        if (num >= 80) {
            item.classList.add("recovery-good");
        } else {
            item.classList.add("recovery-bad");
        }
    }
});

// ▶ Auto color recovery percentage in side card
const recoveryPercentageEl = document.querySelector('.recovery-percentage');
if (recoveryPercentageEl) {
    let text = recoveryPercentageEl.innerText.trim();
    let num = parseFloat(text.replace("%", ""));

    if (num >= 80) {
        recoveryPercentageEl.classList.add("recovery-good");
    } else {
        recoveryPercentageEl.classList.add("recovery-bad");
    }
}

// ▶ Auto color ORDER summary (Orders / Completed / Pending / Cancelled)
document.querySelectorAll('.stat-card .stat-content .stat-item').forEach(item => {
    let label = item.querySelector('.stat-label')?.innerText.trim().toLowerCase();
    let valueSpan = item.querySelector('.stat-value');

    if (!label || !valueSpan) return;

    if (label === "orders") {
        valueSpan.classList.add("order-blue");
    }
    else if (label === "completed") {
        valueSpan.classList.add("order-green");
    }
    else if (label === "in progress") {
        valueSpan.classList.add("order-yellow");
    }
    else if (label === "cancelled") {
        valueSpan.classList.add("order-red");
    }
});

// ▶ Get current selected date from URL or use empty
function getSelectedDate() {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('date') || '';
}

// ▶ Load Recovery Table Data
async function loadRecoveryTableData() {
    const filter = window.currentFilter || 'today';
    const selectedDate = getSelectedDate();

    // Build URL with date parameter if it exists
    let url = `/dashboard/api/dashboard-recovery-table/?filter=${filter}`;
    if (selectedDate) {
        url += `&date=${selectedDate}`;
    }


    try {
        const response = await fetch(url);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        const tbody = document.getElementById('recoveryTableBody');

        if (data.success && data.reports && data.reports.length > 0) {
            tbody.innerHTML = '';

            data.reports.forEach((report, index) => {
                const row = document.createElement('tr');

                // Calculate recovery: (input / output) * 100
                let recovery = 0;
                if (report.total_output > 0) {
                    recovery = Math.round((report.input_qty / report.total_output) * 100);
                }

                row.innerHTML = `
                    <td>${report.die_no || '-'}</td>
                    <td>${report.no_of_cavity || '-'}</td>
                    <td>${report.press || '-'}</td>
                    <td>${report.input_qty || 0}kg</td>
                    <td>${report.total_output || 0}kg</td>
                    <td>${recovery}%</td>
                `;

                tbody.appendChild(row);
            });
        } else {
            tbody.innerHTML = '<tr><td colspan="6" class="text-center">No data available</td></tr>';
        }
    } catch (error) {
        document.getElementById('recoveryTableBody').innerHTML =
            `<tr><td colspan="6" class="text-center">Error: ${error.message}</td></tr>`;
    }
}

// ▶ Load Production Table Data
async function loadProductionTableData() {
    const filter = window.currentFilter || 'today';
    const selectedDate = getSelectedDate();

    // Build URL with date parameter if it exists
    let url = `/dashboard/api/dashboard-production-table/?filter=${filter}`;
    if (selectedDate) {
        url += `&date=${selectedDate}`;
    }

    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        const tbody = document.getElementById('productionTableBody');

        if (data.success && data.reports && data.reports.length > 0) {
            tbody.innerHTML = '';

            data.reports.forEach((report, index) => {
                const row = document.createElement('tr');

                // Determine status badge
                let statusBadge = '';
                if (report.status === 'completed') {
                    statusBadge = '<span class="status-badge completed">Completed</span>';
                } else if (report.status === 'in_progress') {
                    statusBadge = '<span class="status-badge in-progress">In Progress</span>';
                } else if (report.status === 'on_hold') {
                    statusBadge = '<span class="status-badge on-hold">On Hold</span>';
                } else if (report.status === 'cancelled') {
                    statusBadge = '<span class="status-badge cancelled">Cancelled</span>';
                } else {
                    statusBadge = '<span class="status-badge idle">-</span>';
                }

                row.innerHTML = `
                    <td>${report.die_no || '-'}</td>
                    <td>${report.cut_length || '-'}</td>
                    <td>${report.operator || '-'}</td>
                    <td>${statusBadge}</td>
                `;

                tbody.appendChild(row);
            });
        } else {
            tbody.innerHTML = '<tr><td colspan="4" class="text-center">No data available</td></tr>';
        }
    } catch (error) {
        document.getElementById('productionTableBody').innerHTML =
            `<tr><td colspan="4" class="text-center">Error: ${error.message}</td></tr>`;
    }
}

// ▶ Load Order Table Data
async function loadOrderTableData() {
    const filter = window.currentFilter || 'today';
    const selectedDate = getSelectedDate();

    // Build URL with date parameter if it exists
    let url = `/dashboard/api/dashboard-order-table/?filter=${filter}`;
    if (selectedDate) {
        url += `&date=${selectedDate}`;
    }


    try {
        const response = await fetch(url);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        const tbody = document.getElementById('orderTableBody');

        if (data.success && data.orders && data.orders.length > 0) {
            tbody.innerHTML = '';

            data.orders.forEach((order, index) => {
                const row = document.createElement('tr');

                // Map Requisition status to badges
                let statusBadge = '';
                if (order.status === 'completed') {
                    statusBadge = '<span class="status-badge completed">Completed</span>';
                } else if (order.status === 'in_production') {
                    statusBadge = '<span class="status-badge in-progress">In Production</span>';
                } else if (order.status === 'in_planning') {
                    statusBadge = '<span class="status-badge on-hold">In Planning</span>';
                } else if (order.status === 'rejected') {
                    statusBadge = '<span class="status-badge cancelled">Rejected</span>';
                } else if (order.status === 'created') {
                    statusBadge = '<span class="status-badge created">Created</span>';
                } else {
                    statusBadge = '<span class="status-badge idle">-</span>';
                }

                row.innerHTML = `
                    <td>${order.production_id || '-'}</td>
                    <td>${statusBadge}</td>
                `;

                tbody.appendChild(row);
            });
        } else {
            tbody.innerHTML = '<tr><td colspan="2" class="text-center">No data available</td></tr>';
        }
    } catch (error) {
        document.getElementById('orderTableBody').innerHTML =
            `<tr><td colspan="2" class="text-center">Error: ${error.message}</td></tr>`;
    }
}

// Load tables on page load
document.addEventListener('DOMContentLoaded', function () {
    loadRecoveryTableData();
    loadProductionTableData();
    loadOrderTableData();
});

// Filter functionality
function setFilter(filter) {
    // Redirect to same page with filter parameter (remove date parameter)
    window.location.href = `?filter=${filter}`;
}

let currentDate = new Date();
let selectedDate = new Date();

// Calendar Functions
function toggleCalendar() {
    const popup = document.getElementById('calendarPopup');
    popup.classList.toggle('active');

    if (popup.classList.contains('active')) {
        renderCalendar();
    }
}

// Close calendar when clicking outside
function closeCalendarOnOutsideClick(event) {
    if (event.target.id === 'calendarPopup') {
        toggleCalendar();
    }
}

// Change month
function changeMonth(delta) {
    currentDate.setMonth(currentDate.getMonth() + delta);
    renderCalendar();
}

// Render calendar
function renderCalendar() {
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();

    const monthNames = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ];
    document.getElementById('monthYear').textContent =
        `${monthNames[month]} ${year}`;

    const firstDay = new Date(year, month, 1).getDay();
    const daysInMonth = new Date(year, month + 1, 0).getDate();
    const daysInPrevMonth = new Date(year, month, 0).getDate();

    const container = document.getElementById('calendarDays');
    container.innerHTML = "";

    const today = new Date();

    // Previous month
    for (let i = firstDay - 1; i >= 0; i--) {
        let d = daysInPrevMonth - i;
        let div = document.createElement("div");
        div.className = "calendar-day other-month";
        div.textContent = d;
        container.appendChild(div);
    }

    // Current month
    for (let d = 1; d <= daysInMonth; d++) {
        let div = document.createElement("div");
        div.className = "calendar-day";
        div.textContent = d;

        if (
            d === today.getDate() &&
            year === today.getFullYear() &&
            month === today.getMonth()
        ) {
            div.classList.add("today");
        }

        div.onclick = () => selectDate(year, month, d);
        container.appendChild(div);
    }

    // Next month filler
    const cells = container.children.length;
    const remain = 42 - cells;

    for (let i = 1; i <= remain; i++) {
        let div = document.createElement("div");
        div.className = "calendar-day other-month";
        div.textContent = i;
        container.appendChild(div);
    }
}

// Select date
function selectDate(year, month, day) {
    selectedDate = new Date(year, month, day);

    // Format date as YYYY-MM-DD
    const formattedDate = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;

    // Redirect to dashboard with selected date parameter
    window.location.href = `?date=${formattedDate}`;
}

// ==================== LIVE PRESS WISE RECOVERY ====================

async function loadPressWiseRecovery() {
    const filter = window.currentFilter || 'today';
    const selectedDate = getSelectedDate();

    let url = `/dashboard/api/dashboard-recovery-table/?filter=${filter}`;
    if (selectedDate) url += `&date=${selectedDate}`;

    const res = await fetch(url);
    const data = await res.json();

    if (!data.success || !data.reports.length) return;

    const container = document.getElementById("pressWiseRecoveryContainer");
    container.innerHTML = "";

    // Group by press
    const pressMap = {};
    data.reports.forEach(r => {
        if (!r.press) return;

        if (!pressMap[r.press]) {
            pressMap[r.press] = { input: 0, output: 0 };
        }
        pressMap[r.press].input += r.input_qty || 0;
        pressMap[r.press].output += r.total_output || 0;
    });

    Object.entries(pressMap).forEach(([pressName, values], index) => {
        const recovery =
            values.output > 0
                ? Math.round((values.input / values.output) * 100)
                : 0;

        const canvasId = `pressChart_${index}`;

        const card = document.createElement("div");
        card.className = "plant-card";
        card.innerHTML = `
            <div class="plant-circle">
                <canvas id="${canvasId}"></canvas>
            </div>
            <div class="plant-name">${pressName}</div>
            <div class="plant-trend ${recovery >= 80 ? 'up' : 'down'}">
                ${recovery >= 80 ? '↑' : '↓'} ${recovery}%
            </div>
        `;

        container.appendChild(card);
        drawPressDonut(canvasId, recovery);
    });
}

function drawPressDonut(canvasId, targetValue) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    let currentValue = 0;

    const chart = new Chart(ctx, {
        type: "doughnut",
        data: {
            datasets: [{
                data: [0, 100],
                backgroundColor: [
                    targetValue >= 80 ? "#22c55e" : "#ef4444",
                    "#e5e7eb"
                ],
                borderWidth: 0
            }]
        },
        options: {
            cutout: "75%",
            animation: false, // ❗ we control animation manually
            plugins: {
                legend: { display: false },
                tooltip: { enabled: false },
                centerText: {
                    text: "0%"
                }
            }
        },
        plugins: [centerTextPlugin]
    });

    // 🔥 Smooth alive animation
    function animate() {
        if (currentValue >= targetValue) return;

        currentValue += 1; // speed controller (1 = slow, 2 = faster)

        chart.data.datasets[0].data = [
            currentValue,
            100 - currentValue
        ];

        chart.options.plugins.centerText.text = currentValue + "%";
        chart.update();

        requestAnimationFrame(animate);
    }

    requestAnimationFrame(animate);
}


// ==================== CENTER TEXT PLUGIN ====================
const centerTextPlugin = {
    id: "centerText",
    afterDraw(chart, args, options) {
        const { ctx, chartArea: { left, right, top, bottom } } = chart;

        const centerX = left + (right - left) / 2;
        const centerY = top + (bottom - top) / 2;

        ctx.save();
        ctx.font = "bold 18px Inter";
        ctx.fillStyle = "#1e293b";
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.fillText(options.text, centerX, centerY);
        ctx.restore();
    }
};


// Load with dashboard
document.addEventListener("DOMContentLoaded", loadPressWiseRecovery);


// ==================== RECOVERY BAR LOGIC (SAFE ADDITION) ====================

// Get recovery percent from API for a given filter/date
async function fetchRecoveryPercent(filter, date = null) {
    let url = `/dashboard/api/dashboard-recovery-table/?filter=${filter}`;
    if (date) url += `&date=${date}`;

    const res = await fetch(url);
    const data = await res.json();

    if (!data.success || !data.reports || data.reports.length === 0) {
        return 0;
    }

    let totalInput = 0;
    let totalOutput = 0;

    data.reports.forEach(r => {
        totalInput += r.input_qty || 0;
        totalOutput += r.total_output || 0;
    });

    return totalOutput > 0 ? Math.round((totalInput / totalOutput) * 100) : 0;
}

// ==================== ALIVE RECOVERY BAR ANIMATION ====================

// Animate bar from 0% → target %
function animateRecoveryBar(selector, targetPercent, duration = 2000) {
    const bar = document.querySelector(selector);
    if (!bar) return;

    let start = null;
    const target = Math.min(Math.max(targetPercent, 0), 100);

    // start from zero
    bar.style.height = "0%";

    function step(timestamp) {
        if (!start) start = timestamp;
        const progress = timestamp - start;

        const percent = Math.min((progress / duration) * target, target);
        bar.style.height = percent + "%";

        if (percent < target) {
            requestAnimationFrame(step);
        }
    }

    requestAnimationFrame(step);
}


// Load Today vs Yesterday bars
async function loadRecoveryBars() {
    try {
        const today = new Date();
        const yesterday = new Date();
        yesterday.setDate(today.getDate() - 1);

        const format = d =>
            `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;

        const todayRecovery = await fetchRecoveryPercent('today');
        const yesterdayRecovery = await fetchRecoveryPercent('today', format(yesterday));

        animateRecoveryBar('.recovery-bar-fill.today', todayRecovery);
        animateRecoveryBar('.recovery-bar-fill.yesterday', yesterdayRecovery);

        console.log('📊 Recovery Bars:', {
            today: todayRecovery + '%',
            yesterday: yesterdayRecovery + '%'
        });

    } catch (err) {
        console.error('❌ Recovery bar error:', err);
    }
}

// Run after page load
document.addEventListener('DOMContentLoaded', loadRecoveryBars);