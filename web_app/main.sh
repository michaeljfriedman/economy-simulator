#!/bin/bash
# Runs the server

gunicorn -b 0.0.0.0:8000 -k flask_sockets.worker server:app
