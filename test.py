import simulator
import sys

def test_init_people_assigned_to_companies():
  print('Check that all people are assigned to a company')
  people, companies = simulator.init(109, 10, [[0], [1]])
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
  npersons = 10
  income = [[1200, 2400], [0.5, 0.5]]
  expected_people_money = [
    income[0][0] / simulator.months_per_year,
    income[0][1] / simulator.months_per_year
  ]
  expected_company_money = [i*expected_people_money[0] + (npersons-i)*expected_people_money[1]
    for i in range(npersons)]
  people, companies = simulator.init(100, npersons, income)
  for p in people:
    if p.money not in expected_people_money:
      print('Failed: person has wrong amount of money')
      print('Expected: one of %s' % str(expected_people_money))
      print('Actual:   %.2f' % p.money)
      return
  for c in companies:
    if c.money not in expected_company_money:
      print('Failed: company has wrong amount of money')
      print('Expected: one of %s' % str(expected_company_money))
      print ('Actual:  %.2f' % c.money)
      return
  print('Passed')

def test_init_income_distribution():
  print('Check that income is allocated according to the distribution')
  npersons = 1000
  low_income = 100
  high_income = 200
  p = 0.5
  tolerance = 0.02
  income = [[low_income, high_income], [p, p]]
  people, _ = simulator.init(npersons, 1, income)
  npeople_low = len([p for p in people if p.income == low_income])
  npeople_high = len([p for p in people if p.income == high_income])
  low_range = npersons * (p - tolerance)
  high_range = npersons * (p + tolerance)
  if not (low_range <= npeople_low <= high_range and low_range <= npeople_high <= high_range):
    print('Failed: income distribution is off')
    print('Expected: npeople in each category in [%d, %d]' % (int(low_range), int(high_range)))
    print('Actual:   npeople_low=%d, npeople_high=%d' % (npeople_low, npeople_high))
    return
  print('Passed')

def test_init_spending_rate():
  print('Check that all people and companies start a valid spending rate')
  people, companies = simulator.init(100, 10, [[0], [1]])
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

def test_pay_employees():
  print('Check that companies paying employees is working (4 people, 2 companies)')
  npeople = 4
  p_money = 1
  p_income = 12
  c_money = (npeople / 2) * p_income / simulator.months_per_year
  people = [simulator.Person(money=p_money, income=p_income) for i in range(npeople)]
  companies = [
    simulator.Company(money=c_money, employees=people[:int(npeople/2)]),
    simulator.Company(money=c_money, employees=people[int(npeople/2):])
  ]
  people, companies = simulator.pay_employees(people, companies)

  for p in people:
    expected = p_money + p_income / simulator.months_per_year
    if p.money != expected:
      print('Failed: person %s has wrong amount of money' % str(p))
      print('Expected: %.2f' % expected)
      print('Actual:   %.2f' % p.money)
      return
  for c in companies:
    expected = c_money - (npeople / 2) * (p_income / simulator.months_per_year)
    if c.money != expected:
      print('Failed: company %s has wrong amount of money' % str(c))
      print('Expected: %.2f' % expected)
      print('Actual:   %.2f' % c.money)
      return
  print('Passed')

def test_unemployed_people_are_not_paid():
  print('Check that unemployed people do not get paid (1 employed person, 1 unemployed person, 1 company)')
  npeople = 2
  p_money = 1
  p_income = 12
  c_money = npeople * p_income / simulator.months_per_year
  p1 = simulator.Person(money=p_money, income=p_income)
  p2 = simulator.Person(money=p_money, income=p_income, employed=False)
  c = simulator.Company(money=c_money, employees=[p1])
  people, companies = simulator.pay_employees([p1, p2], [c])
  p1, p2 = people
  c = companies[0]

  p1_pay = p_income / simulator.months_per_year
  p1_money_exp = p_money + p1_pay
  if p1.money != p1_money_exp:
    print('Failed: person 1 has wrong amount of money')
    print('Expected: %.2f' % p1_money_exp)
    print('Actual:   %.2f' % p1.money)
    return

  p2_money_exp = p_money
  if p2.money != p2_money_exp:
    print('Failed: person 2 has wrong amount of money')
    print('Expected: %.2f' % p2_money_exp)
    print('Actual:   %.2f' % p2.money)
    return

  c_money_exp = c_money - p1_pay
  if c.money != c_money_exp:
    print('Failed: company has wrong amount of money')
    print('Expected: %.2f' % c_money_exp)
    print('Actual:   %.2f' % c.money)
    return
  print('Passed')

def test_layoff():
  print("Check that company lays off 1 employee when it can't afford them anymore (2 people, 1 company)")
  npeople = 2
  p_income = 12
  c_money = (npeople / 2) * p_income / simulator.months_per_year # only enough for 1 person
  people = [simulator.Person(income=p_income) for i in range(npeople)]
  companies = [simulator.Company(money=c_money, employees=[p for p in people])]

  people, companies = simulator.layoff_employees(people, companies)
  unemployed = 0 if not people[0].employed else 1
  employed = int(not unemployed)
  c = companies[0]

  if people[unemployed].employed:
    print('Failed: both people were still employed')
    print('Expected: One person should be unemployed, and the other should be employed')
    print('Actual: people=%s' % ([str(p) for p in people]))
    return
  if not people[employed].employed:
    print('Failed: both people were laid off')
    print('Expected: One person should be unemployed, and the other should be employed')
    print('Actual: people=%s' % ([str(p) for p in people]))
    return
  if len(c.employees) != 1:
    print('Failed: company has the wrong number of employees')
    print('Expected: len(c.employees) = 1')
    print('Actual:   len(c.employees) = %d' % len(c.employees))
    return
  if c.employees[0] != people[employed]:
    print('Failed: company has the wrong person listed as its employee')
    print('Expected: company employee should be people[%d]=%s' % (employed, str(people[employed])))
    print('Actual:   company employee is people[%d]=%s' % (unemployed, str(people[unemployed])))
    return
  if not c.in_business:
    print('Failed: company is marked out of business even though it still has 1 employee')
    print('Expected: c.in_business = True')
    print('Actual:   c.in_business = %s' % str(c.in_business))
  print('Passed')

def test_company_goes_out_of_business():
  print('Check that a company goes out of business when it lays off all of its employees (1 person, 1 company)')
  p_income = 12
  c_money = 0.5 * p_income / simulator.months_per_year # half the amount it needs
  p = simulator.Person(income=p_income)
  c = simulator.Company(money=c_money, employees=[p])
  people, companies = simulator.layoff_employees([p], [c])

  p = people[0]
  c = companies[0]
  if p.employed:
    print('Failed: person is still marked as employed')
    print('Expected: p.employed = False')
    print('Actual:   p.employed = %s' % str(p.employed))
    return
  if len(c.employees) != 0:
    print('Failed: company still has employees')
    print('Expected: len(c.employees) = 0')
    print('Actual:   len(c.employees) = %d' % len(c.employees))
    return
  if c.in_business:
    print('Failed: company is still marked as in-business')
    print('Expected: c.in_business = False')
    print('Actual:   c.in_business = %s' % str(c.in_business))
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
  test_init_income_distribution()
  test_people_spending()
  test_people_spending_when_out_of_business()
  test_pay_employees()
  test_unemployed_people_are_not_paid()
  test_layoff()
  test_company_goes_out_of_business()
  test_rehire()

if __name__ == '__main__':
  main()
