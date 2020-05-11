/*
 * Scripts for the index page.
 */

$(document).ready(() => {
  //
  // Populate the page
  //

  // Title
  const title = "Economy Simulator";
  $("title").text(title);
  $("#title").text(title);

  // Make inputs
  let vars = [
    {name: "ncompanies", displayName: "Number of companies", type: "number"},
    {name: "employees", displayName: "Employee distribution", type: "distribution"}
    // TODO: the rest.
    // - Use this to make templates and render: https://jinja.palletsprojects.com/en/2.11.x/templates/
    // - Or use react... but templates may be simpler
  ];
  vars.forEach((v) => {
    let div = $("#" + v.name);
    // Set label text
    div.find("label").text(v.displayName);

    if (v.type == "distribution") {
      // Update slider label
      let defaultProb = "0";
      let label = div.find("span");
      label.text(defaultProb + "%");
      div.find(".probability-range")
        .attr("value", defaultProb)
        .on("input", (e) => {
          label.text(e.currentTarget.value + "%");
        });

      // Buttons add/remove an input to/from the group
      div.find(".add-button")
        .text("Add")
        .on("click", () => {
          let distributionInput = div.find(".distribution-input")[0];
          div.append(distributionInput.cloneNode(true));
        });

      div.find(".remove-button")
        .text("Remove")
        .on("click", () => {
          let distributionInput = div.find(".distribution-input");
          distributionInput[distributionInput.length - 1].remove();
        });
    }
  });

  // Chart
  // TODO

  //
  // Dynamic functionality
  //

  // "Run" button sends a hard-coded simulator config to the server and displays
  // the results as it runs
  $("#run")
  .text("Run")
  .on("click", () => {
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
});
