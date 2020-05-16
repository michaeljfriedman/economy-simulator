# Economy Simulation

This project simulates the economy using a simplified model. Our goal is to
see what happens to the distribution of wealth across people and companies, the
the unemployment rate, and the company survival rate, when you vary certain
parameters.

This README covers how to set up your environment to work on the project or run
the simulation. For details on how the simulator works, see the [docs](docs/).

## Getting Started

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

To run the simulation, you'll need to write a config file that sets its
parameters. See the [design page](docs/design.md) for the config spec and an
example that you can copy/paste into a file, e.g. config.json. Then you can run
the simulation:

```bash
cd cli
python main.py --config=config.json --output=output/
```

This will produce a bunch of metrics in the output/ directory. You can plot
them with:

```bash
python plot.py --data-directory=output/ --output=plot.png
```

This will show the metrics over time: the distributions of wealth across people
and companies, the unemployment rate, and the "out of business" rate (the
fraction of companies that went out of business).

That's it! Play around with the config and see what happens to the economy. Use
the `--help` flag for more details on the command-line options.

---

Copyright 2020, Michael Friedman
