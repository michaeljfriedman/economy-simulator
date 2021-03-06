# Economy Simulation

This project simulates the economy using a simplified model. Our goal is to
see what happens to the distribution of wealth across people and companies, the
the unemployment rate, and the business closure rate, when you vary certain
parameters.

> Note that this is merely an experimental model of a toy economy. I do not
claim that this is an accurate model of reality, and any results derived from
this model should not be used to conclude what would actually happen in reality.
I only use it to understand the potential effects of certain parameters on a
simplified model.

This README covers how the simulation is designed and how to run it. For
development details, see the [developer guide](docs/dev_guide.md).

## Design

In this project, we create a simplified model of the economy as what (we
believe) it is fundamentally: a network of circulating money, and to track
various metrics about the economy.

The basic model works like this. There are two kinds of entities: *people* and
*companies*. Each person works for a company, and receives a paycheck from it
each month. They spend a portion of their money at different companies during
the course of each month, saving anything they have leftover. Companies have
to pay their expenses every month (in this model, the only expense is payroll).
They lay off some employees when they can't afford their expenses, going out of
business when they can no longer afford to pay any employees at all. On the other
hand, they hire new employees when they can afford to. Each company also belongs
to an industry, and we can tweak the amount people spend in each industry. We run
this system for a fixed period of time. People and companies may build wealth,
scrape by, or collapse, according to this probabilistic model.

We're primarily interested in two things:

1. Understanding a "normal" economy: Under "normal" conditions, where does the
   money go (the distribution of wealth across people, companies, and
   industries), how does the unemployment rate look, and how many businesses
   close down? Is there an equilibrium? Which variables affect this outcome
   (e.g. number of companies, income distribution, etc.)?
2. The effects of a shutdown (e.g. during the [COVID-19 pandemic](https://www.wsj.com/graphics/march-changed-everything/)).
   During this pandemic, many governments have shut down or hampered large
   sectors of their economy, and there are raging debates over whether and how
   to correct for the consequences ([stimulus checks & unemployment benefits](https://www.economist.com/united-states/2020/05/16/inefficiencies-bedevil-americas-response-to-soaring-joblessness),
   [loans for small businesses](https://nymag.com/intelligencer/2020/04/the-small-business-loan-programs-big-problems-explained.html), etc.).
   In this model, we're interested in the effects of certain government actions
   on unemployment and the survival of businesses. What happens if consumers are
   temporarily blocked from spending in certain industries? What happens if we
   grant people and companies "stimulus checks" to compensate for lost income
   and lost revenue during that time? What happens if we tweak the unemployment
   benefits?

### Simulation algorithm

Initialization:

- Each company is assigned an industry and a number of employees from a
  distribution
- Each person is assigned income and an initial spending rate for the first
  month, both from a distribution
- Both people and companies get a specified number of months' worth of money
  (income for people, payroll expenses for companies)

Each day:

- Each person picks an industry to spend in from a distribution, and picks a
  random company within that industry. They spend 1/30 of their monthly
  spending to that company (this model has 30 days per month).

At the end of each month:

- Companies rehire unemployed people if they can afford them, and pay their
  employees 1 month's income. If they can't afford payroll, they pick random
  employees to lay off until they can. They also get a stimulus/tax if
  applicable.
- People pick a new spending rate for the next month, and get a stimulus/tax
  and/or unemployment benefits if applicable.

## Running a simulation

The simulator has both a publicly available web app at
<https://economy-simulator.herokuapp.com>, and a command-line app you can run
locally. You can use either to run simulations. Generally the web app is easier,
but you may find the command-line version more useful to automate many
simulations with different variables.

### Inputs

The simulation lets you specify a number of parameters for the economy. Some of
these are distributions, which specify *values* and a corresponding
*probability* that each value is selected. First you need to set the base
parameters, which apply for the entire simulation:

- **Number of companies**
- **Income levels**: a distribution of people's annual income. Each
  employed person receives an equal portion (1/12) of their annual income each
  month.
- **Company size**: a distribution of companies' size (the number of employees
  they have). For example, you could say that 1/3 of companies have 100
  employees, and 1/3 have 1,000, and 1/3 have 10,000.

Then you specify a number of *periods* - a limited duration for which certain
parameters apply. The periods run in the order listed, and each has the
following parameters. All parameters must be set in the first period, but after
that, if a parameter is not set in a particular period, the previous
value is used.

- **Duration**: the duration of the period, in months
- **Stimulus/tax for people**: the fraction of each person's monthly income that's
  granted to them as "stimulus" for this period. In the first period, this is
  the amount of money people will start the simulation with (e.g. 1 month's
  income), and in later periods, this can simulate stimulus checks. You can also
  set a negative value, which would take money away from people, simulating a tax.
- **Stimulus/tax for companies**: analogous number for companies, as a fraction of
  their monthly expenses.
- **Unemployment benefit**: a stimulus that's granted each month, only to
  *unemployed* people. Also specified as a fraction of monthly income.
- **Rehire rate**: the probability that an unemployed person is rehired when an
  opening comes up.
- **Inclination to spend**: the average percentage of their money that each
  person will spend each month. For example, setting this to 50% means that
  people will, on average, spend 50% of their money each month. The actual
  percentage that each person spends is different each month, drawn uniformly
  from a subrange between 0 and 1, pushed toward one end so that it centers at
  this number.
- **Spending distribution across industries**: the distribution of which
  industries people will spend their money in. For example, if you had 5
  industries, 4 that each have 25% probability, and 1 with 0%, this would
  simulate the effect of blocking spending in a particular industry (e.g. if
  it's temporarily shut down).

The web app has boxes where you can set each of these parameters. For the CLI,
you'll need to write a config file that sets these parameters. See the
[developer guide](docs/dev_guide.md#config) for the spec of the config and an
example that you can copy/paste into a file, e.g. config.json. Then you can run
the simulation with:

```bash
cd cli
python app.py --config=config.json
```

This will produce a bunch of charts in a directory called output/, showing the
results. Use the `--help` flag for more details on command-line options.

### Outputs

Running a simulation produces 5 main charts:

- Distribution of money across people
- Distribution of money across companies
- Unemployment rate
- Business closure rate
- Total money in circulation

The distributions are represented with multiple lines showing various
percentiles.

The first 4 charts are shown at 3 different levels: over the entire economy,
broken down by income level, and broken down by industry.

That's it! Have fun playing around with the parameters!

---

Copyright 2020, Michael Friedman
