// Set current date
document.getElementById('reportDate').textContent = new Date().toLocaleDateString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
});

// Set default date in filter if not set
const dateInput = document.getElementById('reportDateFilter');
if (!dateInput.value) {
    dateInput.valueAsDate = new Date();
}

// Calculate Recovery percentage and NRT after page loads
document.addEventListener('DOMContentLoaded', function () {
    // Calculate Recovery for each row
    const recoveryFields = document.querySelectorAll('td.calculated-field[data-output]');
    recoveryFields.forEach(function (cell) {
        const output = parseFloat(cell.getAttribute('data-output'));
        const input = parseFloat(cell.getAttribute('data-input'));

        if (input && output && input !== 0) {
            const recovery = ((output / input) * 100).toFixed(2);
            cell.textContent = recovery + '%';
        } else {
            cell.textContent = 'N/A';
        }
    });

    // Calculate NRT for each row
    const nrtFields = document.querySelectorAll('td.calculated-field[data-start]');
    nrtFields.forEach(function (cell) {
        const startTime = cell.getAttribute('data-start');
        const endTime = cell.getAttribute('data-end');

        if (startTime && endTime && startTime !== 'None' && endTime !== 'None') {
            const [startHour, startMin] = startTime.split(':').map(Number);
            const [endHour, endMin] = endTime.split(':').map(Number);

            let hours = endHour - startHour;
            let minutes = endMin - startMin;

            if (minutes < 0) {
                hours -= 1;
                minutes += 60;
            }

            //Show hours
            cell.textContent = hours + ' hrs';
        } else {
            cell.textContent = 'N/A';
        }
    });
});