# Developer Guide

Welcome to the developer guide! This page covers how the simulator is
implemented and how you can get started working on it.

## Getting started

This project uses [vagrant](https://vagrantup.com) +
[virtualbox](https://virtualbox.org) to create the development environment.
First you'll need to have both installed. Then clone this repo and initialize
the development environment with:

```bash
vagrant up
```

Then you can ssh into the virtual machine that's created. The project directory
will be located at /vagrant.

```bash
vagrant ssh
cd /vagrant
```

You can run the simulator/test.py file to verify that everything is working:

```bash
python simulator/test.py
```

If you see all the tests pass, you're good to go!

## Repo

The code is divided into 3 parts: the simulator itself (simulator/), the
command-line app for the simulator (cli/), and the web app (web_app/). Docs are
in the docs/ subdirectory.

```
- cli/
  - main.py       executable app
  - plot.py       plots the results of the simulation
- simulator/
  - simulator.py  the actual simulator
  - test.py       tests for the simulator
- web_app/
  - index.html    HTML for the main page
  - index.js      Scripts for the main page
  - server.py     The web server
```

## Simulator

simulator.py implements the algorithm described in the
[README](../README.md#simulation-algorithm), breaking out individual functions
for different parts. Each of the functions has corresponding unit tests in
test.py.

The simulator just runs the simulation and tracks the model, but doesn't report
any results itself. To get results, clients of the simulator can pass a callback
function `on_day`, which is called at the start of each day. This function can
be used to track progress and/or record data for reporting later.

## CLI

The CLI has two parts: an executable app (main.py) and a plotting program
(plot.py). Running the main produces a directory with output data from the
simulation (the data files produced are described in the header comment of
main.py). The plotter processes the data to produce plots of each of the metrics
described in the [README](../README.md#outputs).

> Note that the data files produced by main.py actually contain all of the raw
results from the simulator, not just the ones plotted. So you could perform
additional analysis on the raw results if you want.

### Config

The config is a JSON object with the following parameters. Distributions are
specified as 2 parallel arrays in a 2d array: the first lists the values, and
the second lists the probability that each value is selected. For example,
in the example config below, the `income` distribution specifies that each
person has an equal 25% chance of being assigned to any of the income levels
($25k, $65k, $100k, and $250k). The parameters are listed in the same order as
in the [README](../README.md#inputs).

Base parameters:

- `ncompanies` (int)
- `income` (distribution)
- `company_size` (distribution)
- `nonpayroll` (float)

Periods:

- `periods` (array): an array of periods as specified below:
  - `duration` (int)
  - `person_stimulus` (float)
  - `company_stimulus` (float)
  - `unemployment_benefit` (float)
  - `rehire_rate` (float)
  - `spending_inclination` (float)
  - `spending_distribution` (distribution)

Example:

```json
{
  "ncompanies": 100,
  "income": [
    [25000, 65000, 100000, 250000],
    [0.25, 0.25, 0.25, 0.25]
  ],
  "company_size": [
    [10, 20],
    [0.5, 0.5]
  ],
  "nonpayroll": 0.75,
  "periods": [
    {
      "duration": 360,
      "person_stimulus": 1.0,
      "company_stimulus": 1.0,
      "unemployment_benefit": 0.8,
      "rehire_rate": 0.8,
      "spending_inclination": 0.5,
      "spending_distribution": [
        ["industry 1", "industry 2"],
        [0.5, 0.5]
      ]
    }
  ]
}
```

## Web app

### Frontend

The web app is just one page that inputs the parameters and plots the outputs
live as the simulation runs. It has two main endpoints: one for the main page,
and one WebSocket endpoint for running the simulator.

The WebSocket is used to maintain a connection so that the server can send live
updates as the simulator runs. Once a connection to the WebSocket is opened, the
client (index.js) sends the config from the frontend to the server (server.py),
and the server parses it and starts the simulator, sending live updates back to
the client each day using the simulator's `on_day` callback.

The frontend (index.{html, js}) is implemented with jQuery. A different class
is defined for each component (e.g. a card), which tracks the inputs and the
HTML element for that component. (In that sense, it's kind of like React, but
just done with jQuery. Why not just use React, you may ask - at the time I
didn't want to have to learn React, so this was faster for me... Not the best
excuse, I know.)

### Deployment

The master branch of the app is deployed on Heroku. You can run it locally with:

```bash
heroku local
```
