'''
The simulator.
'''

from tqdm import tqdm
import numpy as np

months_per_year = 12
days_per_month = 30

# A person in the model
class Person:

  def __init__(self, money=0, income=0, spending_range=[0.7, 1.3], employed=True):
    self.money = money
    self.income = income
    self.spending_range = spending_range
    self.employed = employed
    self.reset_spending_rate() # the current spending rate this month

  def reset_spending_rate(self):
    low, high = self.spending_range
    self.spending_rate = np.random.uniform(low=low, high=high)

# A company in the model
class Company:

  def __init__(self, money=0, employees=[], in_business=True, pay_day=None):
    self.money = money
    self.employees = employees
    self.in_business = in_business
    if pay_day == None:
      self.pay_day = np.random.randint(days_per_month)
    else:
      self.pay_day = pay_day

# Initializes the simulator. Returns the list of people and companies
def init(npersons, ncompanies, income, spending_range):
  people = [
    Person(
      money=income/4, # 3 months' income
      income=income,
      spending_range=spending_range
    ) for i in range(npersons)
  ]
  companies = [Company() for i in range(ncompanies)]
  people_per_company = int(npersons / ncompanies)
  extra = npersons % ncompanies
  for i in range(ncompanies): # assign people to companies
    companies[i].employees = people[i*people_per_company:(i+1)*people_per_company]
    if i < extra:
      companies[i].employees.append(people[len(people)-1-i]) # add one extra
    companies[i].money = np.sum([3 * e.income / months_per_year
      for e in companies[i].employees]) # 3 months' worth of payroll
  return people, companies

# Calculates statistics based on the current state of the model. Returns 3
# values:
# - person_wealth: a list [min, p10, p25, p50, p75, p90, max] representing
#   the wealth distribution across people
# - company_wealth: an analogous list for companies
# - unemployment: the current unemployment rate
def calculate_stats(people, companies):
  person_wealth_data = [p.money for p in people]
  company_wealth_data = [c.money for c in companies]

  person_wealth = [
    np.min(person_wealth_data),
    np.percentile(person_wealth_data, 10),
    np.percentile(person_wealth_data, 25),
    np.percentile(person_wealth_data, 50),
    np.percentile(person_wealth_data, 75),
    np.percentile(person_wealth_data, 90),
    np.max(person_wealth_data)
  ]

  company_wealth = [
    np.min(company_wealth_data),
    np.percentile(company_wealth_data, 10),
    np.percentile(company_wealth_data, 25),
    np.percentile(company_wealth_data, 50),
    np.percentile(company_wealth_data, 75),
    np.percentile(company_wealth_data, 90),
    np.max(company_wealth_data)
  ]

  unemployment = np.sum([1 for p in people if not p.employed]) / len(people)
  return person_wealth, company_wealth, unemployment

# Runs the simulator, given parameters:
# - npersons (int): the number of people in the model
# - ncompanies (int): the number of companies in the model
# - ndays (int): the number of days to run for
# - income (int): annual income to apply to all people
# - spending_range (list of floats): a list [min_fraction, max_fraction]
#   representing the range of their income people may spend each month. A value
#   from this range is chosen uniformly at random each month for each person.
#
# Returns a dict of results:
# - person_wealth: a list of [min, p10, p25, p50, p75, p90, max] lists, one for
#   each day, representing the wealth distribution across people
# - company_wealth: an analogous list for company wealth
# - unemployment: a list of unemployment rates, one for each day
def run(
  npersons=0,
  ncompanies=0,
  ndays=0,
  income=65000,
  spending_range=[0.7, 1.3]
  ):

  # Set up simulation
  people, companies = init(npersons, ncompanies, income, spending_range)

  # Run simluation
  pw, cw, u = calculate_stats(people, companies)
  person_wealth = [pw]
  company_wealth = [cw]
  unemployment = [u]
  for i in tqdm(range(ndays)):
    # Each person spends at a random company
    in_business = [c for c in companies if c.in_business]
    if len(in_business) != 0:
      random_companies = np.random.choice(in_business, len(people))
      for p, c in zip(people, random_companies):
        if not p.employed:
          continue

        amount = np.min([
          p.spending_rate * p.income / (days_per_month * months_per_year),
          p.money
        ])
        p.money -= amount
        c.money += amount

    # Companies pay their employees if it's their pay day
    for c in companies:
      if not c.in_business:
        continue

      if i % days_per_month != c.pay_day:
        continue

      # Company lays off employees until it can afford payroll
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

      for e in c.employees:
        amount = e.income / months_per_year
        c.money -= amount
        e.money += amount
        e.reset_spending_rate()

    # Calculate stats
    pw, cw, u = calculate_stats(people, companies)
    person_wealth.append(pw)
    company_wealth.append(cw)
    unemployment.append(u)

  return {
    'person_wealth': person_wealth,
    'company_wealth': company_wealth,
    'unemployment': unemployment
  }
