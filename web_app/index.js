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

  // Creates a padded conatiner div with the child inside
  let withPadding = function(child) {
    return element("div").addClass("py-3").addClass("my-n3")
      .append(child);
  };

  // An input for a number variable, given its type (integer or float),
  // display name and default value.
  class NumberInput {
    constructor(type, displayName, defaultValue) {
      this.value = defaultValue;
      this.element = null;

      let label = element("h4").addClass("card-title")
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
      
      this.element = withPadding(
        element("div").addClass("card")
        .append(element("div").addClass("card-body")
          .append(label)
          .append(input)
        )
      )
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

      this.element = withPadding(
        element("div").addClass("row")
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
        .addClass("btn")
        .addClass("btn-secondary")
        .addClass("mr-1")
        .attr("type", "button")
        .text("Add")
        .on("click", onClickAdd);

      let removeButton = element("button")
        .addClass("btn")
        .addClass("btn-secondary")
        .addClass("mr-1")
        .attr("type", "button")
        .text("Remove")
        .on("click", onClickRemove);

      this.element = withPadding(
        element("div")
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
      let label = element("h4").addClass("card-title")
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

      this.element = withPadding(
        element("div").addClass("card")
        .append(element("div").addClass("card-body")
          .append(label)
          .append(buttons.element)
        )
      );

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
      $(this.element.find(".card-body")[0]).append(input.element);
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
      this.duration = new Var("duration", new NumberInput("integer", "Number of days", 0));
      this.personStimulus = new Var("person_stimulus", new NumberInput("float", "Person stimulus", 0));
      this.companyStimulus = new Var("company_stimulus", new NumberInput("float", "Company stimulus", 0));
      this.rehireRate = new Var("rehire_rate", new NumberInput("float", "Rehire rate", 0));
      this.spending = new Var("spending", new DistributionInputs("range", "Spending distribution"));
      this.industries = new Var("industries", new DistributionInputs("string", "Industry distribution"));

      this.element = withPadding(
        element("div").addClass("card")
        .append(element("div").addClass("card-body")
          .append(element("h3").addClass("card-title").text("Period " + index))
          .append(this.duration.input.element)
          .append(this.personStimulus.input.element)
          .append(this.companyStimulus.input.element)
          .append(this.rehireRate.input.element)
          .append(this.spending.input.element)
          .append(this.industries.input.element)
        )
      );
    }

    // Sets the value from a JSON object. Returns true/false if successful
    fromJSON(json) {
      let success = true;
      success &= this.duration.set(json.duration);
      success &= this.personStimulus.set(json.person_stimulus);
      success &= this.companyStimulus.set(json.company_stimulus);
      success &= this.rehireRate.set(json.rehire_rate);
      success &= this.spending.set(json.spending);
      success &= this.industries.set(json.industries);
      return success;
    }
  }

  // A container for the entire config
  class Config {
    constructor() {
      this.ncompanies = new Var("ncompanies", new NumberInput("integer", "Number of companies", 0));
      this.income = new Var("income", new DistributionInputs("integer", "Income levels"));
      this.companySize = new Var("company_size", new DistributionInputs("integer", "Company size"));
      this.periods = [];

      let periodButtons = new AddRemoveButtons(
        // The "add" button adds a new period
        () => {
          this.addPeriod();
        },

        // The "remove" button removes a period
        () => {
          this.removePeriod();
        }
      );

      this.periodsContainer = (
        withPadding(element("div").addClass("card").addClass("border-0")
        .append(element("div").addClass("card-body")
          .append(element("h2").addClass("card-title").text("Periods"))
          .append(periodButtons.element)
          .append(element("div").addClass("row"))
          )
        )
      );

      this.element = (
        element("div")
        .append(withPadding(element("div").addClass("card").addClass("border-0")
          .append(element("div").addClass("card-body")
            .append(element("h2").addClass("card-title").text("Base Parameters"))
            .append(element("div").addClass("row")
              .append(element("div").addClass("col-md-4")
                .append(this.ncompanies.input.element)
              ).append(element("div").addClass("col-md-4")
                .append(this.income.input.element)
              ).append(element("div").addClass("col-md-4")
                .append(this.companySize.input.element)
              )
            )
          )
        ))
      ).append(this.periodsContainer);

      this.addPeriod();
    }

    addPeriod() {
      let p = new Period(this.periods.length + 1);
      this.periods.push(p);
      $(this.periodsContainer.find(".row")[0]).append(
        element("div").addClass("col")
        .append(p.element)
      );
    }

    removePeriod() {
      if (this.periods.length != 0) {
        let last = this.periods[this.periods.length - 1];
        this.periods.pop();
        last.element.parent().remove();
      }
    }

    toJSON() {
      let json = {
        ncompanies: this.ncompanies.input.value,
        income: [
          this.income.input.values,
          this.income.input.probabilities
        ],
        company_size: [
          this.companySize.input.values,
          this.companySize.input.probabilities
        ],
        periods: []
      };

      for (let i = 0; i < this.periods.length; i++) {
        let p = this.periods[i];
        json.periods.push({
          duration: p.duration.input.value,
          person_stimulus: p.personStimulus.input.value,
          company_stimulus: p.companyStimulus.input.value,
          rehire_rate: p.rehireRate.input.value,
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
      success &= this.income.set(json.income);
      success &= this.companySize.set(json.companySize);

      // Add/remove periods if necessary to match the given set
      let diff = Math.abs(json.periods.length - this.periods.length);
      for (let i = 0; i < diff; i++) {
        if (json.periods.length > this.periods.length) {
          this.addPeriod();
        } else {
          this.removePeriod();
        }
      }

      for (let i = 0; i < this.periods.length; i++) {
        success &= this.periods[i].fromJSON(json.periods[i]);
      }
      return success;
    }
  }

  // A chart of results
  class ChartComponent {
    // title = the title of the graph
    // legend = a list of labels for each line in the graph, shown in the legend
    // {x,y}Label = the label for each axis
    constructor(title, legend, xLabel, yLabel) {
      this.element = element("canvas")
        .attr("width", "400")
        .attr("height", "400");

      // Initialize the data
      let datasets = [];
      let red = 50;
      let green = 150;
      let blue = 168;
      for (let i = 0; i < legend.length; i++) {
        let color = `rgb(${red}, ${green - 20*i}, ${blue})`;
        datasets.push({
          label: legend[i],
          data: [],
          fill: false,
          backgroundColor: color,
          borderColor: color
        });
      }

      // Initialize the chart
      this.chart = new Chart(this.element, {
        type: "line",
        data: {
          labels: [], // x axis
          datasets: datasets // y axis, one dataset for each line
        },
        options: {
          title: {
            display: true,
            text: title
          },
          scales: {
            yAxes: [{
              scaleLabel: {
                display: true,
                labelString: yLabel
              }
            }],
            xAxes: [{
              scaleLabel: {
                display: true,
                labelString: xLabel
              }
            }]
          }
        }
      });
    }

    // Add a new data point to the chart. newData is an array, where each entry
    // i is the new value for legend[i]
    update(newData) {
      let x = this.chart.data.labels.length;
      this.chart.data.labels.push(x);
      for (let i = 0; i < newData.length; i++) {
        this.chart.data.datasets[i].data.push(newData[i]);
      }
      this.chart.update();
    }
  }

  // Container for all of the charts of a particular statistic (e.g. person
  // wealth, company wealth), across all industries
  class Statistic {
    // name = one of {person_wealth, company_wealth, unemployment, out_of_business}
    // displayName, {x,y}Label, legend = the title, {x,y}Label, and legend of the ChartComponent
    // yIndices = when the server provides an array of values for this statistic (e.g. person wealth),
    //   specify an array of indices to plot. Otherwise (e.g. unemployment), set this to null
    constructor(name, displayName, xLabel, yLabel, legend, yIndices) {
      this.name = name;
      this.displayName = displayName;
      this.xLabel = xLabel;
      this.yLabel = yLabel;
      this.legend = legend;
      this.yIndices = yIndices;

      // Parallel arrays - the ChartComponent for each industry
      this.chartComponents = [];
      this.industries = [];
    }
  }

  // "Run" button sends a the config to the server and displays the results
  // as it runs
  class RunButton {
    constructor(config, chartsContainer) {
      this.element = element("button")
        .addClass("btn")
        .addClass("btn-primary")
        .addClass("btn-lg")
        .addClass("mr-1")
        .attr("type", "button")
        .text("Run")
        .on("click", () => {
          // Create charts for each industry in the config
          let industries = config.periods[0].industries.input.values;
          let charts = [
            new Statistic(
              "person_wealth",
              "Distribution of wealth across people",
              "Months",
              "Dollars",
              ["Min", "10%", "25%", "50%", "75%", "90%", "Max"],
              [0, 10, 25, 50, 75, 90, 100]
            ),
            new Statistic(
              "company_wealth",
              "Distribution of wealth across companies",
              "Months",
              "Dollars",
              ["Min", "10%", "25%", "50%", "75%", "90%", "Max"],
              [0, 10, 25, 50, 75, 90, 100]
            ),
            new Statistic(
              "unemployment",
              "Unemployment rate",
              "Months",
              "Rate",
              [""],
              null
            ),
            new Statistic(
              "out_of_business",
              "Fraction of companies out of business",
              "Months",
              "Fraction",
              [""],
              null
            )
          ];
          let chartsElement = withPadding(
            element("div").addClass("card").addClass("border-0")
            .append(element("div").addClass("card-body")
              .append(element("h2").addClass("card-title").text("Results"))
            )
          );
          industries.forEach((industry) => {
            $(chartsElement.find(".card-body")[0]).append(element("h3").text(industry));
            charts.forEach((chart) => {
              let chartComponent = new ChartComponent(chart.displayName, chart.legend, chart.xLabel, chart.yLabel);
              chart.chartComponents.push(chartComponent);
              chart.industries.push(industry);
              chartsElement.append(chartComponent.element);
            });
          });

          // Render charts
          chartsContainer.empty();
          chartsContainer.append(chartsElement);


          // Send config to the server, and populate results in the charts
          let protocol = (document.location.protocol == "https:") ? "wss:" : "ws:";
          let ws = new WebSocket(`${protocol}//${document.location.host}/run-simulator`);

          ws.onopen = (e) => {
            ws.send(JSON.stringify(config.toJSON()));
          };

          ws.onmessage = (e) => {
            let msg = JSON.parse(e.data);

            // Only plot the first day of each month
            if (msg.day != 0 && msg.day % 30 != 1) {
              return;
            }

            // Add the new data to each chart
            charts.forEach((chart) => {
              for (let i = 0; i < chart.chartComponents.length; i++) {
                let industry = chart.industries[i];
                let data = msg.results[industry][chart.name];

                // Extract only the y indices in the plot
                let newData = [];
                if (chart.yIndices != null) {
                  chart.yIndices.forEach((idx) => {
                    newData.push(data[idx]);
                  });
                } else {
                  newData.push(data);
                }

                chart.chartComponents[i].update(newData);
              }
            });
          };
        });
    }
  }

  // "Get link" button. Generates a link to the site preloaded with the current
  // config
  class GetLinkButton {
    constructor(config) {
      this.element = element("button")
        .addClass("btn")
        .addClass("btn-secondary")
        .addClass("btn-lg")
        .addClass("mr-1")
        .attr("type", "button")
        .text("Get Link")
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
  $("#title-container")
  .append(
    withPadding(
      element("h1").text(title)
    )
  );

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

  // Run and "get link" buttons
  let chartsContainer = $("#charts-container");
  $("#button-container")
  .append(
    withPadding(
      element("div")
      .append((new RunButton(config, chartsContainer)).element)
      .append((new GetLinkButton(config)).element)
    )
  );
});
