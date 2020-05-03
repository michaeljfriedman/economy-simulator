# Economy Simulation Design

## High level summary

In this project, we create a simplified model of the economy as what (we
believe) it is fundamentally: a network of circulating money, and to measure
the distribution of wealth across people and companies, and the unemployment
rate.

The basic model works like this. There are two kinds of entities: *people* and
*companies*. Each person works for a company, and receives fixed income from it
each month. They spend a portion of their wealth at different companies during
the course of each month, saving anything they have leftover. Companies lay off
employees when they can no longer afford to pay them, hire new ones if they can
afford to, and go out of business when they have no more employees. We run this
system for a fixed period of time. People and companies may build wealth,
scrape by, or collapse, according to this probabilistic model.

We're primarily interested in two things:

1. Understanding a "normal" economy: Under "normal" conditions, where does the
   money go (the distribution of wealth across people and companies), how does
   the unemployment rate look, and how does company survival rate look (do some
   companies die out)? Is there an equilibrium? Which variables affect this
   outcome (e.g. size of the economy, income distribution, etc.)?
2. The effects of a shutdown (e.g. during a pandemic): What happens if consumers
   are temporarily blocked from spending in certain areas?

## Version 1: Basic model

Fixed parameters:

- Number of people
- Number of companies
- Income per person

Random variables:

- How much money people spend each month
- Which companies people spend their money at

Simulation:

- Initialization:
  - Each person is assigned to a company (people are divided among companies
    evenly), and gets 1 month income
  - Each company gets money to cover 1 month's worth of payroll
- Each day:
  - Each person picks a random company and spends 1/30 of their monthly
    spending to that company
  - If it's a company's pay day, they pay their employees 1 month's income. If
    they don't have enough money to cover it, they pick a random person to lay
    off until they do. If they run out of employees, they go out of business
    (removed from the economy).

## Version 2: Adds rehiring

Fixed parameters:

- Parameters from v1
- People are always rehired when an opportunity arises

Random variables:

- Parameters from v1

Simulation:

- Add: each month, unemployed people are rehired if a company can afford them,
  and are distributed evenly among companies.

## Version 3: Adds variable income

Income is specified as a distribution - for instance, 25% of people make
25k, 25% make 65k, 25% make 100k and 25% make 250k. This generalizes the
constant income case that's currently implemented.

## Config format

The config is a JSON object with the following parameters. Distributions are
specified as 2 parallel arrays in a 2d array: the first lists the values, and
the second lists the probability that each value is selected.

- `npersons` (int): the number of people in the model
- `ncompanies` (int): the number of companies in the model
- `ndays` (int): how many days to run the simulation for (note there are 30 days
  in each month in this model)
- `income` (distribution): the distribution of people's annual income. An
  employed person receives an equal fraction of their income this each month
  (12 months in each year).
- `spending` (distribution): the distribution of people's spending rates. A
  person picks a spending rate (a fraction of their money) from this
  distribution each month, and spends that much that month. This one is treated
  slightly differently. Each value in the first array should be a pair
  [low, high] indicating the range of rates a person can choose from. People
  pick a *range* according to the distribution, and then choose a value
  uniformly within that range. So in the example below, people have a 50%
  chance of choosing a rate in [0, 0.25], and 50% chance in [0.25, 1] (i.e.
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
- `rehire_rate` (float): the probability that an unemployed is rehired when
  an opportunity arises.

Example:

```json
{
  "npersons": 10000,
  "ncompanies": 100,
  "ndays": 360,
  "income": [
    [25000, 65000, 100000, 250000],
    [0.25, 0.25, 0.25, 0.25]
  ],
  "spending": [
    [[0, 0.25], [0.25, 1]],
    [0.5, 0.5]
  ],
  "initial_money": [
    [1, 2],
    [0.5, 0.5]
  ],
  "rehire_rate": 1.0
}
```
