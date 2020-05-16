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

The simulator outputs the results in a dict, as described in the header comment
of the run() function. (Note that this actually contains more data than what's
plotted in the CLI and web app.)

## CLI

The CLI has two parts: an executable app (main.py) and a plotting program
(plot.py). Running the main produces an directory with output data from the
simulation. Within this directory, there's one subdirectory for each industry,
and within that, one csv file for each metric described in the
[README](../README.md#outputs). Running the plotter will produce plots of each of
theses metrics.

> Note that the csv actually contains all of the raw results from the simulator,
not just the ones plotted. So you could perform additional analysis on the raw
results if you want.

### Config

The config is a JSON object with the following parameters. Distributions are
specified as 2 parallel arrays in a 2d array: the first lists the values, and
the second lists the probability that each value is selected. For example,
in the example config below, the `employees` distribution sets that each
company has a 50% chance of being assigned 10 employees, and a 50% chance of 20.
The parameters are listed in the same order as in the [README](../README.md#inputs).

Base parameters:

- `ncompanies` (int)
- `employees` (distribution)
- `income` (distribution)

Periods:

- `periods` (array): an array of periods as specified below. If a parameter is
  not set in a particular period, the value from the previous period is used
  (but all values must be set in the first period):
  - `ndays` (int)
  - `rehire_rate` (float)
  - `people_new_money` (distribution)
  - `companies_new_money` (distribution)
  - `spending` (distribution). As another example, a uniform distribution over
    [0, 1] would be represented as:

    ```json
    [
      [[0, 1]],
      [1]
    ]
    ```

  - `industries` (distribution)

Example:

```json
{
  "ncompanies": 100,
  "employees": [
    [10, 20],
    [0.5, 0.5]
  ],
  "income": [
    [25000, 65000, 100000, 250000],
    [0.25, 0.25, 0.25, 0.25]
  ],
  "periods": [
    {
      "ndays": 360,
      "rehire_rate": 1.0,
      "people_new_money": [
        [1, 2],
        [0.5, 0.5]
      ],
      "companies_new_money": [
        [1, 2],
        [0.5, 0.5]
      ],
      "spending": [
        [[0, 0.5], [0.5, 1]],
        [0.25, 0.75]
      ],
      "industries": [
        ["industry 1", "industry 2"],
        [0.5, 0.5]
      ]
    }
  ]
}
```

## Web app

The web app is just one page that inputs the parameters and plots the outputs
live as the simulation runs. It has two main endpoints: one for the main page,
and one WebSocket endpoint for running the simulator.

The WebSocket is used to maintain a connection so that the server can send live
updates as the simulator runs. Once a connection to the WebSocket is opened, the
client (index.js) sends the config from the frontend to the server (server.py),
and the server parses it and starts the simulator, sending live updates back to
the client each day using the simulator's `update_progress` callback.

The frontend (index.{html, js}) is implemented with jQuery. A different class
is defined for each component (e.g. a card), which tracks the inputs and the
HTML element for that component. (In that sense, it's kind of like React, but
just done with jQuery. Why not just use React, you may ask - at the time I
didn't want to have to learn React, so this was faster for me `¯\_(ツ)_/¯`)
