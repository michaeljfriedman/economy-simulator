'''
The websocket server.

Based on: https://websockets.readthedocs.io/en/stable/intro.html
'''

import asyncio
import json
import sys
import websockets

# Reads 2 numbers from the client and sends back their sum
async def handle_connection(ws, path):
  print('New connection')
  if path != '/':
    print('Not supported')
    return

  msg = json.loads(await ws.recv())
  resp = {'sum': msg['x'] + msg['y']}
  await ws.send(json.dumps(resp))

# Starts the server
def main():
  ip = sys.argv[1]
  port = int(sys.argv[2])
  print('Starting server on %s:%d' % (ip, port))
  start_server = websockets.serve(handle_connection, ip, port)
  asyncio.get_event_loop().run_until_complete(start_server)
  asyncio.get_event_loop().run_forever()

if __name__ == '__main__':
  main()
