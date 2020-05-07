'''
The web server. Serves the index.html page.

Based on: https://flask.palletsprojects.com/en/1.1.x/quickstart/
'''

import flask
import sys

app = flask.Flask(__name__)

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

# Starts the server
def main():
  host = sys.argv[1]
  port = int(sys.argv[2])
  app.run(host=host, port=port)

if __name__ == '__main__':
  main()
