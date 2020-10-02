# Platform Manager

Platform Manager handles starting new simulations for the simulation platform.

instructions for starting a local MongoDB instance for the use of the logging system can be found at [https://git.ain.rd.tut.fi/procemplus/logwriter/-/tree/master/mongodb](https://git.ain.rd.tut.fi/procemplus/logwriter/-/tree/master/mongodb).

To create the Docker volumes that are used by the platform manager and the simulation components:

```bash
docker volume create simulation_configuration
docker volume create simulation_resources
docker volume create simulation_logs
```

To start a simulation: edit the simulation settings in [simulation_configuration.yml](simulation_configuration.yml) and the run the command

```bash
source start_platform.sh
```
