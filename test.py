import simulator
import sys

def test_init_people_assigned_to_companies():
  print('Check that all people are assigned to a company')
  people, companies = simulator.init(109, 10, 0)
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
  expected_people_money = income / simulator.months_per_year
  expected_company_money = 10 * income / simulator.months_per_year
  people, companies = simulator.init(100, 10, income)
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
  people, companies = simulator.init(100, 10, 0)
  for p in people:
    if p.spending_rate < 0 or p.spending_rate > 1:
      print('Failed: person has an invalid spending rate')
      print('Expected: in range [0, 1]')
      print('Actual:   %.2f' % p.spending_rate)
      return
  print('Passed')

def test_people_spending():
  print('Check that people spend a valid amount to companies (1 person, 2 companies)')
  p_money = 100
  c_money = 0
  p = simulator.Person(money=p_money)
  c1 = simulator.Company(money=c_money)
  c2 = simulator.Company(money=c_money)
  people, companies = simulator.spend([p], [c1, c2])

  if not (people[0].money < p_money and (companies[0].money > c_money
    or companies[1].money > c_money)):
    print('Failed: money was not spent correctly')
    print('Expected: p.money > %.2f, c1.money or c2.money > %.2f' % (p_money, c_money))
    print('Actual:   p.money = %.2f, c1.money = %.2f, c2.money = %.2f' (
      people[0].money, companies[0].money, companies[1].money
    ))
    return
  print('Passed')

def test_people_spending_when_out_of_business():
  print("Check that people don't spend to an out of business company (1 person, 1 company)")
  p_money = 100
  c_money = 0
  p = simulator.Person(money=p_money)
  c = simulator.Company(money=c_money, in_business=False)
  people, companies = simulator.spend([p], [c])

  if people[0].money != 100 or companies[0].money != 0:
    print("Failed: someone's money changed")
    print('Expected: p.money=%.2f, c.money=%.2f' % (p_money, c_money))
    print('Actual:   p.money=%.2f, c.money=%.2f' % (people[0].money, companies[0].money))
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
  # test_basic_30_days()
  test_people_spending()
  test_people_spending_when_out_of_business()
  test_rehire()

if __name__ == '__main__':
  main()
