# Installing the Simulation Platform

## Prerequisites

- Git
    - For fetching the source code from the remote repositories
    - [https://git-scm.com/downloads](https://git-scm.com/downloads)
- Bash
    - For running the helper scripts.
    - [https://www.gnu.org/software/bash/](https://www.gnu.org/software/bash/)
    - For Windows, Bash is included with the Git for Windows, for other operating systems it is likely available by default.
- Docker and Docker Compose
    - For running the dynamically deployed components for the simulations.
    - For running the local RabbitMQ message bus as well as the local MongoDB database.
    - For installing Docker: [https://docs.docker.com/get-docker/](https://docs.docker.com/get-docker/)
    - For installing Docker Compose: [https://docs.docker.com/compose/install/](https://docs.docker.com/compose/install/)
- Access rights to the GitLab server that is used to host the source code
    - For gaining access see [https://wiki.eduuni.fi/pages/viewpage.action?pageId=149657074](https://wiki.eduuni.fi/pages/viewpage.action?pageId=149657074)

Some simulation components might have other requirements. For those, see the component specific documentation.

## Installing the core components

1. Create a folder for the core components. Each core component will have its own subfolder under this folder. In these instructions this main folder is named `platform`.
    - Note, that to avoid repeatedly typing the username and the password for the GitLab server when fetching the source code, you can use command

        ```bash
        git config --global credential.helper store
        ```

        This will store the username and password in plain text to file `.git-credentials` in your home directory after the first time you have given them.
2. Fetch the core component repositories.
    1. There are 4 repositories that are needed for the core components: simulation-manager, logwriter, logreader and platform-manager. The platform-manager repository contains a script that can be used to fetch all 4 repositories with a single command: [fetch_platform_code.sh](https://git.ain.rd.tut.fi/procemplus/platform-manager/-/blob/master/fetch_platform_code.sh).

        If you do not want to use the script and instead want to fetch each of the repositories individually, move to the step 2.6.
    2. Copy the `fetch_platform_code.sh` script file to the `platform` folder for example by downloading it from the GitLab using the browser interface.
    3. Using Git Bash (in Windows) or other terminal that supports Bash navigate to the `platform` folder.
        - In the terminal you can navigate inside a folder using command: `cd <folder_name>`
        - To navigate to the parent folder, use command: `cd ..`
        - To check your current folder, use command: `pwd`
        - To list the files and subfolder in the current folder, use command: `ls -l`
    4. Run the fetch script using the command

        ```bash
        source fetch_platform_code.sh
        ```

        Answer "y" when prompted to start fetching the source code.

        If prompted, give your username and password for the GitLab server.

    5. If everything went alright, the script should print the following at the end:

        ```text
        OK: simulation-manager repository seems ok.
        OK: logwriter repository seems ok.
        OK: logreader repository seems ok.
        OK: platform-manager repository seems ok.
        ```

        After receiving the above printout you can skip the rest of the step 2 and move to the step 3.
    6. Fetch the source code for the Simulation Manager.
        1. Using Git Bash (in Windows) or other terminal that supports Bash navigate to the `platform` folder.
            - In the terminal you can navigate inside a folder using command: `cd <folder_name>`
            - To navigate to the parent folder, use command: `cd ..`
            - To check your current folder, use command: `pwd`
            - To list the files and subfolder in the current folder, use command: `ls -l`
        2. Clone the Simulation Manager repository using the command

            ```bash
            git -c http.sslVerify=false clone --recursive https://git.ain.rd.tut.fi/procemplus/simulation-manager.git
            ```

            If prompted, give your username and password for the GitLab server. The GitLab server uses a self-signed certificate which is why the http.sslVerify option is needed in  the clone command.
        3. Check that the repository was cloned properly by checking that the `simulation-tools` subfolder is not empty using the command:

            ```bash
            ls -l simulation-manager/simulation-tools
            ```

        4. Optionally turn off the certificate verification for the Simulation Manager repository. With this you can avoid giving the http.sslVerify=false option every time you fetch new updates for the Simulation Manager. The verification can be turned off for the Simulation Manager repository and its submodule simulation-tools with the commands:

            ```bash
            cd simulation-manager
            git config http.sslVerify false --local
            cd simulation-tools
            git config http.sslVerify false --local
            ```

    7. Fetch the source code for the Log Writer
        1. Using Git Bash (in Windows) or other terminal that supports Bash navigate to the `platform` folder.
        2. Clone the Log Writer repository using the command

            ```bash
            git -c http.sslVerify=false clone --recursive https://git.ain.rd.tut.fi/procemplus/logwriter.git
            ```

        3. Check that the repository was cloned properly by checking that the `simulation-tools` subfolder is not empty using the command:

            ```bash
            ls -l logwriter/simulation-tools
            ```

        4. Optionally turn off the certificate verification for the Log Writer repository and its submodule simulation-tools with the commands:

            ```bash
            cd logwriter
            git config http.sslVerify false --local
            cd simulation-tools
            git config http.sslVerify false --local
            ```

    8. Fetch the source code for the Log Reader
        1. Using Git Bash (in Windows) or other terminal that supports Bash navigate to the `platform` folder.
        2. Clone the Log Reader repository using the command

            ```bash
            git -c http.sslVerify=false clone https://git.ain.rd.tut.fi/procemplus/logreader.git
            ```

        3. Check that the repository was cloned properly by checking that the `LogReader` subfolder is not empty using the command:

            ```bash
            ls -l logreader/LogReader
            ```

        4. Optionally turn off the certificate verification for the Log Reader repository with the commands:

            ```bash
            cd logreader
            git config http.sslVerify false --local
            ```

    9. Fetch the source code for the Platform Manager
        1. Using Git Bash (in Windows) or other terminal that supports Bash navigate to the `platform` folder.
        2. Clone the Platform Manager repository using the command

            ```bash
            git -c http.sslVerify=false clone --recursive https://git.ain.rd.tut.fi/procemplus/platform-manager.git
            ```

        3. Check that the repository was cloned properly by checking that the `simulation-tools` subfolder is not empty using the command:

            ```bash
            ls -l platform-manager/simulation-tools
            ```

        4. Optionally turn off the certificate verification for the Platform Manager repository and its submodule simulation-tools with the commands:

            ```bash
            cd platform-manager
            git config http.sslVerify false --local
            cd simulation-tools
            git config http.sslVerify false --local
            ```

3. Build the Docker images for the core components and start the background components, i.e. local RabbitMQ instance, local MongoDB instance, a Log Reader instance and a Log Writer instance for listening to the management exchange.
    1. Check that all core code repositories have been cloned. At this point you should have a folder structure:

        ```text
        platform
        ----logreader
        ----logwriter
        ----platform-manager
        ----simulation-manager
        ```

    2. Modify the RabbitMQ settings.
        - All the files mentioned in this and the following sections can be opened and modified by any text editor, for example Notepad++.
        1. The username and password for the local RabbitMQ instance are set in the file `platform-manager/background/env/rabbitmq.env`.
            - `RABBITMQ_DEFAULT_USER` is the username for the local RabbitMQ instance
            - `RABBITMQ_DEFAULT_PASS` is the password for the local RabbitMQ instance
        2. The corresponding username and password for the use of the Log Writer instance are given in the file `platform-manager/background/env/components_logwriter.env`.
            - When using the local RabbitMQ instance, only the following two settings need to be modified.
            - `RABBITMQ_LOGIN` is the username for RabbitMQ access for Log Writer. When using the local RabbitMQ instance, this must correspond to the username set in the previous step.
            - `RABBITMQ_PASSWORD` is the password for RabbitMQ access for Log Writer. When using the local RabbitMQ instance, this must correspond to the password set in the previous step.
            - If you are using a different RabbitMQ instance than the local one, for example the CyberLab RabbitMQ, you need to also modify the `RABBITMQ_HOST`, `RABBITMQ_PORT` and `RABBITMQ_SSL` settings to gain the access. In this case the username and password must correspond to the other RabbitMQ instance and can be different from those set in the previous step.
    3. Modify the MongoDB settings.
        1. The admin username and password for the local MongoDB instance are set in the file `platform-manager/background/env/mongodb.env`.
            - `MONGO_INITDB_ROOT_USERNAME` is the admin username for the local MongoDB instance
            - `MONGO_INITDB_ROOT_PASSWORD` is the admin password for the local MongoDB instance
        2. The corresponding username and password for the use of Log Reader and Log Writer are given in file `platform-manager/background/env/components_mongodb.env`.
            - `MONGODB_USERNAME` must correspond to the admin username set in the previous step
            - `MONGODB_PASSWORD` must correspond to the admin password set in the previous step
            - For now, the Log Reader requires MongoDB user account that has admin privileges. The Log Writer would also work with an user account that has writing privileges for the logs database.
        3. Optionally, to use Mongo Express which can be used to view the database using a web browser, the corresponding username and password are given in the file `platform-manager/background/env/mongo_express.env`.
           - `ME_CONFIG_MONGODB_ADMINUSERNAME` must correspond to the admin username set in the step 6.3.1.
           - `ME_CONFIG_MONGODB_ADMINPASSWORD` must correspond to the admin password set in the step 6.3.1.
    4. Build the Docker images for the core components and start the background components.
        1. Using Git Bash (in Windows) or other terminal that supports Bash navigate to the `platform/platform-manager` folder.
        2. Run the platform core setup script to build the images and start the background components:

            ```bash
            source platform_core_setup.sh
            ```

            You can look at the file `platform/platform-manager/platform_core_setup.sh` to see the exact commands that are used in each step of the script.
        - Running the setup script for the first time will take a couple of minutes.
4. Check that all the Docker images for the core components have been created.
    - To list the built Docker images run the command

        ```bash
        docker images
        ```

        You should have at least the following images: `log_reader`, `log_writer`, `platform_manager`, `simulation_manager` and `dummy`. An example listing is given below:

        ```text
        REPOSITORY               TAG                  IMAGE ID       CREATED         SIZE
        dummy                    0.5                  846f16b145d1   2 minutes ago   1.19GB
        simulation_manager       0.5                  bb0f168c26aa   3 minutes ago   887MB
        log_reader               0.5                  be8a78536c44   4 minutes ago   952MB
        log_writer               0.5                  e0b251c6657a   5 minutes ago   891MB
        platform_manager         0.5                  9770108deed7   5 minutes ago   903MB
        ...
        ```

5. Check that all the background components have been started.
    - To list all the running Docker containers run the command

        ```bash
        docker ps
        ```

        You should have at least the following containers running: `rabbitmq`, `mongodb`, `log_reader` and `log_writer_management`. An example listing is given below (the command and ports column have been removed from the output):

      ```text
      CONTAINER ID   IMAGE                       CREATED          STATUS          NAMES
      5543e00b7a0f   log_reader:0.5              55 seconds ago   Up 51 seconds   log_reader
      9e3e117e6b30   mongo-express:0.54.0        55 seconds ago   Up 51 seconds   mongo_express
      41e60349dc22   log_writer:0.5              55 seconds ago   Up 51 seconds   log_writer_management
      1833b308ccb4   mongo:4.2.7                 56 seconds ago   Up 54 seconds   mongodb
      9ed153b4bbd6   rabbitmq:3.8.4-management   56 seconds ago   Up 55 seconds   rabbitmq
      ```

6. Check that the Log Writer instance listening to the management exchange is running properly.
    - If you are using the local RabbitMQ instance, it might happen that Log Writer instance is started before the RabbitMQ was ready and that can cause Log Writer to stop listening to the message bus. To check the log output from the Log Writer instance use the command

        ```bash
        docker logs log_writer_management
        ```

    - If at the beginning of the listing you see a line with "Connect call failed" followed by "Closing listener for topics: '#'" in the next line, the Log Writer instance is not working properly. To fix this, stop the Log Writer with command

        ```bash
        docker stop log_writer_management
        ```

    and run the platform core setup script from step 6.4 again. After running the script check the Log Writer output again to see if it started without connection errors this time.
7. Check that the Log Reader is running.
    - The Log Reader should be running on localhost at port 8080. To check that it is responding use a browser to check that you can see the user interface page at the address [http://localhost:8080](http://localhost:8080).
    - If the Mongo database was just deployed, it should be empty at this point. The call to list the simulation metadata from all simulations, [http://localhost:8080/simulations](http://localhost:8080/simulations) should return an empty list with an empty database.
    - If you setup the Mongo Express, it can be accessed at the address [http://localhost:8081](http://localhost:8081).
        - Through the Mongo Express, you get admin access to the database, so care should be taken when making any changes to the database contents.
    - If you are using the local RabbitMQ instance, you can access the RabbitMQ Management Plugin at the address [http://localhost:15672](http://localhost:15672).
