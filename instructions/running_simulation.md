# Running simulations

<!-- no toc -->
- [Running first test simulation](#running-first-test-simulation)
    - [Setting up the environment parameters for the Platform Manager](#setting-up-the-environment-parameters-for-the-platform-manager)
    - [Setting up the simulation configuration file](#setting-up-the-simulation-configuration-file)
    - [Starting the first simulation run](#starting-the-first-simulation-run)
- [Running EC scenario demo simulation](#running-ec-scenario-demo-simulation)
- [Running a new simulation](#running-a-new-simulation)
- [Following a running simulation](#following-a-running-simulation)
- [Stopping a running simulation](#stopping-a-running-simulation)

These instructions assume that the core platform has been installed using the instructions given in the page [platform_installation.md](platform_installation.md).
All the files mentioned in these instructions are found in the Platform Manager repository, i.e. in the `platform/platform-manager` folder if the platform installation instruction were followed.

Current version of Platform Manager can only start one simulation run at a time. I.e., Platform Manager is given the simulation run configuration at the startup and after finishing the simulation start procedures Platform Manager closes itself.

## Running first test simulation

To test that the core platform has been installed properly, a simple test simulation configuration has been provided.
This configuration involves 3 dummy components in addition to the Simulation Manager and Log Writer instances that are always included in every simulation run.

### Setting up the environment parameters for the Platform Manager

Before launching the Platform Manager, it needs to be given the connection parameters to the RabbitMQ message bus and the Mongo database. There are also some other parameters that can be changes.
These are set in 3 environment variable files: `rabbitmq.env`, `mongodb_env` and `common.env`.

- The parameters for the RabbitMQ connection, `rabbitmq.env`, should be the same as those that were given for the Log Writer instance listening to the management instance during the platform installation in the file, `background/env/components_logwriter.env`.
    - `RABBITMQ_HOST` is the host name for the RabbitMQ message bus, use `rabbitmq` to use the local RabbitMQ instance started during the platform installation process
    - `RABBITMQ_PORT` is the port number for the RabbitMQ message bus (5672 is the default)
    - `RABBITMQ_LOGIN` is the username for the RabbitMQ access
    - `RABBITMQ_PASSWORD` is the password for the RabbitMQ access
    - `RABBITMQ_SSL` should be either `false` or `true` depending on whether SSL connection is used with the RabbitMQ message bus. For the local message bus it must be `false`, while the CyberLab message bus requires `true`.
- The parameters for the MongoDB connection are given in the file  `mongodb.env` and they should be the as those that were given for the Logging System during the platform installation in the file, `background/env/components_mongodb.env`.
    - `MONGO_HOST` is the host name for the Mongo database, use `mongodb` to use the local MongoDB instance started during the platform installation process
    - `MONGO_PORT` is the port number for the MongoDB (27017 is the default)
    - `MONGODB_USERNAME` must be an username that has write access to the database `logs`, this can be the same admin user that was used during the installation process
    - `MONGODB_PASSWORD` must be the password for the given user in the MongoDB
    - `MONGO_ADMIN` must be either `true` or `false`. If the given user does not have admin access, this should be `false`, otherwise, it can be left as `true`.
- Some general parameters used by the Platform Manager are set in the file `common.env`. At this point the only setting that might need a change is
    - `SIMULATION_LOG_LEVEL` should be a 10 (debug), 20 (info), 30 (warning), 40 (error) or 50 (critical). It sets the logging level for the core components. With the default logging level of 20 no debug level information is logged at all. If there is some problems when trying to run simulations it might be a good idea to set the logging level to 10 in order to get more information.
    - There is a script that should be used to start the Platform Manager that will automatically change the simulation configuration file name, so that should not be edited manually.

### Setting up the simulation configuration file

The simulation run specific parameters are given in a separate configuration file that uses YAML format. For the first test run, a ready-made configuration file, [simulation-configuration-test.yml](simulation-configuration-test.yml) has been made. The configuration file defines

- the simulation metadata: the name and description for the simulation run as well as the start time for the first epoch, epoch length and the maximum number of epochs in the simulation run
- the components participating in the simulation run and their individual parameters

For the first test simulation, the configuration file can be left as it is.

### Starting the first simulation run

To start the first test simulation, using Bash compatible terminal (Git Bash in Windows) navigate to the `platform-manager` folder and use the command

```bash
source start_simulation.sh simulation_configuration_test.yml
```

If everything worked properly, you should see something like:

```text
platform-manager    | 2020-12-14T16:26:52.677 ---     INFO --- Start message for simulation 'Test simulation' sent to management exchange.
platform-manager    | 2020-12-14T16:26:52.678 ---     INFO --- Simulation 'Test simulation' started successfully using id: 2020-12-14T16:26:46.390Z
platform-manager    | 2020-12-14T16:26:52.678 ---     INFO --- Follow the simulation by using the command:
platform-manager    |     source follow_simulation.sh 00
platform-manager    | 2020-12-14T16:26:52.678 ---     INFO --- Alternatively, the simulation manager logs can by viewed by:
platform-manager    |     docker logs --follow Sim00_simulation_manager
platform-manager    | 2020-12-14T16:26:52.678 ---     INFO --- Stopping the platform manager.
```

See the [Following a running simulation](#following-a-running-simulation) section on more details about following the output from the running simulation.

The Log Reader, be default at [http://localhost:8080](http://localhost:8080) can also be used to view the messages.

- `http://localhost:8080/simulations/<simulation_id>` should show the metadata for the test simulation
- `http://localhost:8080/simulations/<simulation_id>/messages` should show all the messages for the test simulation in the order of their arrival
- `http://localhost:8080/simulations/<simulation_id>/messages?topic=Start` should show only the start message for the test simulation

In the above, replace `<simulation_id>` with the id given by the Platform manager. In the earlier output, the simulation id would be `2020-12-14T16:26:46.390Z`. See the Log Reader API documentation page for more details.

## Running EC scenario demo simulation

## Running a new simulation

The simulation component types that Platform Manager supports are defined in the files `supported_component_core.json` and `supported_component_domain.json`. The core components that are used in the first test simulation have been predefined and this these files do not need any modification for the first simulation run.

## Following a running simulation

## Stopping a running simulation
