import simulator
import sys

def test_init_company_size():
  print('Check that company sizes are allocated according to the distribution')
  low = 10
  high = 20
  p = 0.5
  people, companies = simulator.init(ncompanies=100, company_size=[[low, high], [p, p]])

  # Check that all people are assigned to a company
  for i in range(len(people)):
    present = False
    for j in range(len(companies)):
      if people[i] in companies[j].employees:
        present = True
        break
    if not present:
      print('Failed: person %d not assigned to a company')
      return

  # Check distribution is correct
  nlow = len([c for c in companies if len(c.employees) == low])
  nhigh = len([c for c in companies if len(c.employees) == high])
  tolerance = 0.1
  lower_bound = len(companies) * (p - tolerance)
  upper_bound = len(companies) * (p + tolerance)
  if not (lower_bound <= nlow <= upper_bound and lower_bound <= nhigh <= upper_bound):
    print('Failed: company size distribution is off')
    print('Expected: size in each category in [%d, %d]' % (int(lower_bound), int(upper_bound)))
    print('Actual:   nlow=%d, nhigh=%d' % (nlow, nhigh))
    return
  print('Passed')

def test_init_income_distribution():
  print('Check that income is allocated according to the distribution')
  low = 12
  high = 24
  p = 0.5
  income = [[low, high], [p, p]]
  people, _ = simulator.init(ncompanies=1, income=income, company_size=[[1000], [1]])

  nlow = len([p for p in people if p.income == low / simulator.months_per_year])
  nhigh = len([p for p in people if p.income == high / simulator.months_per_year])
  tolerance = 0.04
  lower_bound = len(people) * (p - tolerance)
  upper_bound = len(people) * (p + tolerance)

  if not (lower_bound <= nlow <= upper_bound and lower_bound <= nhigh <= upper_bound):
    print('Failed: income distribution is off')
    print('Expected: npeople in each category in [%d, %d]' % (int(lower_bound), int(upper_bound)))
    print('Actual:   nlow=%d, nhigh=%d' % (nlow, nhigh))
    return
  print('Passed')

def test_init_spending_inclination(s):
  print('Check that spending rates are allocated according to the spending inclination: %.2f' % (s))
  people, _ = simulator.init(
    ncompanies=1,
    spending_inclination=s,
    company_size=[[1000], [1]]
  )

  avg = sum([p.spending_rate for p in people]) / len(people)
  tolerance = 0.01
  lower_bound = s - tolerance
  upper_bound = s + tolerance

  if not (lower_bound <= avg <= upper_bound):
    print('Failed: spending inclination is off')
    print('Expected: average spending rate in range [%.4f, %.4f]' % (lower_bound, upper_bound))
    print('Actual:   average spending rate = %.4f' % (avg))
    return
  print('Passed')

def test_init_industries():
  print('Check that industries are assigned correctly')
  ind1 = 'industry 1'
  ind2 = 'industry 2'
  people, companies = simulator.init(industry_names=[ind1, ind2])

  n1 = len([c for c in companies if c.industry == ind1])
  n2 = len([c for c in companies if c.industry == ind2])
  if n1 != n2:
    print('Failed: wrong number of companies in each industry')
    print('Expected: n1=%d, n2=%d' % (len(companies)/2, len(companies)/2))
    print('Actual:   n1=%d, n2=%d' % (n1, n2))
    return

  for c in companies:
    for e in c.employees:
      if e.industry != c.industry:
        print('Failed: person is not assigned the industry of their company')
        print('Expected: c.industry=%s, p.industry=%s' % (c.industry, c.industry))
        print('Actual:   c.industry=%s, p.industry=%s' % (c.industry, p.industry))
        return
  print('Passed')

def test_stimulus():
  print('Check that stimulus is granted correctly')
  n = 1000
  income = 1
  init_money = 10
  person_stimulus = 0.8
  company_stimulus = 0.9
  people = [simulator.Person(money=init_money, income=income) for i in range(n)]
  companies = [simulator.Company(money=init_money, employees=[people[i]]) for i in range(n)]
  people, companies = simulator.grant_stimulus(people, companies, person_stimulus, company_stimulus)

  # Check that money is correct
  groups = [
    ('people', people, person_stimulus),
    ('companies', companies, company_stimulus)
  ]
  for group_name, group, stimulus in groups:
    expected_money = init_money + stimulus * income
    nincorrect = len([x for x in group if x.money != expected_money])
    for x in group:
      if x.money != expected_money:
        print('Failed: Someone in %s had wrong amount of money' % (group_name))
        print('Expected: money=%.2f' % expected_money)
        print('Actual:   money=%.2f' % x.money)
        return
  print('Passed')

