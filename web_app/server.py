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
import time

app = flask.Flask(__name__)
sockets = flask_sockets.Sockets(app)

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

  # Run simulator
  def update_progress(period, day, people, companies, results):
    try:
      today = {}
      for industry, subresults in results.items():
        today[industry] = {}
        for r, data in subresults.items():
          today[industry][r] = data[day]
      msg = json.dumps({'results': today, 'period': period, 'day': day})
      ws.send(msg)
    except Exception:
      pass
  simulator.run(
    ncompanies=config['ncompanies'],
    employees=config['employees'],
    income=config['income'],
    periods=config['periods'],
    update_progress=update_progress
  )
  ws.close()
