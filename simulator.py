'''
The simulator.
'''

import numpy as np

# Runs the simulator, given parameters:
# - npersons: the number of people in the model
# - ncompanies: the number of companies in the model
# - ndays: the number of days to run for
# - dcompanies: the distribution of companies across industries
# - demployees: the distribution of employees across industries
# - dincome: the distributions of income in each industry
# - dcompany_expenses: the distributions of company expenses in each industry
# - dperson_expenses: the distributions of person expenses in each income bracket
#
# Returns a 2-tuple: (success, results), where `successs` is a boolean
# indicating whether the run was successful, and `results` is a dict with the
# values:
# - err: an error message, if unsuccessful
# - dperson_wealth: ([wealth brackets], [% of persons in each wealth bracket])
# - dcompany_wealth: ([wealth bracket], [% of companies in each wealth bracket])
# - unemployment: the % of persons unemployed
# - death: the % of persons dead
# - unemployment_by_industry: {industry: % of persons unemployed in that industry}
# - death_by_industry: {industry: % of persons dead in that industry}
def run(
  npersons=0,
  ncompanies=0,
  ndays=0,
  dcompanies=(,), # 2-tuple ([industries], [% of companies in each industry])
  demployees=(,), # 2-tuple ([industries], [% of employees in each industry])
  dincome={}, # map {industry: ([salaries], [% of employees with each salary])}
  dcompany_expenses={}, # map {industry: ([other industries], [% of expenses paid to each industry])}
  dperson_expenses={}): # map {income range: ([industries], [% of expenses paid to each industry])}

  # Do some data validation
  industries = sorted(dcompanies[0])
  if sorted(demployees[0]) != industries:
    return False, {'err': 'Industries in demployees do not match'}
  if sorted(dincome.keys()) != industries:
    return False, {'err': 'Industries in dincome do not match'}
  if sorted(dcompany_expenses.keys()) != industries:
    return False, {'err': 'Industries in dcompany_expenses do not match'}
  for _, d in dperson_expenses.items():
    test_industries, _ = d
    if sorted(test_industries) != industries:
      return False, {'err': 'Industries in dperson_expenses do not match'}

  # Set up simulation
  # TODO

  # Run simulation
  for i in range(ndays):
    # TODO: people pay expenses

    # Companies pay expenses
    for c in companies:
      if not c.in_business:
        continue

      for other_c, amount in c.expenses:
        pay = amount / 360
        if pay > c.money:
          # Go out of business
          for e in c.employees:
            e.income = 0
          c.employees = []
          c.in_business = False
          break
        other_c.money += amount / 360

    # TODO: Pay employees their income at the end of each month

  # TODO: Compute results
  return True, {'err': ''}