def test_unemployment_benefit():
  print('Check that unemployment benefit is granted correctly')
  n_employed = 8
  n_unemployed = 2
  income = 1
  init_money = 10
  unemployment_benefit = 0.8
  people = (
    [simulator.Person(money=init_money, income=income) for i in range(n_employed)]
    + [simulator.Person(money=init_money, income=income, employed=False) for i in range(n_unemployed)]
  )
  people = simulator.grant_unemployment(people, unemployment_benefit)

  # Check that money is correct
  for p in people:
    money_with_benefit = init_money + unemployment_benefit * income
    if p.employed and p.money != init_money:
      print('Falied: Employed person has wrong amount of money')
      print('Expected: money=%.2f' % init_money)
      print('Actual:   money=%.2f' % p.money)
      return
    elif not p.employed and p.money != money_with_benefit:
      print('Failed: Unemployed person has wrong amount of money')
      print('Expected: money=%.2f' % money_with_benefit)
      print('Actual:   money=%.2f' % p.money)
      return
  print('Passed')


def test_people_spending1():
  print('Check that people spend a valid amount to companies (1 person, 2 companies)')
  p_money = 100
  c_money = 0
  ind = 'industry'
  spending_rate = 0.5
  p = simulator.Person(money=p_money, spending_rate=spending_rate)
  c1 = simulator.Company(money=c_money, industry=ind)
  c2 = simulator.Company(money=c_money, industry=ind)
  companies = [c1, c2]
  people, companies = simulator.spend([p], companies, [[ind], [1]], {ind: companies})

  spent = spending_rate * p_money / simulator.days_per_month
  p_money_exp = p_money - spent
  c_money_exp = c_money + spent
  if not (people[0].money == p_money_exp and (companies[0].money == c_money_exp
    or companies[1].money == c_money_exp)):
    print('Failed: money was not spent correctly')
    print('Expected: p.money = %.2f, c1.money or c2.money = %.2f' % (p_money_exp, c_money_exp))
    print('Actual:   p.money = %.2f, c1.money = %.2f, c2.money = %.2f' % (
      people[0].money, companies[0].money, companies[1].money
    ))
    return
  print('Passed')

def test_people_spending2():
  print('Check that people spend a valid amount to companies, with > 1 industry (100 people, 2 companies in diff industries)')
  p_money = 100
  c_money = 0
  ind1 = 'industry 1'
  ind2 = 'industry 2'
  spending_rate = 0.5
  p = 0.75
  people = [simulator.Person(money=p_money, spending_rate=spending_rate) for i in range(100)]
  companies = [
    simulator.Company(money=c_money, industry=ind1),
    simulator.Company(money=c_money, industry=ind2)
  ]
  people, companies = simulator.spend(
    people,
    companies,
    [[ind1, ind2], [p, 1-p]],
    {ind1: [companies[0]], ind2: [companies[1]]}
  )

  # Check that people's money is correct
  spent = spending_rate * p_money / simulator.days_per_month
  p_money_exp = p_money - spent
  for person in people:
    if person.money != p_money_exp:
      print('Failed: person spent wrong amount of money')
      print('Expected: p.money=%.2f' % p_money_exp)
      print('Actual:   p.money=%.2f' % p.money)
      return

  # Check that companies' money matches the expected distribution
  tolerance = 0.1
  c_money_exp = [
    {'lower_bound': c_money + (p - tolerance) * len(people) * spent,
     'upper_bound': c_money + (p + tolerance) * len(people) * spent},
    {'lower_bound': c_money + (1 - p - tolerance) * len(people) * spent,
     'upper_bound': c_money + (1 - p + tolerance) * len(people) * spent}
  ]
  for i in range(len(companies)):
    lower_bound = c_money_exp[i]['lower_bound']
    upper_bound = c_money_exp[i]['upper_bound']
    if not (lower_bound <= companies[i].money <= upper_bound):
      print('Failed: company money does not match the distribution')
      print('Expected: company %d money should be in range [%.2f, %.2f]' % (i, lower_bound, upper_bound))
      print('Actual:   company money = %.2f' % companies[i].money)
      return
  print('Passed')

