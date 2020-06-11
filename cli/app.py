'''
This is the executable of the project. You can run this to run the simulator
from the command line. Outputs the results to the specified directory.

Example:
python main.py --config=config.json --output=output
'''

from simulator import simulator
from util import util
from tqdm import tqdm
import argparse
import json
import matplotlib.pyplot as plt
import numpy as np
import os
import sys

# Plots one set of results to an output file.
# - x = list values to plot on x axis
# - y = parallel list of {result name: value to plot on y axis}. Each
#   result is plotted on a subplot, with the result name as the title
# - output_file = string path to file
def plot(x, y, output_file):
  f = plt.figure(figsize=(20, 15))
  result_names = y[0].keys()
  nresults = len(result_names)
  for i, result_name in zip(range(1, nresults+1), result_names):
    ax = f.add_subplot(nresults, 1, i)
    y_values = [y[i][result_name] for i in range(len(y))]
    ax.plot(x, y_values)
    ax.set_title(result_name)
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
  total_ndays = simulator.days_per_month * sum([config['periods'][i]['duration'] for i in range(len(config['periods']))])
  t = tqdm(total=total_ndays)
  results = []
  def on_day(period, day, people, companies):
    t.update()
    if day % simulator.days_per_month != 0:
      return
    results.append(util.results(people, companies))

  simulator.run(config, on_day=on_day)
  t.close()

  # Plot results
  if not os.path.isdir(args.output_dir):
    os.mkdir(args.output_dir)
  x = range(len(results))
  plot(x, [results[i]['overall'] for i in range(len(results))], os.path.join(args.output_dir, 'overall.png'))
  for income in results[0]['income_levels'].keys():
    plot(
      x=x,
      y=[results[i]['income_levels'][income] for i in range(len(results))],
      output_file=os.path.join(args.output_dir, 'income-%s.png' % income)
    )
  for industry in results[0]['industries'].keys():
    plot(
      x=x,
      y=[results[i]['industries'][industry] for i in range(len(results))],
      output_file=os.path.join(args.output_dir, 'industry-%s.png' % industry)
    )

if __name__ == '__main__':
  main(sys.argv[1:])
