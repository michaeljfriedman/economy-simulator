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
    constructor(type, defaultValue, defaultProbability) {
      this.element = element("div");
      this.value = JSON.parse(JSON.stringify(defaultValue)); // copy defaultValue
      this.probability = defaultProbability;

      // Makes a single input element
      let input = (type, defaultValue, onInput) => {
        return element("input")
          .addClass("form-control")
          .attr("value", defaultValue.toString())
          .attr("type", type)
          .on("input", onInput);
      };

      let value;
      if (type == "range") {
        // Make 2 number inputs for the endpoints of the range
        value = element("div").addClass("row")
          .append(element("div").addClass("col")
            .append(input("number", this.value[0], (e) => {
              this.value[0] = e.currentTarget.valueAsNumber;
            }))
          ).append(element("div").addClass("col")
            .append(input("number", this.value[1], (e) => {
              this.value[1] = e.currentTarget.valueAsNumber;
            }))
          );
      } else if (type == "number") {
        value = input("number", this.value, (e) => {
          this.value = e.currentTarget.valueAsNumber;
        });
      } else if (type == "text") {
        value = input("text", this.value, (e) => {
          this.value = e.currentTarget.value;
        });
      } else {
        console.error("type '" + type + "' not supported");
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

  // An add/remove button pair for an input. Specify what each button should do
  // on click.
  class AddRemoveButtons {
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
    constructor(type, displayName) {
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
      } else if (type.startsWith("distribution")) {
        let subtype = type.substring(type.indexOf("-") + 1);
        let defaultValue;
        if (subtype == "number") {
          defaultValue = 0;
        } else if (subtype == "text") {
          defaultValue = "";
        } else if (subtype == "range") {
          defaultValue = [0, 0];
        } else {
          console.error("subtype '" + subtype + "' not supported");
        }
        let defaultProbability = 0;
        this.value = {
          values: [],
          probabilities: []
        };

        let label = element("label")
          .text(displayName);

        let addInput = () => {
          let nextIndex = this.distributionInputs.length;
          let input = new DistributionInput(subtype, defaultValue, defaultProbability);
          input.onInput(() => {
            this.value.values[nextIndex] = input.value;
            this.value.probabilities[nextIndex] = input.probability;
          });
          this.value.values.push(defaultValue);
          this.value.probabilities.push(defaultProbability);
          this.distributionInputs.push(input);
          return input;
        };

        let buttons = new AddRemoveButtons(
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

  // A variable in the simulator config
  class Var {
    constructor(name, displayName, type, input) {
      this.name = name;
      this.displayName = displayName;
      this.type = type;
      this.input = input;
    }
  }

  // A container for the Vars of a single period
  class Period {
    // index = index of this period (for display)
    constructor(index) {
      this.ndays = new Var("ndays", "Number of days", "number", null);
      this.rehireRate = new Var("rehire_rate", "Rehire rate", "number", null);
      this.peopleNewMoney = new Var("people_new_money", "Additional money for people", "distribution-number", null);
      this.companiesNewMoney = new Var("companies_new_money", "Additional money for companies", "distribution-number", null);
      this.spending = new Var("spending", "Spending distribution", "distribution-range", null);
      this.industries = new Var("industries", "Industry distribution", "distribution-text", null);

      let vars = [
        this.ndays,
        this.rehireRate,
        this.peopleNewMoney,
        this.companiesNewMoney,
        this.spending,
        this.industries
      ];

      for (let i = 0; i < vars.length; i++) {
        vars[i].input = new Input(vars[i].type, vars[i].displayName);
      }

      this.element = element("div")
        .append(element("label").text("Period " + index))
        .append(this.ndays.input.element)
        .append(this.rehireRate.input.element)
        .append(this.peopleNewMoney.input.element)
        .append(this.companiesNewMoney.input.element)
        .append(this.spending.input.element)
        .append(this.industries.input.element);
    }
  }

  // A container for all periods
  class Periods {
    constructor() {
      let buttons = new AddRemoveButtons(
        // The "add" button adds a new period
        () => {
          this.add();
        },

        // The "remove" button removes a period
        () => {
          this.remove();
        }
      );
      this.element = element("div")
        .addClass("form-group")
        .append(element("label").text("Periods"))
        .append(buttons.element);

      this.periods = [];
      this.add();
    }

    add() {
      let p = new Period(this.periods.length + 1);
      this.periods.push(p);
      this.element.append(p.element);
    }

    remove() {
      if (this.periods.length != 0) {
        let last = this.periods[this.periods.length - 1];
        this.periods.pop();
        last.element.remove();
      }
    }
  }

  // A container for the entire config
  class Config {
    constructor() {
      this.ncompanies = new Var("ncompanies", "Number of companies", "number", null);
      this.employees = new Var("employees", "Employee distribution", "distribution-number", null);
      this.income = new Var("income", "Income distribution", "distribution-number", null);
      this.periods = new Periods();

      let vars = [
        this.ncompanies,
        this.employees,
        this.income
      ];

      for (let i = 0; i < vars.length; i++) {
        vars[i].input = new Input(vars[i].type, vars[i].displayName);
      }

      this.element = element("div")
        .append(this.ncompanies.input.element)
        .append(this.employees.input.element)
        .append(this.income.input.element)
        .append(this.periods.element);
    }
  }

  //
  // Render the components
  //

  let config = new Config();
  $("#config-container").append(config.element);

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
