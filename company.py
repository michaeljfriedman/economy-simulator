'''
A company in the model.
'''

class Company:

  def __init__(money=0, industry=None, employees=[], expenses={}, in_business=True):
    self.money = money
    self.industry = industry
    self.employees = employees
    self.expenses = expenses
    self.in_business = in_business
