import simulator
import sys

def test_initialization():
  people, companies = simulator.init(109, 10, 0, 0)
  expected = [11] * 9 + [10]

  print('Check that all people are assigned to a company')
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

# Run all tests
def main():
  test_initialization()

if __name__ == '__main__':
  main()
