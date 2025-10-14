document.addEventListener("DOMContentLoaded", function () {
    const dashboard = document.querySelector(".dashboard-animate");
    if (dashboard) {
        setTimeout(() => {
            dashboard.classList.add("show");
        }, 100); // delay for smoother effect
    }
});


const ctx = document.getElementById('productionChart').getContext('2d');
const productionChart = new Chart(ctx, {
    type: 'line', // you can change to 'bar' if you want
    data: {
        labels: ['9 AM', '10 AM', '11 AM', '12 PM', '1 PM', '2 PM', '3 PM'],
        datasets: [{
            label: "Profile Length (ft)",
            data: [70, 75, 78, 76, 79, 80, 78],
            borderColor: 'rgba(59, 130, 246, 1)',
            backgroundColor: 'rgba(59, 130, 246, 0.2)',
            tension: 0.3,
            fill: true,
            pointRadius: 3,
            pointHoverRadius: 5,
        }]
    },
    options: {
        responsive: true,
        plugins: {
            legend: {
                display: true,
                position: 'top',
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                max: 100,
                ticks: {
                    stepSize: 10
                }
            }
        }
    }
});