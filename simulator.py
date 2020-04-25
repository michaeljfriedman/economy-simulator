'''
The simulator.
'''

import numpy as np

# A person in the model
class Person:

  def __init__(self, money=0, income=0, saving_rate=0.3, employed=True):
    self.money = money
    self.income = income
    self.saving_rate = saving_rate
    self.employed = employed

# A company in the model
class Company:

  def __init__(self, money=0, employees=[], in_business=True):
    self.money = money
    self.employees = employees
    self.in_business = in_business

# Runs the simulator, given parameters:
# - npersons (int): the number of people in the model
# - ncompanies (int): the number of companies in the model
# - ndays (int): the number of days to run for
# - income (int): annual income to apply to all people
# - saving_rate (int): the saving rate to apply to all people
#
# Returns a dict of results:
# - person_wealth: a list of (min, p10, p25, p50, p75, p90, max) tuples, one for
#   each day, representing the wealth distribution across people
# - company_wealth: an analogous list for company wealth
# - unemployment: a list of unemployment rates, one for each day
def run(
  npersons=0,
  ncompanies=0,
  ndays=0,
  income=65000,
  saving_rate=0.3
  ):

  # Set up simulation
  people = [
    Person(
      money=income/12,
      income=income,
      saving_rate=saving_rate
    ) for i in range(npersons)
  ]
  companies = [Company() for i in range(ncompanies)]
  people_per_company = int(npersons / ncompanies)
  extra = npersons % ncompanies
  for i in range(ncompanies): # assign people to companies
    companies[i].employees = people[i*people_per_company:(i+1)*people_per_company]
    if i < extra:
      companies[i].employees.append(people[len(people)-1-i]) # add one extra
