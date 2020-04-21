# Economy Simulation Design

## High level summary

In this project, we create a simplified model of the economy as what (we
believe) it is fundamentally: a network of circulating money.

There are two kinds of entities in our model: *people* and *companies*.
Companies are distributed across a set of *industries* (e.g. restaurants,
groceries, entertainment, housing, etc.). Each person receives fixed income from
a company each month, and spends their money according to a distribution across
industries. They save any money they have leftover after expenses. Similarly,
each company has a set of expenses according to a distribution across
industries, and additionally they have a set of employees whose income they pay
each month. They also save any excess money.

Companies will lay off employees when they can no longer afford to pay them, and
people "die" (drop out of the network) when they can no longer afford to pay
their expenses.

All distributions are derived from real data in the US from the Bureau of Labor
Statistics. e.g. We calculate an income distribution per industry based on
the income distributions in each industry from 2019 BLS data.

We run this system for a fixed period of time. People and companies may build
wealth, scrape by, or collapse, according to this probabilistic model. At the
end, we report: the wealth distribution, the unemployment rate, and the death
rate, across people, industries, etc.

## Implementation details

Person:

- Money (int): amount they have
- Income (int): amount of money they receive each year (if 0, unemployed)
- Expenses (list of (industry, int) pairs): amount of money to pay each company
  each year
- Living status (bool)

Company:

- Money (int): amount they have
- Industry (enum)
- Employees (list of persons)
- Expenses (list of (company, amount) pairs): amount of money to pay each
  company each year
- In-business status (bool)

Simulator:

- Read in data:
  - Distribution of % companies in each industry
  - Distribution of % workers in each industry
  - Industries. For each, distributions of: income, expenses
  - Income brackets. For each, distribution of expenses
- Read in config: # people, # companies, how long to run, the data files to use, etc
- Initialize:
  - Create # companies. For each:
    - Pick an industry from the distribution: # companies in each industry.
      Assign to that industry
    - Assign a distribution of expenses from the distribution: expenses in that
      industry -> (industry, amount). Pick a company uniformly at random from
      each industry to give each amount to.
  - Create # people. For each:
    - Pick an industry from the distribution: # workers in each industry.
    - Assign to a company uniformly at random within that industry
    - Assign an income chosen from the distribution: income in that industry
    - Assign a distribution of expenses from the distribution: expenses in that
      income bracket -> (industry, amount).
  - Give everyone 1 month's worth of money:
    - For people: 1 month income
    - For companies: 1 month expenses + payroll
- Run simulation:
  - Each day:
    - Each person pays 1/360 of their expenses. For each expense, pick a company
      uniformly at random in that industry to pay. If they can't afford to pay,
      they die.
    - Each company: Pays 1/360 of their expenses. If they can't afford to pay,
      they lay off all employees and go out of business.
  - Every 30 days:
    - Each company: Pays their employees 1/12 of their income. If they can't
      afford to pay, they lay off employees[^layoffs] until they have enough.
      If they run out of employees, they go out of business.

[^layoffs]: Each employee to lay off is chosen by selecting an income from the
income distribution of that industry, and then selecting the employee with the
income closest to that (if multiple, pick one uniformly at random).
