// Print functionality
function printReport() {
    window.print();
}

// PDF generation functionality using jsPDF
function generatePDF() {
    // Check if jsPDF is loaded
    if (typeof window.jspdf === 'undefined') {
        alert('PDF library not loaded. Please refresh the page.');
        return;
    }

    const { jsPDF } = window.jspdf;
    const doc = new jsPDF('landscape', 'mm', 'a4');

    // Get report title and date
    const pageHeader = document.querySelector('.page-header h1').textContent;
    const reportDate = document.getElementById('reportDate').textContent;

    // Add title
    doc.setFontSize(18);
    doc.setTextColor(30, 58, 138); // #1e3a8a
    doc.text(pageHeader, doc.internal.pageSize.getWidth() / 2, 15, { align: 'center' });

    // Add date
    doc.setFontSize(10);
    doc.setTextColor(100, 116, 139); // #64748b
    doc.text(reportDate, doc.internal.pageSize.getWidth() / 2, 22, { align: 'center' });

    // Collect table data
    const tableData = [];
    const rows = document.querySelectorAll('#reportTableBody tr');

    rows.forEach((row) => {
        const cells = row.querySelectorAll('td');
        if (cells.length > 0 && !row.querySelector('.no-data')) {
            const rowData = [];
            cells.forEach((cell) => {
                rowData.push(cell.textContent.trim());
            });
            tableData.push(rowData);
        }
    });

    // Table headers
    const headers = [
        'S.No', 'Die No', 'Section No', 'Section Name', 'Cavity',
        'Start Time', 'End Time', 'Billet Size', 'No of Billet',
        'Input', 'Cut Length', 'WT per Piece', 'No of OK PCS',
        'Output', 'Recovery %', 'NOP BP', 'NOP BA', 'NRT (hrs)'
    ];

    // Generate table using autoTable
    doc.autoTable({
        head: [headers],
        body: tableData,
        startY: 28,
        styles: {
            fontSize: 7,
            cellPadding: 2,
        },
        headStyles: {
            fillColor: [243, 244, 246],
            textColor: [55, 65, 81],
            fontStyle: 'bold',
            halign: 'center',
        },
        columnStyles: {
            0: { halign: 'center', cellWidth: 10 }, // S.No
            4: { halign: 'center' }, // Cavity
            5: { halign: 'center' }, // Start Time
            6: { halign: 'center' }, // End Time
            8: { halign: 'center' }, // No of Billet
            9: { halign: 'right' }, // Input
            10: { halign: 'center' }, // Cut Length
            11: { halign: 'right' }, // WT per Piece
            12: { halign: 'center' }, // No of OK PCS
            13: { halign: 'right' }, // Output
            14: { halign: 'right', fillColor: [254, 243, 199] }, // Recovery % (highlighted)
            15: { halign: 'center' }, // NOP BP
            16: { halign: 'center' }, // NOP BA
            17: { halign: 'center', fillColor: [254, 243, 199] }, // NRT (highlighted)
        },
        alternateRowStyles: {
            fillColor: [249, 250, 251],
        },
        margin: { top: 28, left: 10, right: 10 },
    });

    // Generate filename with current date
    const today = new Date();
    const filename = `Daily_Production_Report_${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}.pdf`;

    // Save the PDF
    doc.save(filename);
}

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