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

  const defaultConfig = {
    ncompanies: 100,
    income: [
      [50000],
      [1]
    ],
    company_size: [
      [10],
      [1]
    ],
    periods: [{
      duration: 360,
      person_stimulus: 1,
      company_stimulus: 1,
      unemployment_benefit: 0.8,
      rehire_rate: 0.8,
      spending_inclination: 0.5,
      spending_distribution: [
        ["industry 1"],
        [1]
      ]
    }]
  };

  // Creates a new jQuery element
  let element = function(name) {
    return $(document.createElement(name));
  }

  // Creates a padded conatiner div with the child inside
  let withPadding = function(child) {
    return element("div").addClass("p-3").addClass("m-n3")
      .append(child);
  };

  // An input for a number variable, given its type (integer or float) and
  // display name.
  class NumberInput {
    constructor(displayName, type) {
      this.value = 0;
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
      
      this.element = element("div").addClass("card")
        .append(element("div").addClass("card-body")
          .append(label)
          .append(input)
        );
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

  // An input for a percentage, given its display name.
  class PercentageInput {
    constructor(displayName) {
      this.value = 0;
      this.element = null;

      let label = element("h4").addClass("card-title")
        .text(displayName);

      let inputLabel = element("span")
        .text(this.probStr(100 * this.value));
      let input = element("input")
        .addClass("form-control-range")
        .attr("type", "range")
        .attr("value", this.value.toString())
        .on("input", (e) => {
          // Track the value
          this.value = e.currentTarget.valueAsNumber / 100;

          // Update the text label
          inputLabel.text(this.probStr(e.currentTarget.value));
        });

      this.element = element("div").addClass("card")
        .append(element("div").addClass("card-body")
          .append(label)
          .append(input)
          .append(inputLabel)
        );
    }

    // Returns the probability string, given the value out of 100
    probStr(v) {
      return v.toString() + "%";
    }

    // Sets the value
    set(v) {
      if (v == null || v == undefined) {
        return false;
      }

      this.value = v;
      let p = 100 * this.value;
      let input = this.element.find("input")[0];
      let label = this.element.find("span");
      input.value = p;
      label.text(this.probStr(p));
      return true;
    }
  }

  // An input for one (value, probability) pair in a distribution, given its
  // type
  class DistributionInputPair {
    // type is one of {"integer", "float", "string"}
    constructor(type) {
      this.value = (type == "string")? "" : 0;
      this.probability = 0;
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
      if (this.type == "integer" || this.type == "float") {
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

      this.element = element("div").addClass("row")
        .append(element("div").addClass("col")
          .append(value)
        ).append(element("div").addClass("col")
          .append(element("div").addClass("row")
            .append(prob)
          ).append(element("div").addClass("row")
            .append(probLabel)
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
      inputs[0].value = value;
      let p = 100 * probability;
      inputs[1].value = p;
      label.text(this.probStr(p));
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

      this.element = element("div")
        .append(addButton)
        .append(removeButton);
    }
  }

  // A container for all the inputs in a distribution
  class DistributionInput {
    // type is one of the values accepted by DistributionInputPair
    constructor(displayName, type) {
      this.type = type;
      this.values = [];
      this.probabilities = [];
      this.inputs = []; // array of DistributionInputPairs

      // Create the element
      let label = element("h4").addClass("card-title")
        .text(displayName);

      let buttons = new AddRemoveButtons(
        // The "add" button adds a new DistributionInputPair
        () => {
          this.add();
        },

        // The "remove" button removes the last DistributionInputPair
        () => {
          this.remove();
        }
      );

      this.element = element("div").addClass("card")
        .append(element("div").addClass("card-body")
          .append(label)
          .append(withPadding(buttons.element))
        );

      this.add();
    }

    add() {
      let nextIndex = this.inputs.length;
      let input = new DistributionInputPair(this.type);
      input.onInput(() => {
        this.values[nextIndex] = input.value;
        this.probabilities[nextIndex] = input.probability;
      });
      this.values.push(input.value);
      this.probabilities.push(input.probability);
      this.inputs.push(input);
      $(this.element.find(".card-body")[0]).append(withPadding(input.element));
    }

    remove() {
      let n = this.inputs.length;
      if (n != 0) {
        let last = this.inputs[n-1];
        this.values.pop();
        this.probabilities.pop();
        this.inputs.pop();
        last.element.parent().remove();
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

  // Grid of Bootstrap cards
  class CardGrid {
    // title (object) = title text and header (h) level, e.g. {text: "Title", h: 2}
    // hasBorder (boolean) = whether to have a border
    // buttons (AddRemoveButtons) = optional add/remove buttons
    // breakpoints (object) = how many cards to have per row at each breakpoint.
    //   Each breakpoint is optional e.g. {md: 2, lg: 3}
    constructor(title, hasBorder, buttons, breakpoints) {
      // Set the border
      let grid = element("div").addClass("card");
      if (!hasBorder) {
        grid.addClass("border-0");
      }

      // Set breakpoints
      let row = element("div").addClass("row").addClass("row-cols-1");
      Object.keys(breakpoints).forEach((x) => {
        row.addClass(`row-cols-${x}-${breakpoints[x]}`);
      });

      // Add the title and buttons
      let body = element("div").addClass("card-body")
        .append(element(`h${title.h}`).addClass("card-title").text(title.text));
      if (buttons != null) {
        body.append(withPadding(buttons.element));
      }
      body.append(withPadding(row));

      // Put the whole thing together
      this.element = grid.append(body);
      this.cards = [];
    }

    add(card) {
      $(this.element.find(".row")[0])
      .append(element("div").addClass("col").addClass("mb-4")
        .append(card)
      );

      this.cards.push(card);
    }

    remove() {
      if (this.cards.length != 0) {
        let last = this.cards[this.cards.length - 1];
        this.cards.pop();
        last.parent().remove();
      }
    }
  }

  // A container for the Vars of a single period
  class Period {
    // index = index of this period (for display)
    constructor(index) {
      this.duration = new Var("duration", new NumberInput("Number of days", "integer"));
      this.person_stimulus = new Var("person_stimulus", new NumberInput("Person stimulus or tax", "float"));
      this.company_stimulus = new Var("company_stimulus", new NumberInput("Company stimulus or tax", "float"));
      this.unemployment_benefit = new Var("unemployment_benefit", new NumberInput("Unemployment benefit", "float"))
      this.rehire_rate = new Var("rehire_rate", new NumberInput("Rehire rate", "float"));
      this.spending_inclination = new Var("spending_inclination", new PercentageInput("Inclination to spend"));
      this.spending_distribution = new Var("spending_distribution", new DistributionInput("Spending distribution across industries", "string"));

      let cards = new CardGrid({text: `Period ${index}`, h: 3}, true, null, {md: 2, lg: 3});
      [
        this.duration,
        this.person_stimulus,
        this.company_stimulus,
        this.unemployment_benefit,
        this.rehire_rate,
        this.spending_inclination,
        this.spending_distribution
      ].forEach((x) => {
        cards.add(x.input.element);
      });

      this.element = cards.element;
    }
  }

  // A container for the entire config
  class Config {
    constructor() {
      this.ncompanies = new Var("ncompanies", new NumberInput("Number of companies", "integer"));
      this.income = new Var("income", new DistributionInput("Income levels", "integer"));
      this.company_size = new Var("company_size", new DistributionInput("Company size", "integer"));
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

      this.periodsCards = new CardGrid({text: "Periods", h: 2}, false, periodButtons, {});
      let baseParamsCards = new CardGrid({text: "Base Parameters", h: 2}, false, null, {md: 2, lg: 3});
      [
        this.ncompanies,
        this.income,
        this.company_size
      ].forEach((x) => {
        baseParamsCards.add(x.input.element);
      });

      this.element = element("div")
        .append(withPadding(baseParamsCards.element))
        .append(withPadding(this.periodsCards.element));

      // Set default values
      this.fromJSON(defaultConfig);
    }

    addPeriod() {
      let p = new Period(this.periods.length + 1);
      this.periods.push(p);
      this.periodsCards.add(p.element);
    }

    removePeriod() {
      if (this.periods.length != 0) {
        this.periods.pop();
        this.periodsCards.remove();
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
          this.company_size.input.values,
          this.company_size.input.probabilities
        ],
        periods: []
      };

      for (let i = 0; i < this.periods.length; i++) {
        let p = this.periods[i];
        json.periods.push({
          duration: p.duration.input.value,
          person_stimulus: p.person_stimulus.input.value,
          company_stimulus: p.company_stimulus.input.value,
          unemployment_benefit: p.unemployment_benefit.input.value,
          rehire_rate: p.rehire_rate.input.value,
          spending_inclination: p.spending_inclination.input.value,
          spending_distribution: [
            p.spending_distribution.input.values,
            p.spending_distribution.input.probabilities
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
      success &= this.company_size.set(json.company_size);

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
        success &= this.periods[i].duration.set(json.periods[i].duration);
        success &= this.periods[i].person_stimulus.set(json.periods[i].person_stimulus);
        success &= this.periods[i].company_stimulus.set(json.periods[i].company_stimulus);
        success &= this.periods[i].unemployment_benefit.set(json.periods[i].unemployment_benefit);
        success &= this.periods[i].rehire_rate.set(json.periods[i].rehire_rate);
        success &= this.periods[i].spending_inclination.set(json.periods[i].spending_inclination);
        success &= this.periods[i].spending_distribution.set(json.periods[i].spending_distribution);
      }

      if (!success) {
        throw Error("failed to parse config");
      }
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

  // Container for attributes of one type of chart
  class ChartType {
    // name = the name
    // displayName, {x,y}Label, legend = the title, {x,y}Label, and legend of the ChartComponent
    constructor(name, displayName, xLabel, yLabel, legend) {
      this.name = name;
      this.displayName = displayName;
      this.xLabel = xLabel;
      this.yLabel = yLabel;
      this.legend = legend;
    }
  }

  // A group of charts
  // element = the HTML card containing the charts
  // charts = an object of ChartComponents, indexed by name, e.g:
  // {
  //   "person_money": new ChartComponent(...),
  //   ...
  // }
  class ChartGroup {
    // name (string) = name of the groups. This will be the title of the card
    // types (array of ChartTypes)
    constructor(name, types) {
      this.element = withPadding(
        element("div").addClass("card").addClass("border-0")
        .append(element("div").addClass("card-body")
          .append(element("h2").addClass("card-title").text(name))
          .append(element("div").addClass("row"))
        )
      );

      this.charts = {};

      types.forEach((t) => {
        let chart = new ChartComponent(t.displayName, t.legend, t.xLabel, t.yLabel);
        this.charts[t.name] = chart;
        $(this.element.find(".row")[0]).append(
          element("div").addClass("col-md-6")
          .append(chart.element)
        );
      });
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
          // Create charts
          let person_money = new ChartType(
            "person_money",
            "Distribution of wealth across people",
            "Months",
            "Dollars",
            ["Min", "10%", "25%", "50%", "75%", "90%", "Max"]
          );

          let company_money = new ChartType(
            "company_money",
            "Distribution of wealth across companies",
            "Months",
            "Dollars",
            ["Min", "10%", "25%", "50%", "75%", "90%", "Max"]
          );

          let person_unemployment = new ChartType(
            "person_unemployment",
            "Unemployment rate",
            "Months",
            "Rate",
            [""]
          );

          let company_closures = new ChartType(
            "company_closures",
            "Company closure rate",
            "Months",
            "Fraction",
            [""]
          );

          let circulation = new ChartType(
            "circulation",
            "Total money in circulation",
            "Months",
            "Dollars",
            [""]
          );

          let charts = {
            overall: {},
            income_levels: {},
            industries: {}
          };

          // Make overall charts
          charts.overall = new ChartGroup("Overall", [person_money, company_money, person_unemployment, company_closures, circulation]);

          // Make per-income level charts
          charts.income_levels = {}
          let income_levels = [];
          config.income.input.values.forEach((i) => {
            income_levels.push(i.toString());
          });
          income_levels.forEach((i) => {
            charts.income_levels[i] = new ChartGroup(i, [person_money, person_unemployment]);
          });

          // Make per-industry charts
          charts.industries = {};
          let industries = config.periods[0].spending_distribution.input.values;
          industries.forEach((i) => {
            charts.industries[i] = new ChartGroup(i, [person_money, company_money, person_unemployment, company_closures]);
          });

          // Render charts
          chartsContainer.empty();
          chartsContainer.append(charts.overall.element);
          income_levels.forEach((i) => {
            chartsContainer.append(charts.income_levels[i].element);
          });
          industries.forEach((i) => {
            chartsContainer.append(charts.industries[i].element);
          });

          // Send config to the server, and populate results in the charts
          let protocol = (document.location.protocol == "https:") ? "wss:" : "ws:";
          let ws = new WebSocket(`${protocol}//${document.location.host}/run-simulator`);

          ws.onopen = (e) => {
            ws.send(JSON.stringify(config.toJSON()));
          };

          ws.onmessage = (e) => {
            let msg = JSON.parse(e.data);

            // Only plot the first day of each month
            if (msg.day % 30 != 0) {
              return;
            }

            // Add the new data to the charts
            let data = msg.data;

            // Overall charts
            [person_money, company_money, person_unemployment, company_closures, circulation].forEach((t) => {
              charts.overall.charts[t.name].update(data.overall[t.name]);
            });

            // Per-income level charts
            income_levels.forEach((i) => {
              [person_money, person_unemployment].forEach((t) => {
                charts.income_levels[i].charts[t.name].update(data.income_levels[i][t.name]);
              });
            });

            // Industry charts
            industries.forEach((i) => {
              [person_money, company_money, person_unemployment, company_closures].forEach((t) => {
                charts.industries[i].charts[t.name].update(data.industries[i][t.name]);
              });
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
          // Ref: https://stackoverflow.com/questions/47879184/document-execcommandcopy-not-working-on-chrome
          let json = JSON.stringify(config.toJSON());
          let url = (window.location.origin + "?" + urlParams.config + "="
                     + encodeURIComponent(json));

          let text = document.createElement("textarea");
          text.textContent = url;
          document.body.appendChild(text);

          let range = document.createRange();
          range.selectNode(text);

          let selection = document.getSelection();
          selection.removeAllRanges();
          selection.addRange(range);

          document.execCommand("copy");
          this.element.tooltip("show");

          selection.removeAllRanges();
          document.body.removeChild(text);
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
