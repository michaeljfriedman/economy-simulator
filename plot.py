'''
Plots the results from the csv files in a directory.
'''

from collections import defaultdict
import argparse
import csv
import numpy as np
import matplotlib.pyplot as plt
import os
import simulator

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('-d', '--data-directory', dest='data_directory', type=str,
    required=True, help='The directory containing the data')
  parser.add_argument('-o', '--output', dest='output', type=str,
    required=True, help='The name of the file to write the plot to')
  parser.add_argument('-p', '--percentiles', dest='percentiles', type=str,
    required=False, default="0,25,50,75,100",
    help='A comma-separated list of percentiles of data to show. Defaults to the standard 5 summary statistics')
  args = parser.parse_args()
  args.percentiles = [int(i) for i in args.percentiles.split(',')]

  # Read data. x[result_name] is the list of days to plot on the x axis,
  # y[result_name] is the data to plot on the y axis for that result.
  x = defaultdict(lambda: [])
  y = defaultdict(lambda: [])
  data_files = [f for f in os.listdir(args.data_directory) if f.endswith('.csv')]
  for filename in data_files:
    path = os.path.join(args.data_directory, filename)
    result_name = filename[:filename.index('.csv')]
    with open(path, 'r') as f:
      r = csv.reader(f)
      for row in r:
        x[result_name].append(float(row[0]))
        y[result_name].append([float(entry) for entry in row[1:]])

  sample = lambda data: [data[i] for i in [0] + list(range(1, len(data), simulator.days_per_month))]
  for result_name in y.keys():
    # Sample the rows - one row per month
    x[result_name] = sample(x[result_name])
    y[result_name] = sample(y[result_name])

    # Filter to only the percentiles specified
    x[result_name] = np.array(x[result_name])
    y[result_name] = np.array(y[result_name])
    if y[result_name].shape[1] == 101: # if data is percentile data
      y[result_name] = y[result_name][:,args.percentiles]

  # Plot data
  f = plt.figure(1, figsize=(20, 15))
  nresults = len(x.keys())
  for i, result_name in zip(range(1, nresults+1), x.keys()):
    ax = f.add_subplot(nresults, 1, i)
    ax.plot(x[result_name], y[result_name])
    ax.set_title(result_name)
    ax.grid()
  plt.savefig(args.output)

if __name__ == '__main__':
  main()
