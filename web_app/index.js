/*
 * Scripts for the index page.
 */

$(document).ready(() => {
  //
  // Define the page components
  //

  // Creates a new jQuery element
  let element = function(name) {
    return $(document.createElement(name));
  }

  // An input for a number variable, given its type (integer or float),
  // display name and default value.
  class NumberInput {
    constructor(type, displayName, defaultValue) {
      this.value = defaultValue;
      this.element = null;

      let label = element("label")
        .text(displayName);

      let step;
      if (type == "integer") {
        step = "1";
      } else if (type == "float") {
        step = "0.01";
      } else {
        console.error("type '" + type + "' not supported");
      }
      let input = element("input")
        .addClass("form-control")
        .attr("type", "number")
        .attr("step", step)
        .attr("value", this.value.toString());
      input
        .on("input", () => {
          this.value = input[0].valueAsNumber;
        })
      
      this.element = element("div")
        .append(label)
        .append(input);
    }
  }

  // An input for one (value, probability) pair in a distribution, given
  // its name
  class DistributionInput {
    // type is one of {"integer", "float", "string", "range"}
    constructor(type, defaultValue, defaultProbability) {
      this.element = element("div");
      this.value = JSON.parse(JSON.stringify(defaultValue)); // copy defaultValue
      this.probability = defaultProbability;

      // Makes a single input element
      let input = (type, defaultValue, onInput) => {
        let e = element("input")
          .addClass("form-control")
          .attr("value", defaultValue.toString())
          .on("input", onInput);

        if (type == "integer") {
          e.attr("type", "number").attr("step", "1");
        } else if (type == "float") {
          e.attr("type", "number").attr("step", "0.01");
        } else if (type == "string") {
          e.attr("type", "text");
        } else {
          console.log("type '" + type + "' not supported");
        }

        return e;
      };

      let value;
      if (type == "range") {
        // Make 2 number inputs for the endpoints of the range
        value = element("div").addClass("row")
          .append(element("div").addClass("col")
            .append(input("float", this.value[0], (e) => {
              this.value[0] = e.currentTarget.valueAsNumber;
            }))
          ).append(element("div").addClass("col")
            .append(input("float", this.value[1], (e) => {
              this.value[1] = e.currentTarget.valueAsNumber;
            }))
          );
      } else if (type == "integer" || type == "float") {
        value = input(type, this.value, (e) => {
          this.value = e.currentTarget.valueAsNumber;
        });
      } else if (type == "string") {
        value = input(type, this.value, (e) => {
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

  // A container for all the inputs in a distribution
  class DistributionInputs {
    // type is one of the values accepted by DistributionInput
    constructor(type, displayName) {
      this.type = type;
      this.values = [];
      this.probabilities = [];
      this.inputs = []; // array of DistributionInput

      // Create the element
      let label = element("label")
        .text(displayName);

      let buttons = new AddRemoveButtons(
        // The "add" button adds a new DistributionInput
        () => {
          this.add();
        },

        // The "remove" button removes the last DistributionInput
        () => {
          this.remove();
        }
      );

      this.element = element("div").addClass("form-group")
        .append(label)
        .append(buttons.element);

      this.add();
    }

    add() {
      // Set default values based on the type
      let defaultValue;
      if (this.type == "integer" || this.type == "float") {
        defaultValue = 0;
      } else if (this.type == "string") {
        defaultValue = "";
      } else if (this.type == "range") {
        defaultValue = [0, 0];
      } else {
        console.error("type '" + this.type + "' not supported");
      }
      let defaultProbability = 0;

      let nextIndex = this.inputs.length;
      let input = new DistributionInput(this.type, defaultValue, defaultProbability);
      input.onInput(() => {
        this.values[nextIndex] = input.value;
        this.probabilities[nextIndex] = input.probability;
      });
      this.values.push(defaultValue);
      this.probabilities.push(defaultProbability);
      this.inputs.push(input);
      this.element.append(input.element);
    }

    remove() {
      let n = this.inputs.length;
      if (n != 0) {
        let last = this.inputs[n-1];
        this.inputs.pop();
        last.element.remove();
      }
    }
  }

  // A variable in the simulator config
  class Var {
    constructor(name, input) {
      this.name = name;
      this.input = input;
    }
  }

  // A container for the Vars of a single period
  class Period {
    // index = index of this period (for display)
    constructor(index) {
      this.ndays = new Var("ndays", new NumberInput("integer", "Number of days", 0));
      this.rehireRate = new Var("rehire_rate", new NumberInput("float", "Rehire rate", 0));
      this.peopleNewMoney = new Var("people_new_money", new DistributionInputs("integer", "Additional money for people"));
      this.companiesNewMoney = new Var("companies_new_money", new DistributionInputs("integer", "Additional money for companies"));
      this.spending = new Var("spending", new DistributionInputs("range", "Spending distribution"));
      this.industries = new Var("industries", new DistributionInputs("string", "Industry distribution"));

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
      this.ncompanies = new Var("ncompanies", new NumberInput("integer", "Number of companies", 0));
      this.employees = new Var("employees", new DistributionInputs("integer", "Employee distribution"));
      this.income = new Var("income", new DistributionInputs("integer", "Income distribution"));
      this.periods = new Periods();

      this.element = element("div")
        .append(this.ncompanies.input.element)
        .append(this.employees.input.element)
        .append(this.income.input.element)
        .append(this.periods.element);
    }
  }

  // The results chart
  // TODO: Implement the actual chart. For now, just some text
  class Chart {
    constructor() {
      this.element = element("span");
    }

    update(s) {
      this.element.text(s);
    }
  }

  // "Run" button sends a the config to the server and displays the results
  // as it runs
  class RunButton {
    constructor(configComponent, chart) {
      this.element = element("button")
        .addClass("btn")
        .addClass("btn-primary")
        .attr("type", "button")
        .text("Run")
        .on("click", () => {
          let ws = new WebSocket("ws://localhost:8000/run-simulator");

          ws.onopen = (e) => {
            // Build JSON object of the config
            let config = {
              ncompanies: configComponent.ncompanies.input.value,
              employees: [
                configComponent.employees.input.values,
                configComponent.employees.input.probabilities
              ],
              income: [
                configComponent.income.input.values,
                configComponent.income.input.probabilities
              ],
              periods: []
            };

            for (let i = 0; i < configComponent.periods.periods.length; i++) {
              let p = configComponent.periods.periods[i];
              config.periods.push({
                ndays: p.ndays.input.value,
                rehire_rate: p.rehireRate.input.value,
                people_new_money: [
                  p.peopleNewMoney.input.values,
                  p.peopleNewMoney.input.probabilities
                ],
                companies_new_money: [
                  p.companiesNewMoney.input.values,
                  p.companiesNewMoney.input.probabilities
                ],
                spending: [
                  p.spending.input.values,
                  p.spending.input.probabilities
                ],
                industries: [
                  p.industries.input.values,
                  p.industries.input.probabilities
                ]
              });
            }

            // Send config to the server
            ws.send(JSON.stringify(config));
          };

          ws.onmessage = (e) => {
            let msg = JSON.parse(e.data);
            chart.update(JSON.stringify(msg.results));
          };
        });
    }
  }

  //
  // Render the components
  //

  // Title
  const title = "Economy Simulator";
  $("title").text(title);
  $("#title").text(title);

  // Config
  let config = new Config();
  $("#config-container").append(config.element);

  // Chart
  let chart = new Chart();
  $("#chart-container").append(chart.element);

  // Run button
  $("#run-button-container").append((new RunButton(config, chart)).element);
});
