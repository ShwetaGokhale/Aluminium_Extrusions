document.getElementById("filterForm").addEventListener("submit", function (e) {
    e.preventDefault();

    const formData = new FormData(this);

    fetch("{% url 'total_production_report' %}", {
        method: "POST",
        headers: { "X-CSRFToken": formData.get("csrfmiddlewaretoken") },
        body: formData
    })
        .then(res => res.json())
        .then(data => {
            const table = document.getElementById("reportTable");
            const tbody = table.querySelector("tbody");
            const summary = document.getElementById("summary");

            if (data.success && data.records.length > 0) {
                tbody.innerHTML = "";
                data.records.forEach(row => {
                    tbody.innerHTML += `
                    <tr>
                        <td>${row.s_no}</td>
                        <td>${row.date}</td>
                        <td>${row.time}</td>
                        <td>${row.press}</td>
                        <td>${row.die_no}</td>
                        <td>${row.order_no}</td>
                        <td>${row.length.toFixed(2)}</td>
                    </tr>
                `;
                });
                document.getElementById("totalRecords").innerText = data.total_records;
                document.getElementById("totalLength").innerText = data.total_length.toFixed(2);
                document.getElementById("totalFooter").innerText = data.total_length.toFixed(2);

                table.classList.remove("hidden");
                summary.classList.remove("hidden");
            } else {
                tbody.innerHTML = "<tr><td colspan='7'>No records found.</td></tr>";
                summary.classList.remove("hidden");
                document.getElementById("totalRecords").innerText = 0;
                document.getElementById("totalLength").innerText = "0.00";
                document.getElementById("totalFooter").innerText = "0.00";
            }
        });
});
