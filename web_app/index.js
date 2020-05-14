/*
 * Scripts for the index page.
 */

$(document).ready(() => {
  //
  // Define the page components
  //

  const urlParams = {
    config: "config"
  };

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

    // Sets the value
    set(v) {
      if (v == null || v == undefined) {
        return false;
      }

      this.value = v;
      this.element.find("input")[0].value = v;
      return true;
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
      this.type = type;

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
          console.error("type '" + type + "' not supported");
        }

        return e;
      };

      let value;
      if (this.type == "range") {
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
      } else if (this.type == "integer" || this.type == "float") {
        value = input(this.type, this.value, (e) => {
          this.value = e.currentTarget.valueAsNumber;
        });
      } else if (this.type == "string") {
        value = input(this.type, this.value, (e) => {
          this.value = e.currentTarget.value;
        });
      } else {
        console.error("type '" + this.type + "' not supported");
      }

      let probLabel = element("span")
        .text(this.probStr(100 * this.probability));
      let prob = element("input")
        .addClass("form-control-range")
        .attr("type", "range")
        .attr("value", this.probability.toString())
        .on("input", (e) => {
          // Track the probability
          this.probability = e.currentTarget.valueAsNumber / 100;

          // Update the text label
          probLabel.text(this.probStr(e.currentTarget.value));
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

    // Returns the probability string, given the value out of 100
    probStr(v) {
      return v.toString() + "%";
    }

    // Sets the value
    set(value, probability) {
      if (value == null || value == undefined || probability == null || probability == undefined) {
        return false;
      }

      this.value = JSON.parse(JSON.stringify(value));
      this.probability = probability;
      let inputs = this.element.find("input");
      let label = this.element.find("span");
      if (this.type == "range") {
        inputs[0].value = value[0];
        inputs[1].value = value[1];
        let p = 100 * probability;
        inputs[2].value = p;
        label.text(this.probStr(p))
      } else {
        inputs[0].value = value;
        let p = 100 * probability;
        inputs[1].value = p;
        label.text(this.probStr(p));
      }
      return true;
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
        this.values.pop();
        this.probabilities.pop();
        this.inputs.pop();
        last.element.remove();
      }
    }

    // Sets the value
    set(v) {
      let copy;
      try {
        copy = JSON.parse(JSON.stringify(v));
      } catch (e) {
        return false;
      }
      if (copy.length != 2) {
        return false
      }
      let values = copy[0];
      let probabilities = copy[1]
      if (values.length != probabilities.length) {
        return false;
      }

      // Add/remove inputs if necessary to match the given set
      let diff = Math.abs(values.length - this.values.length);
      for (let i = 0; i < diff; i++) {
        if (values.length > this.values.length) {
          this.add();
        } else {
          this.remove();
        }
      }

      let success = true;
      this.values = values;
      this.probabilities = probabilities;
      for (let i = 0; i < this.inputs.length; i++) {
        success &= this.inputs[i].set(this.values[i], this.probabilities[i]);
      }
      return success;
    }
  }

  // A variable in the simulator config
  class Var {
    constructor(name, input) {
      this.name = name;
      this.input = input;
    }

    // Sets the value. Returns true/false if successful
    set(v) {
      return this.input.set(v);
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

    // Sets the value from a JSON object. Returns true/false if successful
    fromJSON(json) {
      let success = true;
      success &= this.ndays.set(json.ndays);
      success &= this.rehireRate.set(json.rehire_rate);
      success &= this.peopleNewMoney.set(json.people_new_money);
      success &= this.companiesNewMoney.set(json.companies_new_money);
      success &= this.spending.set(json.spending);
      success &= this.industries.set(json.industries);
      return success;
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

    // Sets the value from a JSON object. Returns true/false if successful
    fromJSON(json) {
      // Add/remove periods if necessary to match the given set
      let diff = Math.abs(json.length - this.periods.length);
      for (let i = 0; i < diff; i++) {
        if (json.length > this.periods.length) {
          this.add();
        } else {
          this.remove();
        }
      }

      let success = true;
      for (let i = 0; i < this.periods.length; i++) {
        success &= this.periods[i].fromJSON(json[i]);
      }
      return success;
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

    toJSON() {
      let json = {
        ncompanies: this.ncompanies.input.value,
        employees: [
          this.employees.input.values,
          this.employees.input.probabilities
        ],
        income: [
          this.income.input.values,
          this.income.input.probabilities
        ],
        periods: []
      };

      for (let i = 0; i < this.periods.periods.length; i++) {
        let p = this.periods.periods[i];
        json.periods.push({
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

      return json;
    }

    // Sets the config from a JSON object. Returns true/false if successful
    fromJSON(json) {
      let success = true;
      success &= this.ncompanies.set(json.ncompanies);
      success &= this.employees.set(json.employees);
      success &= this.income.set(json.income);
      success &= this.periods.fromJSON(json.periods);
      return success;
    }
  }

  // A chart of results
  class ChartComponent {
    // type = one of {"person_wealth", "company_wealth", "unemployment", "out_of_business"}
    // industry = one of the industries specified in the config
    constructor(type, industry) {
      this.type = type;
      this.industry = industry;
      this.element = element("canvas")
        .attr("width", "400")
        .attr("height", "400");

      // Initialize the data
      let datasets = [];
      let red = 50;
      let green = 150;
      let blue = 168;
      if (this.type == "person_wealth" || this.type == "company_wealth") {
        // Create one dataset per percentile we want to plot
        let labels = ["Min", "10%", "25%", "50%", "75%", "90%", "Max"];
        for (let i = 0; i < labels.length; i++) {
          let color = `rgb(${red}, ${green - 20*i}, ${blue})`;
          datasets.push({
            label: labels[i],
            data: [],
            fill: false,
            backgroundColor: color,
            borderColor: color
          });
        }
      } else if (this.type == "unemployment" || this.type == "out_of_business") {
        let color = `rgb(${red}, ${green}, ${blue})`;
        datasets.push({
          label: "",
          data: [],
          fill: false,
          backgroundColor: color,
          borderColor: color
        });
      } else {
        throw Error("type '" + type + "' not supported");
      }

      // Initialize the chart
      let titles = {
        person_wealth: "Distribution of wealth across people",
        company_wealth: "Distribution of wealth across companies",
        unemployment: "Unemployment rate",
        out_of_business: "Percent of companies out of business"
      }
      this.chart = new Chart(this.element, {
        type: "line",
        data: {
          labels: [], // days
          datasets: datasets
        },
        options: {
          title: {
            display: true,
            text: titles[this.type]
          }
        }
      });
    }

    // Update the chart from a json object of new data from the server
    update(newData) {
      let data = newData[this.industry][this.type];
      let day = this.chart.data.labels.length;
      this.chart.data.labels.push(day);
      if (this.type == "person_wealth" || this.type == "company_wealth") {
        // Add new data at only the percentiles we want to plot
        let percentiles = [0, 10, 25, 50, 75, 90, 100];
        for (let i = 0; i < percentiles.length; i++) {
          let p = percentiles[i];
          this.chart.data.datasets[i].data.push(data[p]);
        }
      } else {
        // Add new values to the single dataset
        this.chart.data.datasets[0].data.push(data);
      }
      this.chart.update();
    }
  }

  // "Run" button sends a the config to the server and displays the results
  // as it runs
  class RunButton {
    constructor(config, chartsContainer) {
      this.element = element("button")
        .addClass("btn")
        .addClass("btn-primary")
        .attr("type", "button")
        .text("Run")
        .on("click", () => {
          // Create charts for each industry in the config
          let industries = config.periods.periods[0].industries.input.values;
          let chartTypes = ["person_wealth", "company_wealth", "unemployment", "out_of_business"];
          let charts = [];
          let chartsElement = element("div");
          industries.forEach((industry) => {
            chartsElement.append(element("h2").text(industry));
            chartTypes.forEach((type) => {
              let chart = new ChartComponent(type, industry);
              charts.push(chart);
              chartsElement.append(chart.element);
            });
          });

          // Render charts
          chartsContainer.empty();
          chartsContainer.append(chartsElement);

          // Send config to the server, and populate results in the charts
          let ws = new WebSocket("ws://localhost:8000/run-simulator");

          ws.onopen = (e) => {
            ws.send(JSON.stringify(config.toJSON()));
          };

          ws.onmessage = (e) => {
            let msg = JSON.parse(e.data);
            charts.forEach((chart) => {
              chart.update(msg.results);
            });
          };
        });
    }
  }

  // Share button. Generates a link to the site preloaded with the current
  // config
  class ShareButton {
    constructor(config) {
      this.element = element("button")
        .addClass("btn")
        .addClass("btn-secondary")
        .attr("type", "button")
        .text("Share")
        .tooltip({
          title: "Link copied!",
          trigger: "manual"
        });
      this.element
        .on("click", () => {
          // Generate URL and copy it to clipboard
          let json = JSON.stringify(config.toJSON());
          let url = (window.location.origin + "?" + urlParams.config + "="
            + encodeURIComponent(json));
          navigator.clipboard.writeText(url);
          this.element.tooltip("show");
        })
        .on("blur", () => {
          // Hide the tooltip when button loses focus
          this.element.tooltip("hide");
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

  // Set the initial config values from the URL param, if present
  let param = (new URLSearchParams(document.location.search)).get(urlParams.config);
  if (param != null) {
    try {
      let givenConfig = JSON.parse(decodeURIComponent(param));
      config.fromJSON(givenConfig);
    } catch (e) {
      console.error("error while parsing URL parameter '" + urlParams.config + "': " + e);
    }
  }

  // Run and share buttons
  let chartsContainer = $("#charts-container");
  $("#button-container")
    .append((new RunButton(config, chartsContainer)).element)
    .append((new ShareButton(config)).element);
});
