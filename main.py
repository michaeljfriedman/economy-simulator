'''
This is the executable of the project. You can run this to run the simulator
from the command line.

Example:
python main.py --config=config.json
'''

import argparse
import csv
import json
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
    npersons=config['npersons'],
    ncompanies=config['ncompanies'],
    ndays=config['ndays'],
    income=config['income'],
    saving_rate=config['saving_rate']
  )

  # Convert unemployment results to csv-writable format
  results['unemployment'] = map(lambda x: [x], results['unemployment'])

  # Write results
  if not os.path.isdir(args.output_dir):
    os.mkdir(args.output_dir)
  for name, data in results.items():
    output_file = os.path.join(args.output_dir, '%s.csv' % name)
    with open(output_file, 'w') as f:
      w = csv.writer(f)
      w.writerows(data)

if __name__ == '__main__':
  main(sys.argv[1:])
