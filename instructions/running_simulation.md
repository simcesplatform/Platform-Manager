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
    - [Making resource files available for the Platform Manager](#making-resource-files-available-for-the-platform-manager)
    - [Building Docker images for domain components](#building-docker-images-for-domain-components)
    - [Registering new component type to the Platform manager](#registering-new-component-type-to-the-platform-manager)
    - [Specifying the simulation configuration file](#specifying-the-simulation-configuration-file)
    - [Starting a new simulation run](#starting-a-new-simulation-run)
- [Following a running simulation](#following-a-running-simulation)
    - [Using follow simulation script](#using-follow-simulation-script)
    - [Using docker logs command](#using-docker-logs-command)
    - [Fetching log files after a simulation run](#fetching-log-files-after-a-simulation-run)
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

There are a couple steps before a simulation run using user developed components can be be started using the Platform Manager:

- All the components have to be installed.
    - With statically deployed components this also involves starting the component manually.
    - With dynamically deployed components this involves building the Docker image for the component. Also any static resource files (for example CSV files) have to be made available for the Platform Manager.
- All the components have to be registered to the Platform Manager.

After the component installation and registration a new simulation configuration file can be created and then used to start a new simulation run.

### Installing a new domain component

The source code for each component should have its own code repository at the [GitLab server](https://git.ain.rd.tut.fi/procemplus). The code repository should have instructions on how to fetch all the required source code for the component that should be followed. In general the command to clone the remote code repository and fetch the source code is:

```bash
git -c http.sslVerify=false clone --recursive https://git.ain.rd.tut.fi/procemplus/<component_name>.git
```

but depending on the component there might also be other requirements. `<component_name>` should be replaced by the repository name for the component, for example `static-time-series-resource` for the Static Time Series Resource component.

For statically deployed components the component code repository should also include instructions on how to install and start the component that should be followed.

A dynamically deployed component should include a Dockerfile that can be used to build the Docker image for the container. See the section [Building Docker images for domain components](#building-docker-images-for-domain-components) on how to build the Docker images for the dynamically deployed domain components.

### Making resource files available for the Platform Manager

Any resource file that is used by a dynamically deployed component during a simulation run, needs to be made available for the Platform Manager. Example for a resource file is the CSV file that is used as input with the Static Time Series Resource component.

Any resource files that are used by statically deployed components are not required to be accessible by the Platform Manager.

To make a resource file available for the Platform Manager:

1. Copy the resource file to the `resources` folder inside the `platform-manager` repository. The files can be either directly at the
resources folder (like the resource files for EC scenario demo) or inside a subfolder.
2. From the root folder of the `platform-manager` repository run the command:

    ```bash
    source platform_domain_setup.sh
    ```

Note that due to the limitation of the current Platform Manager implementation all the files included in the resources folder will be made available for all the dynamically deployed domain components. Also, to avoid errors any file that is currently being used in a running simulation should not be modified while the simulation is still running.

The command above also builds all the Docker images for the dynamically deployed domain components, so it could show some errors in the output if the next section [Building Docker images for domain components](#building-docker-images-for-domain-components) has not yet been handled.

### Building Docker images for domain components

If the component that should be dynamically deployed does not have a ready-made Dockerfile it can be created using the template file [Dockerfile-template](Dockerfile-template) as a starting point. It is based on the Dockerfile for the Static Time Series Resource component. The template file contains comment lines that should help creating a Dockerfile for a new component. The new Dockerfile should be placed at the root folder of the component source code.

The simplest way to build the required Docker images is to add or modify the existing docker-compose build file, `build/domain/docker-compose-build-domain.yml`. By default the file contains the block for the Static Time Series Resource component that is shown below:

```yaml
static-time-series-resource:
    image: static-time-series-resource:0.5
    build:
        context: ../../../static-time-series-resource
        dockerfile: Dockerfile
```

For each dynamically deployed component there should be its own block with a similar format:

```yaml
<component_name>:
    image: <component_name>:<version_tag>
    build:
        context: <path_to_component_folder>
        dockerfile: <docker_filename>
```

- `<component_name>` is the component name, can be the same as the folder name for the repository, for example `static-time-series-resource` for the Static Time Series Resource component
- `<version_tag>` is the version number for the component. This can be chosen freely but it must be the same as what is given when registering the component to the Platform Manager. By default the Static Time Series Resource component is using version `0.5`.
- `<path_to_component_folder>` is the path to the component folder where the Dockerfile is found. In the Static Time Series Resource example a relative path is used.
- `<docker_filename>` is the filename for the Dockerfile in the folder given in the previous setting.

If the docker-compose file contains one or more components that has not been installed, the 5 lines containing the component block can be commented out by adding the number sign (or hashtag) character, #, to the beginning of the lines in within the block. For example if the Static Time Series Resource component is not installed and will not be needed those lines can be commented out when editing the docker-compose file.

Once the docker-compose file has been modified, the Docker images that the Platform Manager will use when starting a simulation run can be built by using the following command from the root folder of the Platform Manager repository:

```bash
source platform_domain_setup.sh
```

After running the script the existing Docker images can be checked using the command:

```bash
docker images
```

In the output listing there should be a line for each of the included components. Example listing when including the Static Time Series Resource using the above example (output lines for the other images are omitted):

```text
REPOSITORY                    TAG                  IMAGE ID       CREATED          SIZE
static-time-series-resource   0.5                  ac5e9e9f5461   28 seconds ago   937MB
...
```

### Registering new component type to the Platform manager

Before Platform Manager can be used to start a new simulation that includes a new domain component, the new component type has to be registered to the Platform Manager. The registering is done to allow the Platform Manager to know whether the new component is a statically or dynamically deployed component and in the latter case to also know which Docker image to use when deploying the dynamic component. The registration process also allows the user to mark some parameters as required so that the Platform Manager does not start a new simulation run in vain if essential information is missing from the simulation configuration.

The domain components are registered for the Platform Manager in the JSON file [supported_components_domain.json](supported_components_domain.json) that is found at the root folder of the `platform-manager`repository. In the file, registrations for the statically deployed Grid component and dynamically deployed Static Time Series Resource component have been made by default. The attribute definitions should match to the ones given in the process parameter block for the component in the [Start message](https://wiki.eduuni.fi/pages/viewpage.action?pageId=164959964).

The supported component file should be valid JSON object with keys being the component type names and the values being registration block for the component.

The possible attributes for the component registration block:

- `Type` (required)
    - either `"dynamic"` or `"static"` depending on the deployment type of the component
- `DockerImage` (required for dynamic component, not needed for static component)
    - the Docker image name including the tag for a dynamically deployed component
    - this should match to what was used in file `build/domain/docker-compose-build-domain.yml` when building the Docker images for the domain components
- `Description` (optional)
    - description for the component
    - not yet used anywhere in the current version
- `Attributes` (optional)
    - key-value list of the registered attributes for the component
    - each key should be the attribute name that is used in the Start message in this components process parameters block
    - each value should be an attribute block where each block can have the following attributes:
        - `Optional` (optional)
            - either `true` or `false` depending on whether the attribute can be omitted or not
            - the default value is `false`, i.e. the attribute is required
            - if a component is not given all the required attributes in the simulation configuration file, the simulation will not be started
            - for optional attribute, the value in the `Default` field is used if the attribute is not included in the simulation configuration file
        - `Default` (required if attribute is optional, otherwise, not needed)
            - the value used for the attribute if the attribute is not included in the simulation configuration file
        - `Environment` (optional, not needed with static components)
            - the environment variable that is set when this attribute is used
            - the default name for the environment variable is the same as the attribute name in the key-value list
    - any attribute that is included in the key-value list will always be included in the Start message process parameter block (either with the default value or the value given in the simulation configuration file)
    - any attribute that is not included in the key-value list but is included as an attribute in the simulation configuration file will also be included in the Start message

After the file `supported_components_domain.json` has been modified to include all the required domain components, the Dockerfile for the Platform Manager has to be built again, otherwise the changes will not be included when starting a new simulation. This can be done by using the same command that was used in the installation process to build the core components. In the root folder of the `platform-manager` repository, use command:

```bash
source platform_setup_core.sh
```

### Specifying the simulation configuration file

TODO: description about the simulation configuration file

Example simulation configuration file for a simulation where a Grid component has been added to the EC scenario can be found at [simulation_configuration_grid.yml](simulation_configuration_grid.yml):

```yaml
Simulation:
    Name: "Energy community with Grid demo"
    Description: "This scenario includes a grid simulation with OpenDSS."
    InitialStartTime: "2020-06-25T00:00:00.000+03:00"
    EpochLength: 3600
    MaxEpochCount: 24

    # Optional settings for the Simulation Manager
    ManagerName: "Manager"
    EpochTimerInterval: 20
    MaxEpochResendCount: 2

    # Optional settings for the Log Writer
    MessageBufferMaxDocumentCount: 10
    MessageBufferMaxInterval: 5.0

Components:  # these are the names of the component implementations (defined in the supported components JSON file)
    # duplication_count is reserved keyword and cannot be used as a parameter for a component instance

    Grid:                            # The statistically deployed Grid component type
        Grid:                        # The name of the Grid instance in the simulation run
            ModelName: "EC_Network"  # The grid model name that will be sent as a part of the Start message
            Symmetrical: false

    Dummy:                        # The dynamically deployed Dummy component to slow down the simulation
        dummy:                    # The base name for the Dummy components
            duplication_count: 2  # Create 2 components, named dummy_1 and dummy_2, with otherwise identical parameters
            MinSleepTime: 1
            MaxSleepTime: 5

    StaticTimeSeriesResource:    # The dynamically deployed Static Time Series Resource component
        load1:                   # The name of this StaticTimeSeriesResource instance in the simulation run
            ResourceType: "Load"                       # corresponds to RESOURCE_TYPE environment variable
            ResourceStateFile: "/resources/Load1.csv"  # corresponds to RESOURCE_STATE_FILE environment variable
        load2:
            ResourceType: "Load"
            ResourceStateFile: "/resources/Load2.csv"
        load3:
            ResourceType: "Load"
            ResourceStateFile: "/resources/Load3.csv"
        load4:
            ResourceType: "Load"
            ResourceStateFile: "/resources/Load4.csv"
        ev:
            ResourceType: "Load"
            ResourceStateFile: "/resources/EV.csv"
        pv_small:
            ResourceType: "Generator"
            ResourceStateFile: "/resources/PV_small.csv"
        pv_large:
            ResourceType: "Generator"
            ResourceStateFile: "/resources/PV_large.csv"
```

Note that while string values can be in most cases be given without double quotes in YAML files they are consistently used in the above example to avoid any possible edge cases where the strings without quotes might be interpreted as something other than a single string value.
A breakdown of parameters set in the example configuration using the knowledge of the default values from [Start (message)](https://wiki.eduuni.fi/pages/viewpage.action?pageId=164959964) and the supported component settings from [supported_components_core.json](supported_components_core.json) and [supported_components_domain.json](supported_components_domain.json):

- The required overall parameters
    - The simulation name is set to `"Energy community with Grid demo"`
    - The description for the simulation is set to `"This scenario includes a grid simulation with OpenDSS."`
    - The start time for the first epoch in set to `"2020-06-25T00:00:00.000+03:00"` or to "2020-06-24T21:00:00.000Z" in UTC time
    - The duration of each epoch is set to `3600` seconds, i.e. 1 hour
    - Maximum number of epochs is set to `24`, i.e. the simulation will last 24 hours or 1 day
- The optional overall parameters
    - The Simulation Manager name in the simulation is set to `"Manager"`, the default name would be `"simulation_manager"`
    - The time duration until Simulation Manager tries to resend the epoch message is set to `20` seconds, the default duration would be `120` seconds
    - The maximum number of epoch resends the Simulation Manager is allowed to try before ending the simulation is set to `2` epoch resends, the default would be `5` epoch resends
    - The maximum number of messages the buffer in Log Writer can have is set to `10` messages, the default would be `20` messages
    - The maximum time interval until the message buffer in Log Writer is cleared is set to `5` seconds, the default would be `10` seconds
- The simulation will have 1 Grid component participating that is statically deployed
    - The name of the Grid component is set to `"Grid"`
    - The `ModelName` parameter for the Grid is set to `"EC_Network"`
    - The `Symmetrical` parameter for the Grid is set to the boolean value `false`
    - The optional parameter `MaxControlCount` for the Grid will be set to the default value `15`
    - The optional parameter `ModelVoltageBand` for the Grid will be set to the default value `0.15`
- The simulation will have 2 Dummy components dynamically deployed by Platform Manager
    - Using the `duplicate_count` attribute there will be `2` Dummy components with identical parameters created. The component names will be in the format `<basename>_<number>`, i.e. `"dummy_1"` and `"dummy_2"` since the base name is set to `"dummy"`
    - The `MinSleepTime` parameter for the Dummy components are set to `1`
    - The `MaxSleepTime` parameter for the Dummy components are set to `5`
    - All the other parameters for the Dummy components, i.e. `WarningChance`, `SendMissChance`, `ReceiveMissChance` and `ErrorChance`, are set to the their default value of `0.0`
- The simulation will have 7 Static Time Series Resource components that will be dynamically deployed by the Platform Manager
    - The resource components representing a load are named `"load1"` `"load2"` `"load3"` `"load4"` and `"ev"`
        - The `ResourceType` parameter is set to `"Load"` in all load components
        - The `ResourceStateFile` parameter is set to the filename where the resource component will find it after it has been deployed, for example the filename for the `"load1"` component is set to `"/resources/Load1.csv"`
            - Note, that the filename given here refer to the filenames inside the Docker containers and thus they all include `"/resources"` at the beginning, since that is where they will be found when included according to the instruction in the section [Making resource files available for the Platform Manager](#making-resource-files-available-for-the-platform-manager).
    - The resource components representing a generator are named `"pv_small"` and `"pv_large"`
        - The `ResourceType` parameter is set to `"Generator"` in both generator components
        - The `ResourceStateFile` parameter is set to the filename where the resource component will find it after it has been deployed, for example the filename for the `"pv_small"` component is set to `"/resources/PV_small.csv"`

TODO: create a template configuration file

TODO: full specification for the configuration file

### Starting a new simulation run

To start a new simulation eun, use Bash compatible terminal to navigate to the `platform-manager` folder and use the command

```bash
source start_simulation.sh <configuration_file>
```

where `<configuration_file>` is the filename containing YAML configuration for the simulation run.

## Following a running simulation

There are a couple of ways to follow a running simulation that has been started by the Platform Manager. Commands for the first 2 ways is given by Platform Manager after the simulation has been started.

- All the component outputs can be followed using a Bash script `follow_simulation.sh`.
- The output from the Simulation Manager can be followed using `docker logs` command.
- The logged messages from the simulation can be looked at using Log Reader even during the simulation. See the [Log Reader API](https://wiki.eduuni.fi/pages/viewpage.action?pageId=154452553) for more information.

The dynamically deployed Docker containers use a name format `Sim<id_number>_<component_name>` where `<id_number>` is the first available 2-digit number (00, 01, ..., 99) at the start of the simulation and `<component_name>` is the component name used in the simulation run. For example, for the first started simulation, the Simulation Manager container should be named `Sim00_simulation_manager`. The Platform Manager outputs the `<id_number>` for the started simulation run.

### Using follow simulation script

To start following the running simulation with colored output from all the dynamically deployed components, using Bash compatible terminal navigate to the platform-manager repository and use the command:

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

To stop a running simulation by closing all the dynamically deployed containers,
using Bash compatible terminal navigate to the platform-manager repository and use the command:

```bash
source stop_simulation.sh <id_number>
```

where `<id_number>` is given by the Platform Manager after the simulation was started.

You can use command

```bash
docker ps --filter name=Sim --format "{{.Names}}"
```

to see all the currently running containers started by the Platform Manager.

Note that this will only stop the dynamically deployed components and does not affect the statically deployed components in any way.
