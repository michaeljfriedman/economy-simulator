# Economy Simulation Design

Person:

- Money (int): amount of money they have
- Income (int): amount of money they receive each month (if 0, unemployed)
- Expenses (list of (company, int) pairs): amount of money to pay each company each day
- Living status (bool)

Company:

- Money (int): amount of money they have
- Industry (enum)
- Employees (list of persons)
- Expenses (list of (company, amount) pairs): amount of money to pay each company each day

Simulator:

- Read in data
- Read in config: # people, # companies, how long to run, etc
- Initialize:
  - Create # companies. For each:
    - Pick an industry from the distribution: # companies in each industry. Assign to that industry
    - Assign a distribution of expenses from the distribution: expenses in that industry -> (industry, amount). Pick a company uniformly at random from each industry to give each amount to.
  - Create # people. For each:
    - Pick an industry from the distribution: # workers in each industry.
    - Assign to a company uniformly at random within that industry
    - Assign an income chosen from the distribution: income in that industry
    - Assign a distribution of expenses from the distribution: expenses in that income bracket -> (industry, amount). Pick a company uniformly at random from each industry to give each amount to.
  - Give everyone 1 month's worth of money:
    - For people: 1 month income
    - For companies: 1 month expenses + payroll
- Run simulation (see notebook)
