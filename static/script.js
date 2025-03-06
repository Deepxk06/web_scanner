document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("scanForm").addEventListener("submit", async function (event) {
        event.preventDefault();
        let url = document.getElementById("url").value;

        let response = await fetch("/scan", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ url })
        });

        let data = await response.json();
        document.getElementById("result").innerText = JSON.stringify(data, null, 2);
    });
});
