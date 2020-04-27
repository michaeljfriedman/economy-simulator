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
import os
import simulator
import sys

# Plots results to a file.
# - days: a parallel list numbering the days. This will be the x axis
# - results: a dict of results. Each key is the name of the result, and maps
#   to a list of values to plot, one for each day. e.g. {'result1': [0, 1, 2]}.
#   These will be the y-axis, with each result plotted on a subplot.
# - output_file: the file to write the plot to
# - sample (optional): a lambda mapping a full list of values to a subset of
#   values. This will be used to sample the data in the plot.
def plot_results(days, results, output_file, sample=lambda x: x):
  f = plt.figure(1, figsize=(20, 15))
  nresults = len(results.keys())
  for i, name in zip(range(1, nresults+1), results.keys()):
    ax = f.add_subplot(3, 1, i)
    ax.plot(sample(days), sample(results[name]))
    ax.set_title(name)
    ax.grid()
  plt.savefig(output_file)

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
    npersons=config['npersons'],
    ncompanies=config['ncompanies'],
    ndays=config['ndays'],
    income=config['income'],
    spending_range=config['spending_range']
  )

  # Convert unemployment results to csv-writable format
  results['unemployment'] = list(map(lambda x: [x], results['unemployment']))

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

  # Create plots of results, sampling the first day of each month
  sample = lambda x: [x[0]] + [x[i] for i in range(1, len(x), simulator.days_per_month)]
  output_file = os.path.join(args.output_dir, 'plot.png')
  plot_results(days, results, output_file, sample=sample)

if __name__ == '__main__':
  main(sys.argv[1:])
