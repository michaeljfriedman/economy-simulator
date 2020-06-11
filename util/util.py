'''
Helper functions for the web app and CLI.
'''

from simulator import simulator
import numpy as np

# Merges dicts
def merge(dicts):
  d0 = dicts[0]
  for d in dicts[1:]:
    d0.update(d)
  return d0

# Computes the results from a particular day of the simulation, given the list
# of people and companies from that day. Returns a dict you can see below, with
# the results as described in the docs.
def results(people, companies):
  # Computes people results
  def people_results(people, percentiles):
    person_money = [0] * len(percentiles) if len(people) == 0 else list(np.round(np.percentile([p.money for p in people], percentiles), 2))
    person_unemployment = [1] if len(people) == 0 else [np.mean([not p.employed for p in people])]
    return {
      'person_money': person_money,
      'person_unemployment': person_unemployment
    }

  # Computes company results
  def company_results(companies, percentiles):
    return {
      'company_money': list(np.round(np.percentile([c.money for c in companies], percentiles), 2)),
      'company_closures': [np.mean([not c.in_business for c in companies])]
    }

  # Compute all results
  percentiles = [0, 10, 25, 50, 75, 90, 100]
  income_levels = set([p.income for p in people])
  industries = set([c.industry for c in companies])
  return {
    'overall': merge([
      people_results(people, percentiles),
      company_results(companies, percentiles),
      {'circulation': [
        round(np.sum([p.money for p in people]) + np.sum([c.money for c in companies]), 2)
      ]}
    ]),
    'income_levels': {
      str(int(simulator.months_per_year * i)): people_results([p for p in people if p.income == i], percentiles)
      for i in income_levels
    },
    'industries': {
      i: merge([
        people_results([p for p in people if p.industry == i], percentiles),
        company_results([c for c in companies if c.industry == i], percentiles)
      ])
      for i in industries
    }
  }
