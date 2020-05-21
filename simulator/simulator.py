'''
The simulator.
'''

import numpy as np

months_per_year = 12
days_per_month = 30
defaults = {
  'ncompanies': 10,
  'income': [
    [65000],
    [1]
  ],
  'company_size': [
    [10],
    [1]
  ],
  'periods': [
    {
      'duration': 360,
      'person_stimulus': 1,
      'company_stimulus': 1,
      'unemployment_benefit': 0,
      'rehire_rate': 1,
      'spending_inclination': 0.5,
      'industries': [
        ['whole_economy'],
        [1]
      ],
    }
  ]
}

# A person in the model
class Person:

  def __init__(self, money=0, income=0, employed=True, spending_rate=0, industry='economy'):
    self.money = money
    self.income = income # income *per month* (not annual)
    self.employed = employed
    self.spending_rate = spending_rate
    self.industry = industry

  def __str__(self):
    return ('Person(money=%.2f, income=%.2f, employed=%s, industry="%s")'
      % (self.money, self.income, str(self.employed), self.industry))

# A company in the model
class Company:

  def __init__(self, money=0, employees=[], in_business=True, industry='economy'):
    self.money = money
    self.employees = employees
    self.in_business = in_business
    self.industry = industry

  def __str__(self):
    return ('Company(money=%.2f, in_business=%s, industry="%s", employees=%s)'
      % (self.money, str(self.in_business), self.industry, str([str(e) for e in self.employees])))

# Picks a new spending rate for each person given the spending inclination.
# This function derives the uniform distribution to draw rates from, as
# described in the README. Returns the new list of people.
def reset_spending_rates(people, spending_inclination):
  lo = 0
  hi = 1
  diff = spending_inclination - 0.5
  if diff > 0:
    lo += 2 * diff
  else:
    hi += 2 * diff # remember diff is negative
  rands = np.random.rand(len(people)) # random numbers used to pick a spending rate for each person
  for i in range(len(people)):
    people[i].spending_rate = lo + rands[i] * (hi - lo)
  return people

# Initializes the simulator. Returns the list of people and companies
def init(
  ncompanies=defaults['ncompanies'],
  income=defaults['income'],
  company_size=defaults['company_size'],
  spending_inclination=defaults['periods'][0]['spending_inclination'],
  industry_names=defaults['periods'][0]['industries'][0]
  ):

  # Assign people to companies
  people = []
  companies = [Company(industry=industry_names[i % len(industry_names)]) for i in range(ncompanies)]
  size = np.random.choice(company_size[0], p=company_size[1], size=len(companies))
  for i in range(ncompanies):
    companies[i].employees = [Person(industry=companies[i].industry) for j in range(size[i])]
    people += companies[i].employees

  # Assign each person income and spending rates
  incomes = np.random.choice(income[0], p=income[1], size=len(people))
  for i in range(len(people)):
    people[i].income = incomes[i] / months_per_year
  people = reset_spending_rates(people, spending_inclination)
  return people, companies

# Grant stimulus for people and companies. Returns the new list of people and
# companies.
def grant_stimulus(people, companies, person_stimulus, company_stimulus):
  for p in people:
    p.money += person_stimulus * p.income

  for c in companies:
    payroll = np.sum([e.income for e in c.employees])
    c.money += company_stimulus * payroll

  return people, companies

# Grant the unemployment benefit to people. Returns the new list of people
def grant_unemployment(people, unemployment_benefit):
  for p in people:
    if not p.employed:
      p.money += unemployment_benefit * p.income
  return people

# Given the list of people, companies, and industries each person picks a random
# company within an industry chosen from the industry distribution, and spends a
# portion of their monthly spending at that company. Returns the new list of
# people and companies.
# - ind_companies: a dict {industry: [list of companies in business in that industry]}
def spend(people, companies, industries, ind_companies):
  in_business = [c for c in companies if c.in_business]
  if len(in_business) != 0:
    rand_inds = np.random.choice(industries[0], p=industries[1], size=len(people))
    rands = np.random.rand(len(people)) # random numbers used to pick a company for each person
    for p, rand_ind, r in zip(people, rand_inds, rands):
      ind = ind_companies[rand_ind]
      c = ind[int(r * len(ind))]
      amount = p.spending_rate * p.money / days_per_month
      p.money -= amount
      c.money += amount
  return people, companies

