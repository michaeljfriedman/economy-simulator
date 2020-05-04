'''
The simulator.
'''

from tqdm import tqdm
import numpy as np

months_per_year = 12
days_per_month = 30
defaults = {
  'ncompanies': 10,
  'employees': [
    [10],
    [1]
  ],
  'income': [
    [65000],
    [1]
  ],
  'initial_money': [
    [1],
    [1]
  ],
  'periods': [
    {
      'ndays': 360,
      'rehire_rate': 1,
      'spending': [
        [[0, 1]],
        [1]
      ],
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

# Picks a new spending rate for each person from the spending distribution.
# Returns the new list of people.
def reset_spending_rates(people, spending_dist):
  range_idx = np.random.choice(range(len(spending_dist[0])), p=spending_dist[1], size=len(people))
  rands = np.random.rand(len(people)) # random numbers used to pick a spending rate for each person
  for i in range(len(people)):
    r = range_idx[i]
    lo, hi = spending_dist[0][r]
    people[i].spending_rate = lo + rands[i] * (hi - lo)
  return people

# Initializes the simulator. Returns the list of people and companies
def init(
  ncompanies=defaults['ncompanies'],
  employees=defaults['employees'],
  income=defaults['income'],
  initial_money=defaults['initial_money'],
  spending=defaults['periods'][0]['spending'],
  industry_names=defaults['periods'][0]['industries'][0]
  ):

  # Assign people to companies
  people = []
  companies = [Company(industry=industry_names[i % len(industry_names)]) for i in range(ncompanies)]
  nemployees = np.random.choice(employees[0], p=employees[1], size=len(companies))
  for i in range(ncompanies):
    companies[i].employees = [Person(industry=companies[i].industry) for j in range(nemployees[i])]
    people += companies[i].employees

  # Assign each person income, initial money, and spending rates
  incomes = np.random.choice(income[0], p=income[1], size=len(people))
  people_months = np.random.choice(initial_money[0], p=initial_money[1], size=len(people))
  for i in range(len(people)):
    people[i].income = incomes[i] / months_per_year
    people[i].money = people_months[i] * people[i].income
  people = reset_spending_rates(people, spending)

  # Initialize company money
  company_months = np.random.choice(initial_money[0], p=initial_money[1], size=len(companies))
  for i in range(len(companies)):
    payroll = np.sum([e.income for e in companies[i].employees])
    companies[i].money = company_months[i] * payroll
  return people, companies

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

# Runs the simulator, given the parameters as defined in design.md. Returns a
# dict of results. Each key is an industry name from industries, and each value
# is a dict of:
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
  income=defaults['income'],
  initial_money=defaults['initial_money'],
  employees=defaults['employees'],
  periods=defaults['periods']
  ):

  # Set up simulation
  industry_names = periods[0]['industries'][0]
  people, companies = init(
    ncompanies=ncompanies,
    employees=employees,
    income=income,
    initial_money=initial_money,
    spending=periods[0]['spending'],
    industry_names=industry_names
  )
  rehire_rate = None
  spending = None
  industries = None

  # Run simluation
  results = {
    industry: {
      'person_wealth': [], 'company_wealth': [], 'unemployment': [], 'out_of_business': []
    } for industry in industry_names
  }
  results = calculate_stats(results, people, companies)
  for i in range(len(periods)):
    print('Period %d/%d' % (i+1, len(periods)))

    # Set parameters for this period
    rehire_rate = rehire_rate if 'rehire_rate' not in periods[i] else periods[i]['rehire_rate']
    spending = spending if 'spending' not in periods[i] else periods[i]['spending']
    industries = industries if 'industries' not in periods[i] else periods[i]['industries']

    # Run the period
    for j in tqdm(range(periods[i]['ndays'])):
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

        # Reset people's spending rates
        people = reset_spending_rates(people, spending)

      results = calculate_stats(results, people, companies)

  return results
