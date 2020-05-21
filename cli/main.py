'''
This is the executable of the project. You can run this to run the simulator
from the command line. Outputs the results to the specified directory:
- person_income.csv: A row of each person's income
- person_money.csv: 1 row for each day, recording each person's money that day
- person_industries.csv: 1 row for each day, recording each person's industry
  that day
- person_unemployment.csv: 1 row for each day, recording 0/1 whether each person
  is unemployed.
- company_industries.csv: A row of each company's industry
- company_money.csv: 1 row for each day, recording each company's money that day
- company_closures.csv: 1 row for each day, recording 0/1 whether each company
  is closed down

Example:
python main.py --config=config.json --output=output
'''

from simulator import simulator
from tqdm import tqdm
import argparse
import csv
import json
import numpy as np
import os
import sys

def main(argv):
  # Parse config
  parser = argparse.ArgumentParser()
  parser.add_argument('-c', '--config', dest='config', type=str,
    default='config.json', help='The path to the config file')
  parser.add_argument('-o', '--output', dest='output_dir', type=str,
    default='output', help='The directory to write results to')
  args = parser.parse_args()
  with open(args.config, 'r') as f:
    config = json.loads(f.read())

  # Run simulator
  total_ndays = sum([config['periods'][i]['duration'] for i in range(len(config['periods']))])
  person_income = [[]]
  person_money = [[] for i in range(total_ndays)]
  person_industries = [[] for i in range(total_ndays)]
  person_unemployment = [[] for i in range(total_ndays)]
  company_industries = [[]]
  company_money = [[] for i in range(total_ndays)]
  company_closures = [[] for i in range(total_ndays)]
  t = tqdm(total=total_ndays)
  def on_day(period, day, people, companies):
    i = simulator.days_per_month * period + day
    for p in people:
      if period == 0 and day == 0:
        person_income[0].append(p.income)
      person_money[i].append(p.money)
      person_industries[i].append(p.industry)
      person_unemployment[i].append(not p.employed)
    for c in companies:
      if period == 0 and day == 0:
        company_industries[0].append(c.industry)
      company_money[i].append(c.money)
      company_closures[i].append(not c.in_business)
    t.update()

  simulator.run(
    ncompanies=config['ncompanies'],
    income=config['income'],
    company_size=config['company_size'],
    periods=config['periods'],
    on_day=on_day
  )
  t.close()

  # Write results
  if not os.path.isdir(args.output_dir):
      os.mkdir(args.output_dir)
  files = [
    ('person_income', person_income),
    ('person_money', person_money),
    ('person_industries', person_industries),
    ('person_unemployment', person_unemployment),
    ('company_industries', company_industries),
    ('company_money', company_money),
    ('company_closures', company_closures)
  ]
  for filename, data in files:
    path = os.path.join(args.output_dir, '%s.csv' % filename)
    with open(path, 'w') as f:
      w = csv.writer(f)
      arr = np.array(data)
      if filename in ['person_income', 'person_money', 'company_money']:
        arr = np.around(arr, 2) # round to 2 decimal places
      elif filename in ['person_unemployment', 'company_closures']:
        arr = arr.astype(int) # convert to 0/1
      w.writerows(arr)

if __name__ == '__main__':
  main(sys.argv[1:])
