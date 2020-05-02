'''
The simulator.
'''

from tqdm import tqdm
import numpy as np

months_per_year = 12
days_per_month = 30

# A person in the model
class Person:

  def __init__(self, money=0, income=0, employed=True, spending_rate=0):
    self.money = money
    self.income = income
    self.employed = employed
    self.spending_rate = spending_rate

  def __str__(self):
    return ('Person(money=%.2f, income=%.2f, employed=%s)'
      % (self.money, self.income, str(self.employed)))

# A company in the model
class Company:

  def __init__(self, money=0, employees=[], in_business=True):
    self.money = money
    self.employees = employees
    self.in_business = in_business

  def __str__(self):
    return ('Company(money=%.2f, in_business=%s employees=%s)'
      % (self.money, str(self.in_business), str([str(e) for e in self.employees])))

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
def init(npersons, ncompanies, income, spending_dist):
  # Assign each person income from the distribution
  incomes = np.random.choice(income[0], p=income[1], size=npersons)
  people = [
    Person(
      money=incomes[i]/months_per_year, # 1 month income
      income=incomes[i]
    ) for i in range(npersons)
  ]
  people = reset_spending_rates(people, spending_dist)

  companies = [Company() for i in range(ncompanies)]
  people_per_company = int(npersons / ncompanies)
  extra = npersons % ncompanies
  for i in range(ncompanies): # assign people to companies
    companies[i].employees = people[i*people_per_company:(i+1)*people_per_company]
    if i < extra:
      companies[i].employees.append(people[len(people)-1-i]) # add one extra
    companies[i].money = np.sum([e.income / months_per_year
      for e in companies[i].employees]) # 1 months' worth of payroll
  return people, companies

# Given the list of people and companies, each person spends a portion of their
# monthly spending money at a random company. Returns the new list of people
# and companies.
def spend(people, companies):
  in_business = [c for c in companies if c.in_business]
  if len(in_business) != 0:
    random_companies = np.random.choice(in_business, len(people))
    for p, c in zip(people, random_companies):
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

# Calculates statistics based on the current state of the model. Returns 3
# values:
# - person_wealth: a list of every percentile of the wealth distribution across
#   people
# - company_wealth: an analogous list for companies
# - unemployment: the current unemployment rate
# - out_of_business: the current fraction of companies out of business
def calculate_stats(people, companies):
  person_wealth_data = [p.money for p in people]
  company_wealth_data = [c.money for c in companies]

  percentiles = range(0, 101)
  person_wealth = list(np.percentile(person_wealth_data, percentiles))
  company_wealth = list(np.percentile(company_wealth_data, percentiles))

  unemployment = np.sum([1 for p in people if not p.employed]) / len(people)
  out_of_business = np.sum([1 for c in companies if not c.in_business]) / len(companies)
  return person_wealth, company_wealth, unemployment, out_of_business

# Runs the simulator, given parameters:
# - npersons (int): the number of people in the model
# - ncompanies (int): the number of companies in the model
# - ndays (int): the number of days to run for
# - income (2d list of floats): the distribution of people's annual income.
#   Specified as two parallel arrays: the first lists the income amounts, and
#   the second lists the probability of each amount being chosen for a person.
# - spending (2d list of floats): the distribution of people's spending rates.
#   Analogous to income, but the first list consists of [low, high] pairs
#   representing the range of rates to choose from.
# - rehire_rate (float): the probability of an unemployed person being rehired
#   when an opportunity arises
#
# Returns a dict of results:
# - person_wealth: a list of stats, one for each day, where each day is a list
#   of every percentile of the wealth distribution across people
# - company_wealth: an analogous list for company wealth
# - unemployment: a list of unemployment rates, one for each day
# - out_of_business: a list of out-of-business rates (fraction of companies
#   out of business), one for each day
def run(
  npersons=0,
  ncompanies=0,
  ndays=0,
  income=[[65000], [1.0]],
  spending=[[[0, 1]], [1]],
  rehire_rate=1.0
  ):

  # Set up simulation
  people, companies = init(npersons, ncompanies, income, spending)

  # Run simluation
  pw, cw, u, oob = calculate_stats(people, companies)
  person_wealth = [pw]
  company_wealth = [cw]
  unemployment = [u]
  out_of_business = [oob]
  for i in tqdm(range(ndays)):
    # Each person spends at a random company
    people, companies = spend(people, companies)

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
    pw, cw, u, oob = calculate_stats(people, companies)
    person_wealth.append(pw)
    company_wealth.append(cw)
    unemployment.append(u)
    out_of_business.append(oob)

  return {
    'person_wealth': person_wealth,
    'company_wealth': company_wealth,
    'unemployment': unemployment,
    'out_of_business': out_of_business
  }
