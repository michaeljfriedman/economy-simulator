import simulator
import sys

def test_init_people_assigned_to_companies():
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

def test_init_money():
  print('Check that all people and companies start with the right amount of money')
  income = 1200
  expected_people_money = income / 4
  expected_company_money = 10 * income / 4
  people, companies = simulator.init(100, 10, income, 0)
  for p in people:
    if p.money != expected_people_money:
      print('Failed: person has wrong amount of money')
      print('Expected: %.2f' % expected_people_money)
      print('Actual:   %.2f' % p.money)
      return
  for c in companies:
    if c.money != expected_company_money:
      print('Failed: company has wrong amount of money')
      print('Expected: %.2f' % expected_company_money)
      print ('Actual:  %.2f' % c.money)
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
  person_money = 300 - spent
  company_money = 300 + spent
  expected = {
    'person_wealth': [person_money, person_money, person_money, person_money, person_money, person_money, person_money],
    'company_wealth': [company_money, company_money, company_money, company_money, company_money, company_money, company_money],
    'unemployment': 0
  }
  for name in ['person_wealth', 'company_wealth', 'unemployment']:
    if actual[name] != expected[name]:
      print('Failed: Result %s was wrong' % name)
      print('Expected: %s' % str(expected[name]))
      print('Actual:   %s' % str(actual[name]))
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
  person_money = 300 + 100 - spent
  company_money = 300 - 100 + spent
  actual = {
    'person_wealth': results['person_wealth'][30],
    'company_wealth': results['company_wealth'][30],
    'unemployment': results['unemployment'][30]
  }
  expected = {
    'person_wealth': [person_money, person_money, person_money, person_money, person_money, person_money, person_money],
    'company_wealth': [company_money, company_money, company_money, company_money, company_money, company_money, company_money],
    'unemployment': 0
  }
  for name in ['person_wealth', 'company_wealth', 'unemployment']:
    if actual[name] != expected[name]:
      print('Failed: Result %s was wrong' % name)
      print('Expected: %s' % str(expected[name]))
      print('Actual:   %s' % str(actual[name]))
      print(results)
      return
  print('Passed')

# Run all tests
def main():
  test_init_people_assigned_to_companies()
  test_init_money()
  test_basic_one_day()
  test_basic_30_days()

if __name__ == '__main__':
  main()
