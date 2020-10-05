# Platform Manager

Platform Manager handles starting new simulations for the simulation platform.

## Setup

instructions for starting a local MongoDB instance for the use of the logging system can be found at [https://git.ain.rd.tut.fi/procemplus/logwriter/-/tree/master/mongodb](https://git.ain.rd.tut.fi/procemplus/logwriter/-/tree/master/mongodb).

To build the required Docker images, to make the needed static files available, and to start the background processes:

```bash
source platform_setup.sh
```

### Advanced setup

To only build the Docker images:

```bash
docker-compose -f build/docker-compose-build-images.yml build
```

To only copy the static resource files:

```bash
source copy_folder_to_volume.sh resources simulation_resources /resources
```

To only start the background processes (RabbitMQ, MongoDB, LogReader):

```bash
docker-compose -f background/docker-compose-background.yml up --detach
```

## Run simulation

To start a simulation: edit the simulation settings in [simulation_configuration.yml](simulation_configuration.yml) and the run the command

```bash
source start_platform.sh
```
