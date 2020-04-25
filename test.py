import simulator
import sys

def test_initialization():
  print('Check that all people are assigned to a company')
  people, companies = simulator.init(109, 10, 0, 0)
  expected = [11] * 9 + [10]
  for p in people:
    present = False
    for c in companies:
      if p in c.employees:
        present = True
        break
    if not present:
      print('Failed: person not assigned to a company')
      print('Expected: %s' % str(expected))
      print('Actual:   %s' % str([len(c.employees) for c in companies]))
      return
  print('Passed')

def test_basic_one_day():
  print('Check that last-day results of a 1 day simulation are correct (1 person, 1 company, income 1200, saving rate 0.25)')
  results = simulator.run(
    npersons=1,
    ncompanies=1,
    ndays=1,
    income=1200,
    saving_rate=0.25
  )
  actual = {
    'person_wealth': results['person_wealth'][1],
    'company_wealth': results['company_wealth'][1],
    'unemployment': results['unemployment'][1]
  }
  spent = 75 / 30
  person_money = 100 - spent
  company_money = 1200 - 100 + spent
  expected = {
    'person_wealth': (person_money, person_money, person_money, person_money, person_money, person_money, person_money),
    'company_wealth': (company_money, company_money, company_money, company_money, company_money, company_money, company_money),
    'unemployment': 0
  }
  for key in ['person_wealth', 'company_wealth', 'unemployment']:
    if actual[key] != expected[key]:
      print('Failed: Result %s was wrong' % key)
      print('Expected: %s' % str(expected[key]))
      print('Actual:   %s' % str(actual[key]))
      return
  print('Passed')

def test_basic_30_days():
  print('Check that the last-day results of a 30 day simulation (1 pay cycle) are correct (1 person, 1 company, income 1200, saving rate 0.25)')
  results = simulator.run(
    npersons=1,
    ncompanies=1,
    ndays=30,
    income=1200,
    saving_rate=0.25
  )
  spent = 75
  person_money = 100 - spent
  company_money = 1200 - 100 + spent
  actual = {
    'person_wealth': results['person_wealth'][30],
    'company_wealth': results['company_wealth'][30],
    'unemployment': results['unemployment'][30]
  }
  expected = {
    'person_wealth': (person_money, person_money, person_money, person_money, person_money, person_money, person_money),
    'company_wealth': (company_money, company_money, company_money, company_money, company_money, company_money, company_money),
    'unemployment': 0
  }
  for key in ['person_wealth', 'company_wealth', 'unemployment']:
    if actual[key] != expected[key]:
      print('Failed: Result %s was wrong' % key)
      print('Expected: %s' % str(expected[key]))
      print('Actual:   %s' % str(actual[key]))
      print(results)
      return
  print('Passed')

# Run all tests
def main():
  test_initialization()
  test_basic_one_day()
  test_basic_30_days()

if __name__ == '__main__':
  main()
