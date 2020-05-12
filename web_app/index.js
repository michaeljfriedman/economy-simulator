/*
 * Scripts for the index page.
 */

$(document).ready(() => {
  //
  // Define the page components
  //

  // Title
  const title = "Economy Simulator";
  $("title").text(title);
  $("#title").text(title);

  // Creates a new jQuery element
  let element = function(name) {
    return $(document.createElement(name));
  }

  // An input for a number variable, given its display name and default value.
  // Also allows you to add an onInput listener.
  class NumberInput {
    constructor(displayName, defaultValue) {
      this.value = defaultValue;
      this.element = null;

      let label = element("label")
        .text(displayName);
      let input = element("input")
        .addClass("form-control")
        .attr("type", "number")
        .attr("value", this.value.toString());
      input
        .on("input", () => {
          this.value = input[0].valueAsNumber;
        })
      
      this.element = element("div")
        .append(label)
        .append(input);
    }

    onInput(f) {
      this.element
        .find("input")
        .on("input", f);
    }
  }

  // An input for one (value, probability) pair in a distribution, given
  // its name
  class DistributionInput {
    constructor(name, defaultValue, defaultProbability) {
      this.element = element("div");
      this.value = defaultValue;
      this.probability = defaultProbability;

      let value = element("input")
        .addClass("form-control")
        .attr("value", this.value.toString())
        .on("input", (e) => {
          this.value = e.currentTarget.valueAsNumber; // track the value
        });
      if (name == "industries") {
        value = value.attr("type", "text");
      } else {
        value = value.attr("type", "number");
      }

      let probLabel = element("span")
        .text(this.probability.toString() + "%");
      let prob = element("input")
        .attr("type", "range")
        .attr("value", this.probability.toString())
        .on("input", (e) => {
          // Track the probability
          this.probability = e.currentTarget.valueAsNumber / 100;

          // Update the text label
          probLabel.text(e.currentTarget.value + "%");
        });;

      this.element 
        .append(element("div").addClass("row")
          .append(element("div").addClass("col")
            .append(value)
          ).append(element("div").addClass("col")
            .append(element("div").addClass("row")
              .append(prob)
            ).append(element("div").addClass("row")
              .append(probLabel)
            )
          )
        );
    }

    onInput(f) {
      this.element
        .find("input")
        .on("input", f);
    }
  }

  // An add/remove button pair for a distribution input. Specify what each
  // button should do on click.
  class DistributionButtons {
    constructor(onClickAdd, onClickRemove) {
      let addButton = element("button")
        .text("Add")
        .on("click", onClickAdd);

      let removeButton = element("button")
        .text("Remove")
        .on("click", onClickRemove);

      this.element =
        element("div").addClass("row")
          .append(element("div").addClass("col")
            .append(addButton)
            .append(removeButton)
          );
    }
  }

  // An input field, given its type, name, and display name. Tracks the value
  // of the input.
  class Input {
    constructor(type, name, displayName) {
      this.element = null;
      this.value = null;
      this.distributionInputs = []; // for type == "distribution" only, an array of DistributionInputs

      // Create the element
      this.element = element("div")
        .addClass("form-group");

      // Number input
      if (type == "number") {
        this.value = 0;
        let input = new NumberInput(displayName, this.value);
        input.onInput(() => {
          this.value = input.value;
        });
        this.element.append(input.element);

      // Distribution input
      } else if (type == "distribution") {
        let defaultValue = 0;
        let defaultProbability = 0;
        this.value = {
          values: [],
          probabilities: []
        };

        let label = element("label")
          .text(displayName);

        let addInput = () => {
          let nextIndex = this.distributionInputs.length;
          let input = new DistributionInput(name, defaultValue, defaultProbability);
          input.onInput(() => {
            this.value.values[nextIndex] = input.value;
            this.value.probabilities[nextIndex] = input.probability;
          });
          this.value.values.push(defaultValue);
          this.value.probabilities.push(defaultProbability);
          this.distributionInputs.push(input);
          return input;
        };

        let buttons = new DistributionButtons(
          // The "add" button adds a new DistributionInput
          () => {
            let input = addInput();
            this.element.append(input.element);
          },

          // The "remove" button removes the last DistributionInput
          () => {
            let n = this.distributionInputs.length;
            if (n != 0) {
              let last = this.distributionInputs[n-1];
              this.distributionInputs.pop();
              last.element.remove();
            }
          }
        );

        let input = addInput();

        this.element.append(label)
          .append(buttons.element)
          .append(input.element);
      } else {
        console.error("input type " + type + " not supported");
      }
    }
  }

  //
  // Render the components
  //

  // A variable in the simulator config
  class Var {
    constructor(name, displayName, type, input) {
      this.name = name;
      this.displayName = displayName;
      this.type = type;
      this.input = input;
    }
  }

  let vars = [
    new Var("ncompanies", "Number of companies", "number", null),
    new Var("employees", "Employee distribution", "distribution", null)
    // TODO: the rest
  ];

  for (let i = 0; i < vars.length; i++) {
    vars[i].input = new Input(vars[i].type, vars[i].name, vars[i].displayName);
    $("#config-container").append(vars[i].input.element);
  }

  // Chart
  // TODO

  //
  // Implement the "run" button
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
