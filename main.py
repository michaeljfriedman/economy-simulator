'''
This is the executable of the project. You can run this to run the simulator
from the command line. Outputs the results to the specified directory:
- A csv file for each result statistic: person wealth, company wealth, and
  unemployment rate. Each row is a day of data (the first column is the day).
- A plot of the results

Example:
python main.py --config=config.json --output=output
'''

import argparse
import csv
import json
import matplotlib.pyplot as plt
import numpy as np
import os
import simulator
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
  results = simulator.run(
    ncompanies=config['ncompanies'],
    ndays=config['ndays'],
    income=config['income'],
    spending=config['spending'],
    initial_money=config['initial_money'],
    employees=config['employees'],
    rehire_rate=config['rehire_rate']
  )

  # Convert results to csv-writable format
  results['unemployment'] = list(map(lambda x: [x], results['unemployment']))
  results['out_of_business'] = list(map(lambda x: [x], results['out_of_business']))

  # Write results
  if not os.path.isdir(args.output_dir):
    os.makedirs(args.output_dir, exist_ok=True)
  days = [i for i in range(len(results['unemployment']))]
  for name, data in results.items():
    output_file = os.path.join(args.output_dir, '%s.csv' % name)
    with open(output_file, 'w') as f:
      w = csv.writer(f)
      rows = [[day] + row for day, row in zip(days, data)]
      w.writerows(rows)

if __name__ == '__main__':
  main(sys.argv[1:])
