# Running simulations

<!-- no toc -->
- [Running first test simulation](#running-first-test-simulation)
    - [Setting up the environment parameters for the Platform Manager](#setting-up-the-environment-parameters-for-the-platform-manager)
    - [Setting up the simulation configuration file](#setting-up-the-simulation-configuration-file)
    - [Starting the first simulation run](#starting-the-first-simulation-run)
- [Running EC scenario demo simulation](#running-ec-scenario-demo-simulation)
    - [Installing the domain component](#installing-the-domain-component)
    - [Starting the simulation run](#starting-the-simulation-run)
- [Running a new simulation](#running-a-new-simulation)
    - [Installing a new domain component](#installing-a-new-domain-component)
    - [Adding a new component type to the domain build script](#adding-a-new-component-type-to-the-domain-build-script)
    - [Registering new component type to the Platform manager](#registering-new-component-type-to-the-platform-manager)
    - [Building all the components](#building-all-the-components)
    - [Specifying the simulation configuration file](#specifying-the-simulation-configuration-file)
    - [Starting a new simulation run](#starting-a-new-simulation-run)
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

To start the first test simulation, use Bash compatible terminal (Git Bash in Windows) to navigate to the `platform-manager` folder and use the command

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

In the above, replace `<simulation_id>` with the id given by the Platform manager. In the earlier output, the simulation id would be `2020-12-14T16:26:46.390Z`. See the Log Reader API documentation page for more details about the using the API.

## Running EC scenario demo simulation

After successfully running the test simulation, the next step is to run a simulation with at least one domain component. The Energy Community (EC) demo scenario uses the dynamically deployed StaticTimeSeriesResource components along with the core components. The scenario is defined at the wiki page [Energy Community (EC)](https://wiki.eduuni.fi/pages/viewpage.action?pageId=171974859).

### Installing the domain component

To be able to use the StaticTimeSeriesResource component in a simulation run, it must first be installed. Use the following steps to make it available for the Platform Manager to use.

1. Using Bash compatible terminal (Git Bash in Windows) navigate to the `platform` folder (the folder under which the Platform Manager and all the other core components are installed).
2. Clone the StaticTimeSeriesResource repository using the command

    ```bash
    git -c http.sslVerify=false clone --recursive https://git.ain.rd.tut.fi/procemplus/static-time-series-resource.git
    ```

3. A link to the Dockerfile for StaticTimeSeriesResource has already been included in the file `platform-manager/build/domain/docker-compose-build-domain.yml` and all the CSV files required for the EC demo scenario have been added to the folder `platform-manager/resources`. The static time series resource component type has also already been registered to the Platform Manager using file `platform-manager/supported_components_domain.json`. Thus the Docker image for the new domain component can be built using the ready-made script by using the command

    ```bash
    source platform_domain_setup.sh
    ```

    This script will run the docker-compose build command for the mentioned docker-compose file and make all the files in the resources folder available for the Platform Manager.

4. Check the simulation configuration file for the EC demo scenario. The ready-made configuration file can be found at [platform-manager/simulation_configuration_ec.yml](platform-manager/simulation_configuration_ec.yml). Note that the filenames for the CSV files that the static time series resource component uses are given as `/resources/<filename>` where the `<filename>` is the corresponding filename at the folder `/platform-manager/resources/`.

### Starting the simulation run

To start the EC demo scenario simulation, use Bash compatible terminal to navigate to the `platform-manager` folder and use the command

```bash
source start_simulation.sh simulation_configuration_ec.yml
```

After the simulation run has been completed you should be able to use the Log Reader to look through the messages used in the simulation. An example of creating a time series for the real powers for the generators in CSV format and the expected response is given below. `<simulation_id>` should be replaced by the simulation id given by the Platform Manager.

- Request:

    ```text
    http://localhost:8080/simulations/<simulation_id>/timeseries?attrs=RealPower&topic=ResourceState.Generator.%23&startEpoch=5&endEpoch=8&format=csv
    ```

- Response:

    ```csv
    epoch;timestamp;ResourceState.Generator.pv_large:pv_large.RealPower;ResourceState.Generator.pv_small:pv_small.RealPower
    5;2020-06-25T01:00:00Z;0.35;0.14
    6;2020-06-25T02:00:00Z;0.84;0.34
    7;2020-06-25T03:00:00Z;1.4;0.57
    8;2020-06-25T04:00:00Z;1.89;0.76
    ```

## Running a new simulation

...

### Installing a new domain component

...

### Adding a new component type to the domain build script

...

### Registering new component type to the Platform manager

...

### Building all the components

...

### Specifying the simulation configuration file

...

### Starting a new simulation run

...

## Following a running simulation

There are a couple of ways to follow a running simulation that has been started by the Platform Manager. Commands for the first 2 ways is given by Platform Manager after the simulation has been started.

- All the component outputs can be followed using a Bash script `follow_simulation.sh`.
- The output from the Simulation Manager can be followed using `docker logs` command.
- The logged messages from the simulation can be looked at using Log Reader even during the simulation. See the [Log Reader API](https://wiki.eduuni.fi/pages/viewpage.action?pageId=154452553) for more information.

The dynamically deployed Docker containers use a name format `Sim<id_number>_<component_name>` where `<id_number>` is the first available 2-digit number (00, 01, ..., 99) at the start of the simulation and `<component_name>` is the component name used in the simulation run. For example, for the first started simulation, the Simulation Manager container should be named `Sim00_simulation_manager`. The Platform Manager outputs the `<id_number>` for the started simulation run.

### Using follow simulation script

To start following the running simulation with colored output from all the dynamically deployed components using Bash compatible terminal navigate to the platform-manager repository and use the command:

```bash
source follow_simulation.sh <id_number>
```

where `<id_number>` is given by the Platform Manager after the simulation run has been started. The full command is also part of the Platform Manager output.

Note that due to the way this follow script has been implemented, it cannot be easily canceled and if you want to stop following the simulation the easiest way to do so is to close the terminal window.

### Using docker logs command

To follow the advancing of the simulation the output from the Simulation Manager can be followed using the command (can be used from any folder and does not require Bash compatible terminal, e.g. works also with Command Prompt in Windows):

```bash
docker logs --follow Sim<id_number>_simulation_manager
```

where `<id_number>` is given by the Platform Manager after the simulation run has been started. The full command is also part of the Platform Manager output.

Following the Simulation Manager output can be cancelled using the key combination `Ctrl+C`.

### Fetching log files after a simulation run

The dynamically deployed Docker containers are deleted after the simulation is finished, and thus the component outputs cannot be looked at using the follow simulation script or docker logs command after the simulation is finished.

After the simulation, the output from the components can be found stored in log files in a Docker volume called `simulation_logs` in the folder `/logs`. The log files can be fetched to a local folder using a Bash script `logs/copy_logs.hh`:

1. Navigate to the folder `logs` inside the platform-manager repository using a Bash compatible terminal.
2. Use the following command to copy all the log files to the `logs` folder:

    ```bash
    source copy_logs.sh
    ```

The filenames for the log files use the format `logfile_<component_name>.log`. Note that the files can contain outputs from multiple simulations. The latest outputs are at the end of log files.

## Stopping a running simulation

...
