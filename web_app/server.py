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
  with open('index.html') as f:
    return f.read()

# Returns the index js page
@app.route('/index.js')
def index_js():
  with open('index.js') as f:
    return f.read()

@sockets.route('/run-simulator')
def run_simulator(ws):
  # config = json.loads(ws.receive())
  # def update_progress(period, day, people, companies, results):
  #   try:
  #     ws.send(json.dumps(results))
  #   except Exception:
  #     pass
  # simulator.run(
  #   ncompanies=config['ncompanies'],
  #   employees=config['employees'],
  #   income=config['income'],
  #   periods=config['periods'],
  #   update_progress=update_progress
  # )
  # ws.close()

  msg = json.loads(ws.receive())
  x0 = int(msg['x'])
  x1 = int(msg['y'])
  for i in range(10):
    s = x0 + x1
    ws.send(json.dumps({'sum': s}))
    x0 = x1
    x1 = s
    time.sleep(1)
  ws.close()
