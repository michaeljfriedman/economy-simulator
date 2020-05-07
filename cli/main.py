'''
This is the executable of the project. You can run this to run the simulator
from the command line. Outputs the results to the specified directory:
- A csv file for each result statistic: person wealth, company wealth, and
  unemployment rate. Each row is a day of data (the first column is the day).
- A plot of the results

Example:
python main.py --config=config.json --output=output
'''

from simulator import simulator
from tqdm import tqdm
import argparse
import csv
import json
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
  total_ndays = sum([config['periods'][i]['ndays'] for i in range(len(config['periods']))])
  t = tqdm(total=total_ndays)
  def update_progress(period, day, people, companies, results):
    t.update()
  results = simulator.run(
    ncompanies=config['ncompanies'],
    employees=config['employees'],
    income=config['income'],
    periods=config['periods'],
    update_progress=update_progress
  )
  t.close()

  # Write results
  for ind, ind_results in results.items():
    path = os.path.join(args.output_dir, ind)
    if not os.path.isdir(path):
      os.makedirs(path, exist_ok=True)

    # Convert results to csv-writable format
    ind_results['unemployment'] = list(map(lambda x: [x], ind_results['unemployment']))
    ind_results['out_of_business'] = list(map(lambda x: [x], ind_results['out_of_business']))

    # Write
    days = [i for i in range(len(ind_results['unemployment']))]
    for name, data in ind_results.items():
      output_file = os.path.join(path, '%s.csv' % name)
      with open(output_file, 'w') as f:
        w = csv.writer(f)
        rows = [[day] + row for day, row in zip(days, data)]
        w.writerows(rows)

if __name__ == '__main__':
  main(sys.argv[1:])
