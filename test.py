import simulator
import sys

def test_init_people_assigned_to_companies():
  print('Check that all people are assigned to a company')
  people, companies = simulator.init(109, 10, 0, [0, 0])
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
  people, companies = simulator.init(100, 10, income, [0, 0])
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

def test_init_spending_rate():
  print('Check that all people and companies start a valid spending rate')
  low = 0.75
  high = 1.25
  people, companies = simulator.init(100, 10, 0, [low, high])
  for p in people:
    if p.spending_rate < 0.75 or p.spending_rate > 1.25:
      print('Failed: person has an invalid spending rate')
      print('Expected: in range [%.2f, %.2f)' % (low, high))
      print('Actual:   %.2f' % p.spending_rate)
      return
  print('Passed')

def test_basic_one_day():
  print('Check that last-day results of a 1 day simulation are correct (1 person, 1 company, income 1200, saving rate 0.25)')
  results = simulator.run(
    npersons=1,
    ncompanies=1,
    ndays=1,
    income=1200,
    spending_range=[0.75, 0.75]
  )
  actual = {
    'person_wealth': results['person_wealth'][1],
    'company_wealth': results['company_wealth'][1],
    'unemployment': results['unemployment'][1],
    'out_of_business': results['out_of_business'][1]
  }
  spent = 75 / 30
  person_money = 300 - spent
  company_money = 300 + spent
  expected = {
    'person_wealth': [person_money, person_money, person_money, person_money, person_money, person_money, person_money],
    'company_wealth': [company_money, company_money, company_money, company_money, company_money, company_money, company_money],
    'unemployment': 0,
    'out_of_business': 0
  }
  for name in expected.keys():
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
    spending_range=[0.75, 0.75]
  )
  spent = 75
  person_money = 300 + 100 - spent
  company_money = 300 - 100 + spent
  actual = {
    'person_wealth': results['person_wealth'][30],
    'company_wealth': results['company_wealth'][30],
    'unemployment': results['unemployment'][30],
    'out_of_business': results['out_of_business'][30]
  }
  expected = {
    'person_wealth': [person_money, person_money, person_money, person_money, person_money, person_money, person_money],
    'company_wealth': [company_money, company_money, company_money, company_money, company_money, company_money, company_money],
    'unemployment': 0,
    'out_of_business': 0
  }
  for name in expected.keys():
    if actual[name] != expected[name]:
      print('Failed: Result %s was wrong' % name)
      print('Expected: %s' % str(expected[name]))
      print('Actual:   %s' % str(actual[name]))
      print(results)
      return
  print('Passed')

def test_rehire():
  print('Check that rehiring works (1 person, 1 company that can afford to hire that person)')
  income = 12
  people = [simulator.Person(income=income, employed=False)]
  companies = [simulator.Company(money=income/simulator.months_per_year)]

  p = simulator.Person(income=income, employed=True)
  expected_people = [p]
  expected_companies = [simulator.Company(
    money=income/simulator.months_per_year,
    employees=[p]
  )]

  actual_people, actual_companies = simulator.rehire_people(people, companies, 1.0)

  for p_exp, p_act in zip(expected_people, actual_people):
    if str(p_exp) != str(p_act):
      print('Failed: person was wrong')
      print('Expected: %s' % str(p_exp))
      print('Actual:   %s' % str(p_act))
      return
  for c_exp, c_act in zip(expected_companies, actual_companies):
    if str(c_exp) != str(c_act):
      print('Failed: company was wrong')
      print('Expected: %s' % str(c_exp))
      print('Actual:   %s' % str(c_act))
      return
  print('Passed')

# Run all tests
def main():
  test_init_people_assigned_to_companies()
  test_init_money()
  test_init_spending_rate()
  test_basic_one_day()
  test_basic_30_days()
  test_rehire()

if __name__ == '__main__':
  main()
