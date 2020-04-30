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

## Config format

The config is a JSON object with the parameters:

- `npersons` (int): the number of people in the model
- `ncompanies` (int): the number of companies in the model
- `ndays` (int): how many days to run the simulation for (note there are 30 days
  in each month in this model)
- `income` (int): annual income of each person in the model. An employed person
  receives an equal amount of this each month (there are 12 months in each year
  in this model)
- `rehire_rate` (float): the probability that an unemployed is rehired when
  an opportunity arises.

Example:

```json
{
  "npersons": 10000,
  "ncompanies": 100,
  "ndays": 360,
  "income": 65000,
  "rehire_rate": 1.0
}
```
