# Economy Simulation

This project simulates the economy using a simplified model.

This README covers how to set up your environment to work on the project or run
the simulation. For details on how the simulation works, see the
[design page](design.md).

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

**TODO**: running the simulation
