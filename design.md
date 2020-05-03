# Economy Simulation Design

## High level summary

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

## Simulation details

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

## Config

The config is a JSON object with the following parameters. Distributions are
specified as 2 parallel arrays in a 2d array: the first lists the values, and
the second lists the probability that each value is selected.

- `ncompanies` (int): the number of companies in the model
- `ndays` (int): how many days to run the simulation for (note there are 30 days
  in each month in this model)
- `rehire_rate` (float): the probability that an unemployed is rehired when
  an opportunity arises.
- `income` (distribution): the distribution of people's annual income. An
  employed person receives an equal fraction of their income this each month
  (12 months in each year).
- `spending` (distribution): the distribution of people's spending rates. A
  person picks a spending rate (a fraction of their money) from this
  distribution each month, and spends that much that month. This one is treated
  slightly differently. Each value in the first array should be a pair
  [low, high] indicating the range of rates a person can choose from. People
  pick a *range* according to the distribution, and then choose a value
  uniformly within that range. So in the example below, people have a 25%
  chance of choosing a rate in [0, 0.5], and 75% chance in [0.5, 1] (i.e.
  a skewed distribution that gives people a tendency to spend more than save).
  As another example, a uniform distribution over [0, 1] would be represented as:

  ```json
  [
    [[0, 1]],
    [1]
  ]
  ```

- `initial_money` (distribution): the distribution of initial money. Specifies
  the number of months' worth of money people and companies start with. For
  people, it's X months' income; for companies, it's X months' payroll.
- `employees` (distribution): the distribution of the number of employees
  assigned to companies. For example, in the the config below, each company has
  a 50% chance of being assigned 10 employees, and a 50% chance of 20.
- `industry_selection` (distribution): the distribution of how likely a person
  is to spend money in a particular industry. For example, in the config below,
  a person is equally likely to spend at a company in industry 1 or industry 2.

Example:

```json
{
  "ncompanies": 100,
  "ndays": 360,
  "rehire_rate": 1.0,
  "income": [
    [25000, 65000, 100000, 250000],
    [0.25, 0.25, 0.25, 0.25]
  ],
  "spending": [
    [[0, 0.5], [0.5, 1]],
    [0.25, 0.75]
  ],
  "initial_money": [
    [1, 2],
    [0.5, 0.5]
  ],
  "employees": [
    [10, 20],
    [0.5, 0.5]
  ],
  "industry_selection": [
    ["industry 1", "industry 2"],
    [0.5, 0.5]
  ]
}
```
