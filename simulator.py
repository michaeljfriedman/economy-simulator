'''
The simulator.
'''

from tqdm import tqdm
import numpy as np

months_per_year = 12
days_per_month = 30
defaults = {
  'ncompanies': 10,
  'ndays': 0,
  'rehire_rate': 1,
  'income': [
    [65000],
    [1]
  ],
  'spending': [
    [[0, 1]],
    [1]
  ],
  'initial_money': [
    [1],
    [1]
  ],
  'employees': [
    [10],
    [1]
  ],
  'industry_selection': [
    ['economy'],
    [1]
  ]
}

# A person in the model
class Person:

  def __init__(self, money=0, income=0, employed=True, spending_rate=0, industry='economy'):
    self.money = money
    self.income = income
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

# Picks a new spending rate for each person from the spending distribution.
# Returns the new list of people.
def reset_spending_rates(people, spending_dist):
  rands = np.random.rand(len(people)) # random numbers used to pick a spending rate for each person
  ranges, probs = spending_dist
  ranges = [None] + ranges # add a dummy value
  probs = list(np.cumsum([0] + probs)) # convert to cumulative sum, which gives us ranges for rands
  for i in range(len(people)):
    for j in range(1, len(probs)):
      if probs[j-1] <= rands[i] < probs[j]:
        # Pick a value uniformly in the corresponding range
        lo, hi = ranges[j]
        people[i].spending_rate = lo + rands[i] * (hi - lo)
  return people

# Initializes the simulator. Returns the list of people and companies
def init(
  ncompanies=defaults['ncompanies'],
  income=defaults['income'],
  spending=defaults['spending'],
  initial_money=defaults['initial_money'],
  employees=defaults['employees'],
  industries=defaults['industry_selection'][0]
  ):

  # Assign people to companies
  people = []
  companies = [Company(industry=industries[i % len(industries)]) for i in range(ncompanies)]
  nemployees = np.random.choice(employees[0], p=employees[1], size=len(companies))
  for i in range(ncompanies):
    companies[i].employees = [Person(industry=companies[i].industry) for j in range(nemployees[i])]
    people += companies[i].employees

  # Assign each person income, initial money, and spending rates
  incomes = np.random.choice(income[0], p=income[1], size=len(people))
  people_months = np.random.choice(initial_money[0], p=initial_money[1], size=len(people))
  for i in range(len(people)):
    people[i].income = incomes[i]
    people[i].money = people_months[i] * people[i].income / months_per_year
  people = reset_spending_rates(people, spending)

  # Initialize company money
  company_months = np.random.choice(initial_money[0], p=initial_money[1], size=len(companies))
  for i in range(len(companies)):
    payroll = np.sum([e.income / months_per_year for e in companies[i].employees])
    companies[i].money = company_months[i] * payroll
  return people, companies

# Given the list of people, companies, and industries each person picks a random
# company within an industry chosen from the industry distribution, and spends a
# portion of their monthly spending at that company. Returns the new list of
# people and companies.
# - industries: a dict {industry: [list of companies in business in that industry]}
def spend(people, companies, industries, industry_selection):
  in_business = [c for c in companies if c.in_business]
  if len(in_business) != 0:
    rand_inds = np.random.choice(industry_selection[0], p=industry_selection[1], size=len(people))
    rands = np.random.rand(len(people)) # random numbers used to pick a company for each person
    for p, rand_ind, r in zip(people, rand_inds, rands):
      ind = industries[rand_ind]
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
  cost_of_new_hire = np.array([p.income / months_per_year for p in unemployed])
  company_money = np.array([c.money for c in in_business])
  company_payroll = np.array([np.sum([e.income / months_per_year for e in c.employees]) for c in in_business])
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
    layoff_order = np.random.permutation(c.employees)
    l = 0 # index of next employee to lay off
    while True:
      total_amount = np.sum([e.income / months_per_year for e in c.employees])
      if total_amount <= c.money:
        break
      layoff = layoff_order[l]
      l += 1
      c.employees.remove(layoff)
      layoff.employed = False
      if len(c.employees) == 0:
        c.in_business = False
        break
  return people, companies

