# Economy Simulation Design

## High level summary

In this project, we create a simplified model of the economy as what (we
believe) it is fundamentally: a network of circulating money, and to measure
the distribution of wealth across people and companies, and the unemployment
rate.

The basic model works like this. There are two kinds of entities: *people* and
*companies*. Each person works for a company, and receives fixed income from it
each month. They spend a portion of their income at different companies during
the course of each month, saving if they have any leftover. Companies lay off
employees when they can no longer afford to pay them, and go out of business
when they have no more employees. We run this system for a fixed period of time.
People and companies may build wealth, scrape by, or collapse, according to this
probabilistic model.

Future versions will tweak/add other parameters, but this is the foundation.
Some examples:

- People have different income levels
- People have different spending/saving rates
- Companies have expenses other than payroll, paying other companies
- Unemployed people can be rehired
- Companies are distributed across different *industries* (e.g. restaurants,
  housing, entertainment, etc.). Spending (by people and companies) happens
  across different industries
- People and companies vary how much they spend depending on the industry
- People and companies have a pre-determined set of expenses (rather than a
  general spending/savings rate), which they have to pay even when they're
  unemployed
- After some time, spending is blocked in certain industries (e.g. like in an
  shutdown in response to a pandemic)

## Version 1: Basic model

Key points:

- Everyone makes the same amount of money, and spends at the same rate
- Variable: *which companies* people spend their money to

Fixed parameters:

- Number of people
- Number of companies
- Income per person
- Spending vs saving rate per person

Simulation:

- Initialization:
  - Each person is assigned to a company (people are divided among companies
    evenly)
  - Each company gets money to cover 1 year's worth of payroll
- Every month (30 days):
  - Each company pays each of their employees 1 month's income. If they don't
    have enough money to cover it, they pick a random person to lay off until
    they do. If they run out of employees, they go out of business (removed from
    the economy).
- Each day:
  - Each person picks a random company and spends 1/30 of their monthly
    spending to that company

## Config format

The config is a JSON object with the parameters:

- `npersons` (int): the number of people in the model
- `ncompanies` (int): the number of companies in the model
- `ndays` (int): how many days to run the simulation for (note there are 30 days
  in each month in this model)
- `income` (int): annual income of each person in the model. An employed person
  receives an equal amount of this each month (there are 12 months in each year
  in this model)
- `spending_range` (array of floats): a 2-element array [min_fraction,
  max_fraction] representing the range of their income people may spend each
  month. A value from this range is chosen uniformly at random each month for
  each person.

Example:

```json
{
  "npersons": 10000,
  "ncompanies": 100,
  "ndays": 360,
  "income": 65000,
  "spending_range": [0.75, 1.25]
}
```
