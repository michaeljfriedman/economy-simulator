'''
Plots the results from the csv files in a directory.
'''

from collections import defaultdict
from simulator import simulator
import argparse
import csv
import numpy as np
import matplotlib.pyplot as plt
import os

# Computes the percentiles across each row of each dataset, restricted to only
# the given columns
# - data = dict of {name: np array of data}
# - names = list of names to compute percentiles for
# - cols = list of column indexes
# - percentiles = list of percentiles to compute
def compute_results(data, names, cols, percentiles):
  results = {}
  for name in names:
    results[name] = np.percentile(data[name][:,cols], percentiles, axis=1).T
  return results

# Plots one set of results to an output file.
# - x = np array of values to plot on x axis (n x 1)
# - y = dict of {result name: np array of data to plot on y axis (n x m)}. Each
#   result is plotted on a subplot, with the result name as the title
# - output_file = string path to file
def plot(x, y, output_file):
  f = plt.figure(figsize=(20, 15))
  nresults = len(y)
  for i, result_name in zip(range(1, nresults+1), y):
    ax = f.add_subplot(nresults, 1, i)
    ax.plot(x, y[result_name])
    ax.set_title(result_name)
    ax.grid()
  plt.savefig(output_file)

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('-d', '--directory', dest='directory', type=str,
    required=True, help='The directory containing the data. Plots are written here as well')
  parser.add_argument('-p', '--percentiles', dest='percentiles', type=str,
    required=False, default="0,10,25,50,75,90,100",
    help='A comma-separated list of percentiles of data to show. Defaults to the standard 5 summary statistics, plus 10th and 90th percentiles')
  args = parser.parse_args()
  args.percentiles = [int(i) for i in args.percentiles.split(',')]

  # Read data. x is the list of days to plot on the x axis. data[f] is the data
  # from file f
  x = []
  data = {
    'person_income': [],
    'person_money': [],
    'person_industries': [],
    'person_employment': [],
    'company_industries': [],
    'company_money': [],
    'company_closures': []
  }
  for filename in data:
    path = os.path.join(args.directory, '%s.csv' % filename)
    with open(path, 'r') as f:
      r = csv.reader(f)
      row_index = 0
      for row in r:
        if filename == 'person_money':
          x.append([row_index])
        data[filename].append(row)
        row_index += 1

  # Convert to numpy arrays
  x = np.array(x, dtype=np.int)
  for f in data:
    if f in ['person_income', 'person_money', 'company_money']:
      dtype = np.float
    elif f in ['person_employment', 'company_closures']:
      dtype = np.bool
    else:
      dtype = np.str
    data[f] = np.array(data[f], dtype=dtype)

  # Sample the rows to one per month
  sample = lambda arr: arr[list(range(0, arr.shape[0], simulator.days_per_month)),:]
  x = sample(x)
  for f in data:
    data[f] = sample(data[f])

  npeople = data['person_money'].shape[1]
  ncompanies = data['company_money'].shape[1]

  # Plot overall results
  overall_results = compute_results(
    data=data,
    names=['person_money', 'person_employment'],
    cols=range(npeople),
    percentiles=args.percentiles
  )
  overall_results.update(compute_results(
    data=data,
    names=['company_money', 'company_closures'],
    cols=range(ncompanies),
    percentiles=args.percentiles
  ))
  plot(x, overall_results, os.path.join(args.directory, 'overall.png'))

  # Plot results per income level
  for income in np.unique(data['person_income']):
    y = compute_results(
      data=data,
      names=['person_money', 'person_employment'],
      cols=[j for j in range(npeople) if data['person_income'][0,j] == income],
      percentiles=args.percentiles
    )
    plot(x, y, os.path.join(args.directory, 'income-%.2f.png' % income))

  # Plot results per industry
  for ind in np.unique(data['company_industries']):
    y = compute_results(
      data=data,
      names=['person_money', 'person_employment'],
      cols=[j for j in range(npeople) if data['person_industries'][0,j] == ind],
      percentiles=args.percentiles
    )
    y.update(compute_results(
      data=data,
      names=['company_money', 'company_closures'],
      cols=[j for j in range(ncompanies) if data['company_industries'][0,j] == ind],
      percentiles=args.percentiles
    ))
    plot(x, y, os.path.join(args.directory, 'industry-%s.png' % ind))


if __name__ == '__main__':
  main()