# Given the list of people and companies, each company pays their employees
# one month's income. Returns the new list of people and companies.
def pay_employees(people, companies):
  for c in companies:
    if not c.in_business:
      continue
    for e in c.employees:
      amount = e.income / months_per_year
      c.money -= amount
      e.money += amount
  return people, companies

# Calculates statistics based on the current state of the model and adds them
# to the given results. Returns the new results.
def calculate_stats(results, people, companies):
  for ind, ind_results in results.items():
    ind_people = [p for p in people if p.industry == ind]
    ind_companies = [c for c in companies if c.industry == ind]
    percentiles = range(0, 101)
    new_results = {
      'person_wealth': list(np.percentile([p.money for p in ind_people], percentiles)),
      'company_wealth': list(np.percentile([c.money for c in ind_companies], percentiles)),
      'unemployment': len([p for p in ind_people if not p.employed]) / len(ind_people),
      'out_of_business': len([c for c in ind_companies if not c.in_business]) / len(ind_companies)
    }
    for k in ind_results.keys():
      ind_results[k].append(new_results[k])
  return results

# Runs the simulator, given parameters:
# - ncompanies (int): the number of companies in the model
# - ndays (int): the number of days to run for
# - rehire_rate (float): the probability of an unemployed person being rehired
#   when an opportunity arises
# - income (2d list of floats): the distribution of people's annual income.
#   Specified as two parallel arrays: the first lists the income amounts, and
#   the second lists the probability of each amount being chosen for a person.
# - spending (2d list of floats): the distribution of people's spending rates.
#   Analogous to income, but the first list consists of [low, high] pairs
#   representing the range of rates to choose from.
# - initial_money (2d list of floats): the distribution of initial money.
#   Lists the number of months' worth of income people start with / payroll
#   companies start with.
# - employees (2d list of floats): the distribution of employees assigned to
#   companies. Lists the possible number of employees a company will start with.
# - industry_selection (2d list of strings and floats): the distribution of
#   how likely a person is to spend in each industry. Lists the industries by
#   name, and the probabilities associated with each.
#
# Returns a dict of results. Each key is an industry name from
# industry_selection, and each value is a dict of:
# - person_wealth: a list of stats, one for each day, where each day is a list
#   of every percentile of the wealth distribution across people in that
#   industry.
# - company_wealth: an analogous list for company wealth
# - unemployment: a list of unemployment rates in that industry, one for each
#   day
# - out_of_business: a list of out-of-business rates (fraction of companies
#   in that industry that are out of business), one for each day
def run(
  ncompanies=defaults['ncompanies'],
  ndays=defaults['ndays'],
  rehire_rate=defaults['rehire_rate'],
  income=defaults['income'],
  spending=defaults['spending'],
  initial_money=defaults['initial_money'],
  employees=defaults['employees'],
  industry_selection=defaults["industry_selection"]
  ):

  # Set up simulation
  people, companies = init(
    ncompanies=ncompanies,
    income=income,
    spending=spending,
    initial_money=initial_money,
    employees=employees,
    industries=industry_selection[0]
  )

  # Run simluation
  results = {
    industry: {
      'person_wealth': [], 'company_wealth': [], 'unemployment': [], 'out_of_business': []
    } for industry in industry_selection[0]
  }
  results = calculate_stats(results, people, companies)
  for i in tqdm(range(ndays)):
    # Each person spends at a random company
    industries = {
      ind: [c for c in companies if c.in_business and c.industry == ind]
      for ind in industry_selection[0]
    }
    people, companies = spend(people, companies, industries, industry_selection)

    # At the end of the month, companies hire new employees and pay their
    # employees
    if i % days_per_month == days_per_month - 1:
      people, companies = rehire_people(people, companies, rehire_rate)

      # Company lays off employees until it can afford payroll
      people, companies = layoff_employees(people, companies)

      # Pay employees
      people, companies = pay_employees(people, companies)

      # Reset people's spending rates
      people = reset_spending_rates(people, spending)

    # Calculate stats
    results = calculate_stats(results, people, companies)

  return results
