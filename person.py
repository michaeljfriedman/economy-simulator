'''
A person in the model.
'''

class Person:

  def __init__(money=0, income=0, expenses={}, living=True):
    self.money = money
    self.income = income
    self.expenses = expenses
    self.living = living