# Given the list of people and companies and the probability of rehiring,
# companies than can afford to hire unemployed people do so with that
# probability, giving each person an equally likely chance of being hired
# by any company. Returns the new list of people and companies.
def rehire_people(people, companies, rehire_rate):
  # Hire unemployed people
  unemployed = np.random.permutation([p for p in people if not p.employed])
  in_business = [c for c in companies if c.in_business]

  rehire = np.random.rand(len(unemployed)) <= rehire_rate # whether to rehire each person
  rands = np.random.rand(len(unemployed)) # rand numbers used to select the company that will hire this person

  # Build an array where entry (i, j) is whether company j can afford to hire person i
  cost_of_new_hire = np.array([p.income for p in unemployed])
  company_money = np.array([c.money for c in in_business])
  company_payroll = np.array([np.sum([e.income for e in c.employees]) for c in in_business])
  can_afford = np.outer(1/cost_of_new_hire, company_money - company_payroll) >= 1

  # Pick the company that will hire each person
  for i in range(len(unemployed)):
    if not rehire[i]:
      continue
    c_indices = np.argwhere(can_afford[i,:]) # indices of True values
    if c_indices.shape[0] == 0:
      continue
    r = int(rands[i] * c_indices.shape[0])
    c_index = c_indices[r,0] # random company among the True values
    c = in_business[c_index]
    c.employees.append(unemployed[i])
    unemployed[i].employed = True
    unemployed[i].industry = c.industry

  return people, companies

# Given the list of people and companies, companies lay off employees until
# they can afford to pay all of them. Returns the new list of people and
# companies.
def layoff_employees(people, companies):
  for c in companies:
    if not c.in_business:
      continue

    # Count number of people to lay off
    payroll = np.sum([e.income for e in c.employees])
    layoffs = np.random.permutation(c.employees) # order in which to lay off employees
    layoff_income = 0 # total income of laid off employees
    nlayoff = 0
    while True:
      if payroll - layoff_income <= c.money:
        break
      layoff_income += layoffs[nlayoff].income
      nlayoff += 1
      if nlayoff == len(c.employees):
        c.in_business = False
        break

    # Lay off those people
    for i in range(nlayoff):
      c.employees.remove(layoffs[i])
      layoffs[i].employed = False
  return people, companies

# Given the list of people and companies, each company pays their employees
# one month's income. Returns the new list of people and companies.
def pay_employees(people, companies):
  for c in companies:
    if not c.in_business:
      continue
    for e in c.employees:
      amount = e.income
      c.money -= amount
      e.money += amount
  return people, companies

# Runs the simulator, given the parameters as defined in design.md; and an
# optional callback function on_day, which is called at the start of each day,
# with the following arguments:
# - period: the index of the current period (from 0)
# - day: the index of the current day (from 0)
# - people: the list of people
# - companies: the list of companies
# The caller can use this to record data and/or report progress up a level.
#
# NOTE: Be mindful - these args are passed by reference, so you can technically
# change them and mess with the simulation. Please don't do that. Read only. I
# would have passed a copy instead, but it slows down the simulation a lot.
def run(
  ncompanies=defaults['ncompanies'],
  income=defaults['income'],
  company_size=defaults['company_size'],
  periods=defaults['periods'],
  on_day=lambda period, day, people, companies: None
  ):

  # Set up simulation
  industry_names = periods[0]['industries'][0]
  people, companies = init(
    ncompanies=ncompanies,
    company_size=company_size,
    income=income,
    spending_inclination=periods[0]['spending_inclination'],
    industry_names=industry_names
  )
  person_stimulus = None
  company_stimulus = None
  unemployment_benefit = None
  rehire_rate = None
  spending_inclination = None
  industries = None

  # Run simluation
  for i in range(len(periods)):
    # Set parameters for this period
    person_stimulus = person_stimulus if 'person_stimulus' not in periods[i] else periods[i]['person_stimulus']
    company_stimulus = company_stimulus if 'company_stimulus' not in periods[i] else periods[i]['company_stimulus']
    unemployment_benefit = unemployment_benefit if 'unemployment_benefit' not in periods[i] else periods[i]['unemployment_benefit']
    rehire_rate = rehire_rate if 'rehire_rate' not in periods[i] else periods[i]['rehire_rate']
    spending_inclination = spending_inclination if 'spending_inclination' not in periods[i] else periods[i]['spending_inclination']
    industries = industries if 'industries' not in periods[i] else periods[i]['industries']

    # Grant stimulus/unemployment benefits for this period
    people, companies = grant_stimulus(people, companies, person_stimulus, company_stimulus)

    # Run the period
    for j in range(periods[i]['duration']):
      on_day(i, j, people, companies)

      ind_companies = {
        ind: [c for c in companies if c.in_business and c.industry == ind]
        for ind in industries[0]
      }
      people, companies = spend(people, companies, industries, ind_companies)

      # At the end of the month, companies hire new employees and pay their
      # employees
      if j % days_per_month == days_per_month - 1:
        people, companies = rehire_people(people, companies, rehire_rate)
        people, companies = layoff_employees(people, companies)
        people, companies = pay_employees(people, companies)

        # Grant unemployment benefits
        people = grant_unemployment(people, unemployment_benefit)

        # Reset people's spending rates
        people = reset_spending_rates(people, spending_inclination)
