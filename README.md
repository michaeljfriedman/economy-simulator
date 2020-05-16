# Economy Simulation

This project simulates the economy using a simplified model. Our goal is to
see what happens to the distribution of wealth across people and companies, the
the unemployment rate, and the company survival rate, when you vary certain
parameters.

This README covers how the simulation is designed and how to run it. For
development details, see the [developer guide](docs/dev_guide.md).

## Design

In this project, we create a simplified model of the economy as what (we
believe) it is fundamentally: a network of circulating money, and to track
various metrics about the economy.

The basic model works like this. There are two kinds of entities: *people* and
*companies*. Each person works for a company, and receives a paycheck from it
each month. They spend a portion of their money at different companies during
the course of each month, saving anything they have leftover. Companies lay off
employees when they can no longer afford to pay them, hire new ones if they can
afford to, and go out of business when they have no more employees. Each company
also belongs to an industry, and we can tweak the amount people spend in each
industry. We run this system for a fixed period of time. People and companies
may build wealth, scrape by, or collapse, according to this probabilistic model.

We're primarily interested in two things:

1. Understanding a "normal" economy: Under "normal" conditions, where does the
   money go (the distribution of wealth across people, companies, and
   industries), how does the unemployment rate look, and how does company
   survival rate look (do some companies die out)? Is there an equilibrium?
   Which variables affect this outcome (e.g. number of companies, income
   distribution, etc.)?
2. The effects of a shutdown (e.g. during a [pandemic](https://www.wsj.com/graphics/march-changed-everything/)):
   What happens if consumers are temporarily blocked from spending in certain
   industries?

### Simulation algorithm

Initialization:

- Each company is assigned to an industry and is assigned a number of employees
  from a distribution
- Each person is assigned income and an initial spending rate for the first
  month, both from a distribution
- Both people and companies get some number of months' worth of money (income
  for people, payroll for companies), chosen from a distribution

Each day:

- Each person picks an industry to spend in from a distribution, and picks a
  random company within that industry. They spend 1/30 of their monthly
  spending to that company (this model has 30 days per month)
- At the end of the month, companies rehire unemployed people if they can afford
  them, and pay their employees 1 month's income. If they don't have enough
  money to cover payroll, they pick a random person to lay off until they do. If
  they run out of employees, they go out of business (removed from the economy).
  People pick a new spending rate for the next month.

## Running a simulation

The simulator has both a publicly available web app at
<https://economy-simulator.herokuapp.com>, and a command-line app you can run
locally. You can use either to run simulations. Generally the web app is easier,
but you may find the command-line version more useful to automate many
simulations with different variables.

### Inputs

The simulation lets you specify a number of parameters for the economy. Some of
these are distributions, which specify *values* and a corresponding
*probability* of that value being selected. First you need to set the base
parameters, which apply for the entire simulation:

- **Number of companies**
- **Employee distribution**: a distribution of how many employees are assigned to
  companies. For example, you could say there's a 50% chance of a company
  having 10 employees, and 50% chance of 20.
- **Income distribution**: a distribution of people's annual income. Each
  employed person receives an equal portion (1/12) of their annual income each
  month.

Then you specify a number of *periods* - a limited period of time during which
certain parameters apply. The periods run in order, and each has:

- **Number of days**: the duration of the period
- **Rehire rate**: the probability that an unemployed person is rehired when an
  opening comes up.
- **Additional money for people**: the distribution of additional money people
  get at the start of this period, specified in months of income. In the first
  period, this is the amount of money people will start the simulation with
  (e.g. 100% of people receive 1 month's income), and in later periods, this
  can simulate "stimulus checks".
- **Additional money for companies**: analogous distribution for companies,
  specified in months of payroll.
- **Spending distribution**: the distribution of people's spending rates. Each
  month, every person picks a spending rate (a fraction of their money) from
  this distribution, and spends that much in that month. Each value should be
  a pair of numbers representing a *range* of rates people can choose from
  (e.g. 0 to 1 would be the full range of their money). People pick a range
  according to the distribution, and then choose a value uniformly within that
  range. So for example, if you had two ranges [0, 0.5] with 25% probability,
  and [0.5, 1] with 75% probability, this would be a "skewed" distribution that
  gives people a tendency to spend more.
- **Industry distribution**: the distribution of how likely a person is to spend
  money in a particular industry. So for example, if you had 5 industries, 4
  that each have 25% probability, and 1 with 0%, this would simulate the effect
  of blocking spending in a particular industry (e.g. if it's temporarily shut
  down).

The web app has boxes where you can set each of these parameters. For the CLI,
you'll need to write a config file that sets these parameters. See the
[developer guide](docs/dev_guide.md#cli) for the spec of the config and an
example that you can copy/paste into a file, e.g. config.json. Then you can run
the simulation with:

```bash
cd cli
python main.py --config=config.json --output=output/
```

This will produce a bunch of metrics in the output/ directory. You can plot
them with:

```bash
python plot.py --data-directory=output/ --output=plot.png
```

Use the `--help` flag for more details on command-line options.

### Outputs

Running a simulation produces 4 charts for each industry, with one data point
at the beginning of each month:

- Distribution of wealth across people
- Distribution of wealth across companies
- Unemployment rate
- Percentage of companies that went out of business

The distributions are represented with multiple lines showing various
percentiles.

That's it! Have fun playing around with the parameters!

---

Copyright 2020, Michael Friedman
