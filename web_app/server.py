'''
The web server. Serves the index.html page and .

References:
- Flask + WebSockets + Heroku tutorial: https://devcenter.heroku.com/articles/python-websockets
- Flask docs: https://flask.palletsprojects.com/en/1.1.x/quickstart/
'''

from simulator import simulator
from util import util
import flask
import flask_sockets
import json
import logging
import time

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

  # Callback computes results from the day and sends to the client
  def on_day(period, day, people, companies):
    data = util.results(people, companies)
    msg = json.dumps({'data': data, 'period': period, 'day': day})
    try:
      ws.send(msg)
    except Exception:
      pass

  # Run the simulator
  simulator.run(config, on_day=on_day)
  ws.close()
