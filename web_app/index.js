// Button sends a hard-coded simulator config to the server and displays the
// results as it runs
document.getElementById("button").addEventListener("click", () => {
  let ws = new WebSocket("ws://localhost:8000/run-simulator");

  ws.onopen = function(event) {
    config = {
      "ncompanies": 100,
      "employees": [
        [10],
        [1]
      ],
      "income": [
        [50000],
        [1]
      ],
      "periods": [
        {
          "ndays": 720,
          "rehire_rate": 1.0,
          "people_new_money": [
            [1],
            [1]
          ],
          "companies_new_money": [
            [1],
            [1]
          ],
          "spending": [
            [[0, 1]],
            [1]
          ],
          "industries": [
            ["economy"],
            [1]
          ]
        }
      ]
    };
    ws.send(JSON.stringify(config));
  };

  ws.onmessage = function(event) {
    msg = JSON.parse(event.data);
    document.getElementById("results").innerText = JSON.stringify(msg.results);
  };
});