def test_people_spending_when_out_of_business():
  print("Check that people don't spend to an out of business company (1 person, 1 company)")
  p_money = 100
  c_money = 0
  ind = 'industry'
  p = simulator.Person(money=p_money)
  c = simulator.Company(money=c_money, in_business=False, industry=ind)
  people, companies = simulator.spend(
    [p],
    [c],
    [[ind], [1]],
    {ind: [c]}
  )

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
  p_income = 1
  c_money = (npeople / 2) * p_income
  people = [simulator.Person(money=p_money, income=p_income) for i in range(npeople)]
  companies = [
    simulator.Company(money=c_money, employees=people[:int(npeople/2)]),
    simulator.Company(money=c_money, employees=people[int(npeople/2):])
  ]
  people, companies = simulator.pay_employees(people, companies)

  for p in people:
    expected = p_money + p_income
    if p.money != expected:
      print('Failed: person %s has wrong amount of money' % str(p))
      print('Expected: %.2f' % expected)
      print('Actual:   %.2f' % p.money)
      return
  for c in companies:
    expected = c_money - (npeople / 2) * (p_income)
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
  p_income = 1
  c_money = npeople * p_income
  p1 = simulator.Person(money=p_money, income=p_income)
  p2 = simulator.Person(money=p_money, income=p_income, employed=False)
  c = simulator.Company(money=c_money, employees=[p1])
  people, companies = simulator.pay_employees([p1, p2], [c])
  p1, p2 = people
  c = companies[0]

  p1_pay = p_income
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
  print("Check that company lays off 2/4 employees when it can't afford them anymore (4 people, 1 company)")
  npeople = 4
  p_income = 1
  c_money = (npeople / 2) * p_income # only enough for 1/2
  people = [simulator.Person(income=p_income) for i in range(npeople)]
  companies = [simulator.Company(money=c_money, employees=[p for p in people])]

  people, companies = simulator.layoff_employees(people, companies)
  unemployed = [i for i in range(len(people)) if not people[i].employed]
  employed = [i for i in range(len(people)) if people[i].employed]
  c = companies[0]

  if len(unemployed) != npeople / 2:
    print('Failed: wrong number of people were laid off')
    print('Expected: %d' % (npeople / 2))
    print('Actual:   %d' % len(unemployed))
    return
  if len(employed) != npeople / 2:
    print('Failed: wrong number of people are still employed')
    print('Expected: %d' % (npeople / 2))
    print('Actual:   %d' % len(employed))
    return
  if len(c.employees) != npeople / 2:
    print('Failed: company has the wrong number of employees')
    print('Expected: %d' % (npeople / 2))
    print('Actual:   %d' % len(c.employees))
    return

  employee_indices = []
  for e in c.employees:
    for i in range(len(people)):
      if e == people[i]:
        employee_indices.append(i)
  if sorted(employee_indices) != sorted(employed):
    print('Failed: company has the wrong people listed as employees')
    print('Expected: people indices %s' % sorted(employed))
    print('Actual:   people indices %s' % sorted(employee_indices))
    return
  if not c.in_business:
    print('Failed: company is marked out of business even though it still has employees')
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
  income = 1
  old_ind = 'old industry'
  new_ind = 'new industry'
  people = [simulator.Person(income=income, employed=False, industry=old_ind)]
  companies = [simulator.Company(money=income, industry=new_ind)]

  p_exp = simulator.Person(income=income, employed=True, industry=new_ind)
  expected_people = [p_exp]
  expected_companies = [simulator.Company(
    money=income,
    employees=[p_exp],
    industry=new_ind
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
  test_init_company_size()
  test_init_income_distribution()
  test_init_spending_inclination(0.5)
  test_init_spending_inclination(0.2)
  test_init_spending_inclination(0.9)
  test_init_industries()
  test_stimulus()
  test_unemployment_benefit()
  test_people_spending1()
  test_people_spending2()
  test_people_spending_when_out_of_business()
  test_pay_employees()
  test_unemployed_people_are_not_paid()
  test_layoff()
  test_company_goes_out_of_business()
  test_rehire()

if __name__ == '__main__':
  main()
