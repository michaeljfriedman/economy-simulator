'''
The web server. Serves the index.html page and .

References:
- Flask + WebSockets + Heroku tutorial: https://devcenter.heroku.com/articles/python-websockets
- Flask docs: https://flask.palletsprojects.com/en/1.1.x/quickstart/
'''

from simulator import simulator
import flask
import flask_sockets
import json
import logging
import numpy as np
import time

# Merges dicts
def merge(dicts):
  d0 = dicts[0]
  for d in dicts[1:]:
    d0.update(d)
  return d0

app = flask.Flask(__name__)
sockets = flask_sockets.Sockets(app)
gunicorn_logger = logging.getLogger('gunicorn.error')
app.logger.handlers = gunicorn_logger.handlers
app.logger.setLevel(gunicorn_logger.level)

# Returns the index html page
@app.route('/')
def index():
  with open('web_app/index.html') as f:
    return f.read()

# Returns the index js page
@app.route('/index.js')
def index_js():
  with open('web_app/index.js') as f:
    return f.read()

# Runs the simulator with the config provided by the client. Sends a simple
# progress update each day - just the current period/day.
@sockets.route('/run-simulator')
def run_simulator(ws):
  config = json.loads(ws.receive())

  # Validate config
  def replyInvalid(ws):
    ws.send(json.dumps({'results': 'invalid config'}))
    ws.close()
  for _, v in config.items():
    if v == None:
      replyInvalid(ws)
      return

  if len(config['periods']) == 0:
    replyInvalid(ws)
    return

  for p in config['periods']:
    for _, v in p.items():
      if v == None:
        replyInvalid(ws)
        return

  # Helper functions
  def people_results(people, percentiles):
    person_money = [0] * len(percentiles) if len(people) == 0 else list(np.round(np.percentile([p.money for p in people], percentiles), 2))
    person_unemployment = [1] if len(people) == 0 else [np.mean([not p.employed for p in people])]
    return {
      'person_money': person_money,
      'person_unemployment': person_unemployment
    }

  def company_results(companies, percentiles):
    return {
      'company_money': list(np.round(np.percentile([c.money for c in companies], percentiles), 2)),
      'company_closures': [np.mean([not c.in_business for c in companies])]
    }

  # Callback computes results from the day and sends to the client
  def on_day(period, day, people, companies):
    percentiles = [0, 10, 25, 50, 75, 90, 100]
    income_levels = set([p.income for p in people])
    industries = set([c.industry for c in companies])
    data = {
      'overall': merge([
        people_results(people, percentiles),
        company_results(companies, percentiles),
        {'circulation': [
          round(np.sum([p.money for p in people]) + np.sum([c.money for c in companies]), 2)
        ]}
      ]),
      'income_levels': {
        str(int(simulator.months_per_year * i)): people_results([p for p in people if p.income == i], percentiles)
        for i in income_levels
      },
      'industries': {
        i: merge([
          people_results([p for p in people if p.industry == i], percentiles),
          company_results([c for c in companies if c.industry == i], percentiles)
        ])
        for i in industries
      }
    }
    msg = json.dumps({'data': data, 'period': period, 'day': day})
    try:
      ws.send(msg)
    except Exception:
      pass

  # Run the simulator
  simulator.run(config, on_day=on_day)
  ws.close()
