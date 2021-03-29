# Python Flask Ariadne Development Environment in Docker

I often work on projects or create projects that must be handed off to other developers once created. Having been on the receiving end of this, I know that it can be a huge time-suck to try to get a project started up locally with all the correct dependencies. A developer picking up an existing application often needs to get the app running quickly so they can target the new feature (or bug) that is the current need. Exploring local setup shouldn't be the bulk of time spent.

Additionally, when I am working on local dev, I want my dev environment to match the production environment as closely as possible. How many times has code worked in local only to fail in production because the environment is slightly different?

I recently had the great opportunity to create a GraphQL API in Python. I had experience in GraphQl, but none in Python. On that note please forgive anything I've done that doesn't seem "Pythonic"! I am still a learner of course and always striving to improve.

When designing the API, we decided that a GraphQl API best served the requirements. GraphQL vs Rest is a completely different discussion and outside of the scope of this article. To that end We decided to use Flask as the Server and Ariadne for the GraphQL. Ariadne's approach of "Schema First" seems to work better with GraphQl. Additionally, I was able to translate ideas I have from Elixir development to the app for faster development.

This app is using a PostgreSQL database but could be changed out to a different database. Changing out the database is outside of the scope of this article.

The code base for this article may be found at: [http://github/genui/python-flask-ariadne-api-starter](http://github/genui/python-flask-ariadne-api-starter). The repo may be used as a starting point for your own Python GraphQL API.

## Dependencies

- [Git](https://git-scm.com/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop) (`docker`)
- [Visual Studio Code](https://code.visualstudio.com/) (`code`) - this is optional, but sure makes everything a lot easier.
- A PostgreSQL server. See [Running PostgreSQL in Docker](#running-postgresql-in-docker) for more info.

The Setup of the Python app itself is also outside of the scope of this article. Using the example app, we know that the app has a script or command to start the server. We will address how this script or command gets initialized later in the article.

## Running PostgreSQL in Docker

Setting up a Postgres server for development is outside of the scope of this article. For this app, I am using [postgres_docker](https://github.com/generalui/postgres_docker).

## Dockerfile

The app has two Dockerfiles. One for deployment and one for development. I wanted the development file to resemble the production file as much as possible. the reason for two files is that in development, I have a number of dependencies (for testing, linting, profiling, etc) that I didn't need or want in production. I also have a number of apps that I wanted available in the container for dev that I didn't need or want in production.

### Production Dockerfile

The production Dockerfile looks like:

[`Dockerfile`](./Dockerfile)

```Dockerfile
# Make the Python version into a variable so that it may be updated easily if / when needed. (ie "3.8")
ARG pythonVersion

# Start with a bare Alpine Linux to keep the container image small.
FROM tiangolo/uwsgi-nginx-flask:python${pythonVersion}-alpine

# Designate the `/app` folder inside the container as the working directory.
WORKDIR /app

# Copy only what's needed from the app codebase to the `/app` folder inside the container.
COPY ./requirements.txt ./app.py ./config.py ./setup.py ./uwsgi.ini /app/
COPY ./api/ /app/api
COPY ./migrations/ /app/migrations

# Execute everything under a single "RUN" to reduce the layer count.
# Upgrade pip
RUN pip install --upgrade pip && \
    # `libpq` is needed for Postgres commands.
    apk add --no-cache libpq && \
    # Install build tools for installing dependencies.
    apk add --no-cache --virtual .build-deps \
    gcc \
    musl-dev \
    postgresql-dev \
    linux-headers && \
    # Install the PyPI dependencies using pip
    pip install --no-cache-dir -r requirements.txt && \
    # Remove the build tools now that we are done with them.
    apk del --no-cache .build-deps
```

When the Docker container is built, the python image version must be passed in using the `--build-arg <variable_name>=<value>` flag. See: [https://docs.docker.com/engine/reference/builder/#arg](https://docs.docker.com/engine/reference/builder/#arg). This allows me to update the Python version easily if/when needed.

The App deploys with uWSGI for easy and secure deployment.

The code base is copied into the container and the requirements installed. There are some tools needed to help install the requirements. These are removed when no longer needed. Everything else needed for the app is already built into the container.

### Development Dockerfile

The development Dockerfile is similar to the production Dockerfile but with some additional apps and requirements installed just for dev. Again, I am trying to maintain parity between what is deployed in a release and what is run on the local dev machine.

Key similarities:

- Python version
- Running on Alpine
- Using the same code base
- Installing the same build tools for installing dependencies
- Building with the same `requirements.txt` file
- Removing the build tools after installing dependencies

[`Dockerfile-dev`](./Dockerfile-dev)

```Dockerfile
# Make the Python version into a variable so that it may be updated easily if / when needed. (ie "3.8")
ARG pythonVersion

# Using a python image itself so the app may be updated easily if / when needed. (ie "3.8")
# Start with a bare Alpine Linux to keep the container image small.
FROM python:${pythonVersion}-alpine

# Designate the `/app` folder inside the container as the working directory.
WORKDIR /app

# Copy the requirements (both prod and dev) files to the `/app` folder inside the container.
# Do this in a separate "COPY" so that the the image will update if either of these files change.
COPY ./requirements.txt ./requirements-dev.txt /app/
# Copy the code base to the work directory. This will ensure it is added to the volume.
COPY ./ /app/

# Execute everything under a single "RUN" to reduce the layer count.
# Upgrade pip
RUN pip install --upgrade pip && \
    # `libpq` is needed for Postgres commands.
    apk add --no-cache libpq \
    # These useful tools are only installed in the development environment.
    bash curl openssh git nodejs npm && \
    # Install `git-genui` for git commits.
    # This is only installed in the development environment.
    # See https://www.npmjs.com/package/git-genui
    npm install -g git-genui && \
    # Install build tools for installing dependencies.
    apk add --no-cache --virtual .build-deps \
    gcc \
    musl-dev \
    postgresql-dev \
    linux-headers && \
    # Install the PyPI dependencies using pip
    pip install --no-cache-dir -r requirements.txt && \
    # These are only installed in the development environment.
    pip install --no-cache-dir -r requirements-dev.txt && \
    # Remove the build tools now that we are done with them.
    apk del --no-cache .build-deps

# Inside the container, execute the Python script that starts the server.
# Only if `NO_AUTO_START` is NOT set.
# Otherwise, tail nothing so a process will continue and the container will run.
CMD ["bash", "-c", "if [ -z ${NO_AUTO_START} ]; then python /app/run.py; else tail -f /dev/null; fi"]
```

Of course the Docker files could be run as is with Docker cli. This would be just a bit ugly and complicated. I'll use docker-compose instead.

## Docker Compose

Using a docker compose file to start and stop the docker container allows much more configurability for my environment and app.

To find out more about the docker-compose file and the configuration options, see [https://docs.docker.com/compose/compose-file/compose-file-v3/](https://docs.docker.com/compose/compose-file/compose-file-v3/)

Here's a look at what is happening in the `docker-compose.yml` file that is being used for Dev.

[`docker-compose.yml`](./docker-compose.yml)

```yaml
version: "3.8"

services:
  api:
    env_file: ${DOT_ENV_FILE:-.env-none}
    # Ensure specific environment variables are ALWAYS available.
    environment:
      - FLASK_APP=${FLASK_APP:-app.py}
      - FLASK_ENV=${FLASK_ENV:-development}
      - FLASK_RUN_PORT=${FLASK_RUN_PORT:-5000}
      - LOG_TYPE=${LOG_TYPE:-}
      - NO_AUTO_START=${NO_AUTO_START:-}
      - POSTGRES_DB=${POSTGRES_DB:-pfaas_dev}
      - POSTGRES_DB_TEST=${POSTGRES_DB:-pfaas_test}
      - POSTGRES_HOST=${POSTGRES_HOST:-host.docker.internal}
      - POSTGRES_HOST_TEST=${POSTGRES_HOST_TEST:-host.docker.internal}
      - POSTGRES_PORT=${POSTGRES_PORT:-5432}
      - POSTGRES_PORT_TEST=${POSTGRES_PORT_TEST:-5432}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-docker}
      - POSTGRES_PASSWORD_TEST=${POSTGRES_PASSWORD_TEST:-docker}
      - POSTGRES_USER=${POSTGRES_USER:-postgres}
      - POSTGRES_USER_TEST=${POSTGRES_USER_TEST:-postgres}
      - PYTHONUNBUFFERED=1
      - PYTHON_VERSION=${PYTHON_VERSION:-3.8}
      - SECRET_KEY=${SECRET_KEY:-some_real_good_secret}
      - SNAKEVIZ_PORT=${SNAKEVIZ_PORT:-8020}
      - SSL_ENABLED=${SSL_ENABLED:-}
    build:
      context: ./
      dockerfile: Dockerfile-dev
      args:
        pythonVersion: ${PYTHON_VERSION:-3.8}
    container_name: python-flask-ariadne-api-starter
    image: python-flask-ariadne-api-starter:dev
    command:
      - "sh"
      - "-c"
      - "if [ -z ${NO_AUTO_START:-} ]; then python /app/run.py; else tail -f /dev/null; fi"
    ports:
      - ${FLASK_RUN_PORT:-5000}:${FLASK_RUN_PORT:-5000}
      - ${SNAKEVIZ_PORT:-8020}:${SNAKEVIZ_PORT:-8020}
    volumes:
      - .:/app:delegated
      - ~/.gitconfig:/root/.gitconfig:delegated
      - ~/.ssh:/root/.ssh:delegated
      - python-flask-ariadne-api-starter-dev-root-vol:/root:delegated
    logging:
      options:
        max-size: "10m"
        max-file: "3"
volumes:
  python-flask-ariadne-api-starter-dev-root-vol:
```

The docker compose file is counting on a number of environment variables being available. Defaults have been defined in the event the variables haven't been set.

Initially, the `DOT_ENV_FILE` denotes the name of a `.env` file to pick up environment variables from. If this environment variable hasn't been set, then the default `.env-none` file is use which intentionally has no environment variables set in it.

To override defaults, create a `.env-dev` file (modeled after the included `.env-SAMPLE` file) and set the desired override values. The path to this file MUST be set to the `DOT_ENV_FILE` variable. I have created a script that ensures this, but more on that later.

Some of the defaults in the `environment` option are set for this app. Values for `POSTGRES_DB` and `POSTGRES_DB_TEST`, the database names for dev and test respectively, are set for this app. You would change these defaults to values appropriate for your situation. The database host values are set by default to `host.docker.internal`. This allows the container to connect to `localhost` of the local machine and not localhost of the container. Note that this doesn't work in Linux. For linux to connect to the host machine's localhost, use `172.17.0.1` instead.

In the `build` option, I tell docker compose where to find the docker file and what its name is. I also pass the python version (defaults to 3.8).

I've added a container name and image name to help easily identify them on the local machine. I have named them `python-flask-ariadne-api-starter` for this app, but they could be named whatever is convenient. The image version is tagged simply `dev` as this image will be overwritten with changes.

The `command` option is executed in the container once the container is built. I have created an optional `NO_AUTO_START` variable that will be set (or not) in the container. If it is set to a truthy value, the container will NOT automatically start the server. This may be useful for starting the container and then entering the container to do all dev inside. The server may then be started inside the container and played with exclusively in the container context. More on this later. If `NO_AUTO_START` is set to a truthy value, then I execute `tail -f /dev/null`. This tails nothing but provides a process to run so that the container will keep running.

The `ports` option exposes ports inside the container to the outside machine. The `FLASK_RUN_PORT` is the port that the server will be running on. As localhost inside the container can't be accessed by the local browser, the port is exposed. This is also true for the `SNAKEVIZ_PORT` port, the port that the profiling info page is rendered on. Learn more about [SnakeViz](https://jiffyclub.github.io/snakeviz/).

The `volumes` option is very important in the development environment. We create a number of volumes here. All of them are delegated for better performance. This is geared towards developing INSIDE the container. See [Docker volumes: cached vs delegated](https://tkacz.pro/docker-volumes-cached-vs-delegated/). I create these 4 volumes:

- I map the local project directory to the working directory inside the container. Thus, changes made in the local are reflected inside the container and vice versa.

- I map the local `~/.gitconfig` file (in the user's home folder) to to the root user's home folder in the container. This supports git commands in the container as though you are operating on your local command line.

- I map the local `~/.ssh` folder (in the user's home folder) to to the root user's home folder in the container. This makes the local ssh keys available inside the container for git fetches, pulls and pushes.

- I map the entire root user's home folder in the container to a volume. We named the volume `python-flask-ariadne-api-starter-dev-root-vol` for this app to differentiate it from other volumes on the local, but you coould name it whatever is appropriate for your situation. Please note that the volume itself is defined at the bottom of the `docker-compose.yml` file under `volumes`.

  This volume persists any other files that are created inside the root user's home folder inside the container. Files like `.bashrc` and `.profile` can be very useful inside the container. Additionally, if VS Code is being used and the [Remote - Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension is being used, the VS Code server and installed extensions are stored there. These will persist between starts and stops and helps make opening a lot faster.

- The `logging` option limits the size of logs within the container. This ultimately helps with performance. If logs get too large, the container gets huge and can really slow down.

The `docker-compose.yml` file may be run on it's own to start the docker container, but I have created some convenience scripts that put everything in one place and simplify the process.

## Start

There is a magic `start.sh` script in the root of the project. Starting the app in dev is as simple as running

```sh
./start.sh
```

in the root of the project.

This will help set environment variables such as `DOT_ENV_FILE` by identifying if a `.env-dev` file exists or not. The script accepts a few flags:

- `-b` or `--build` - Pass this flag if you explicitly want to rebuild the image.

- `-r` or `--reset_env` - Pass this flag to reset environment variables back to defaults. Sometimes, I play around with environment variables and the values can get all crazy. This will reset them with one caveat in mind, it will read the values set in the `.env-dev` file. Clearing out this file will and passing this flag will completely reset the environment variables to defaults.

- `-n` or `--no_auto_start` - Pass this flag to start the container without starting the server. This may be useful for starting the container and then entering the container to do all dev inside. The server may then be started inside the container and played with exclusively in the container context. More on this later.

Here's a look at the `start.sh` script:

[`start.sh`](./start.sh)

```bash
#!/bin/bash

# Defined some useful colors for echo outputs.
# Use BLUE for informational.
BLUE="\033[1;34m"
# Use Green for a successful action.
GREEN="\033[0;32m"
# Use YELLOW for warning informational and initiating actions.
YELLOW="\033[1;33m"
# Use RED for error informational and extreme actions.
RED="\033[1;31m"
# No Color (used to stop or reset a color).
NC='\033[0m'

# By default, set these variables to false.
build=false
no_auto_start=false
reset=false

# Checks if a specific param has been passed to the script.
has_param() {
    local term="$1"
    shift
    for arg; do
        if [[ $arg == "$term" ]]; then
            return 0
        fi
    done
    return 1
}

# If the `-b or --build` flag is passed, set build to true.
if has_param '-b' "$@" || has_param '--build' "$@"
then
    >&2 echo -e "${BLUE}Build requested${NC}"
    build=true
fi

# If the `-n or --no_auto_start` flag is passed, set no_auto_start to true.
if has_param '-n' "$@" || has_param '--no_auto_start' "$@"
then
    >&2 echo -e "${BLUE}No auto start requested${NC}"
    no_auto_start=true
fi

# If the `-r or --reset_env` flag is passed, set reset to true.
if has_param '-r' "$@" || has_param '--reset_env' "$@"
then
    >&2 echo -e "${BLUE}Reset environemtn variables requested${NC}"
    reset=true
fi

if [ "${reset}" = true ]
then
    # Reset the environment variables.
    source ./reset_env_variables.sh
else
    # Set the environment variables.
    source ./set_env_variables.sh
fi

if [ "${no_auto_start}" = true ]
then
    # Ensure the NO_AUTO_START envirnoment variable is set to true.
    export NO_AUTO_START=true
fi

if [ "${build}" = true ]
then
    # Build and start the container.
    docker-compose up -d --build
else
    # Start the container.
    docker-compose up -d
fi

# Only execute if the `NO_AUTO_START` variable has NOT been set.
if [ -z ${NO_AUTO_START} ]
then
    # If CTRL+C is pressed, ensure the progress background PID is stopped too.
    function ctrl_c()
    {
        >&2 echo -e "${RED} => CTRL+C received, exiting${NC}"
        # Stop the progress indicator.
        kill $progress_pid
        wait $progress_pid 2>/dev/null
        # Cursor visible again.
        tput cnorm
        exit
    }

    # Creates a animated progress (a cursor growing taller and shorter)
    function progress() {
        # Make sure to use non-unicode character type locale. (That way it works for any locale as long as the font supports the characters).
        local LC_CTYPE=C
        local char="▁▂▃▄▅▆▇█▇▆▅▄▃▂▁"
        local charwidth=3
        local i=0
        # Cursor invisible
        tput civis
        while sleep 0.1; do
            i=$(((i + $charwidth) % ${#char}))
            printf "%s" "${char:$i:$charwidth}"
            echo -en "\033[1D"
        done
    }

    # Pings the server up to 35 times to see if it is available yet.
    function check_status() {
        local max_num_tries=35
        local status_code=$(curl --write-out %{http_code} --silent --output /dev/null localhost:${FLASK_RUN_PORT}/graphiql)
        if [[ ${iterator} -lt ${max_num_tries} && ${status_code} -eq 200 ]]
        then
            # Stop the progress indicator.
            kill $progress_pid
            wait $progress_pid 2>/dev/null
            # Cursor visible again.
            tput cnorm
            >&2 echo -e "${GREEN}GraphiQL is Up at localhost:${FLASK_RUN_PORT}/graphiql${NC}"
            open http://localhost:${FLASK_RUN_PORT}/graphiql
        elif [[ ${iterator} -eq ${max_num_tries} ]]
        then
            # Stop the progress indicator.
            kill $progress_pid
            wait $progress_pid 2>/dev/null
            # Cursor visible again.
            tput cnorm
            >&2 echo -e "${YELLOW}Did not work. Perhaps the server is taking a long time to start?${NC}"
        else
            echo -en "${chars:$iterator:1}" "\r"
            sleep 1
            ((iterator++))
            check_status
        fi
    }
    # Start the progress indicator.
    >&2 echo -e "${YELLOW}* Checking if the server is Up at localhost:${FLASK_RUN_PORT}${NC} ..."
    progress &
    # Set the progress indicator's PID to a variable.
    progress_pid=$!
    # This is a trap for CTRL+C
    trap ctrl_c INT
    # Check the status
    iterator=0
    check_status
else
    >&2 echo -e "${GREEN}The server container is built and running.\n- The server has not been started; it must be started manually.\n- Please see the README.md for more information.${NC}"
fi
```

There is a LOT going on here.

I start out by defining some nice colors for displaying console text to the user. This may help show the user what is happening though the start process.

I then capture any flags that were passed to the script. By default, the variables representing these flags are set to false. If the flags are passed, these variables get set to true.

If the variables representing the passed flags are true, I take specific actions.

- If `reset` is true, I source the `reset_env_variables.sh` script which unsets all the environment variables and then sources the `set_env_variables.sh` script which sets needed defaults. More on these scripts later.

  If `reset` is still false, I skip the `reset_env_variables.sh` and just source the `set_env_variables.sh` script.

- If the `no_auto_start` is true, I explicitly set the `NO_AUTO_START` environment variable to true.

- If `build` is true, I execute `docker-compose up` with the `-b` flag to get it to rebuild the image.

  If `build` is still false, I execute `docker-compose up` WITHOUT the `-b` flag. Note that if there are changes to the `Dockerfile-dev` file, it will also rebuild.

Now I check if the `NO_AUTO_START` environment variable is set. If it is NOT, I define a bunch of useful function and execute them.

I first start the progress function in the background. This will display an animated cursor to hep indicate to the user that something is actually happening and the app isn't just stuck. I set the progress pid to a variable so that I can kill it when I'm done with it.

I capture CTRL+C so that if the user kills the script, I can still stop the progress function.

Then I begin pinging the server to see if it is up. I ping it a max of 35 times (once per second). If it is running, I attempt to open it in the browser. If I don't get it in 35 seconds, I leave a message for the user.

If the `NO_AUTO_START` environment variable WAS set, the server would not have started automatically, so it makes no sense to ping the server. I just drop a note to the user to inform them as to what is going on.

## Stop

Once our container is running, I can do whatever my initial goal for the development session is. Ultimately, I will finish my task and want the server to stop.

The `stop.sh` script is just the thing!

This simply calls `docker-compose down`. It stops the container and removes it. Then removes any networks.

[`stop.sh`](./stop.sh)

```bash
#!/bin/bash

# Stop the container.
docker-compose down
```

## Environment Variables

Environment variable management can be a big part of configuring an app and getting it to run right in the correct environment.

Most of the environment variables needed for this app are set by default in the `docker-compose.yml file`. If there are different environment variables that are needed in your app, they should be added there and then overridden as necessary in the `.env-dev` file. Of course secrets and other sensitive data should NEVER be committed to your repo, thus, the `.env-dev` file is on the `.gitignore` list. Defaults should always be safe values. If there are specific environment variables that NEED to be set but cannot be included as defaults in the `docker-compose.yml` file, PLEASE include some information in the README.md that informs future developers about this.

The two environment variables that I need to have set are `DOT_ENV_FILE` and `FLASK_RUN_PORT`. I need `DOT_ENV_FILE` set to the path for the `.env-dev` file if it exists. I need `FLASK_RUN_PORT` set as I use it in the `start.sh` script.

I accomplish this in the `set_env_variables.sh` file. Here it is:

[`set_env_variables.sh`](./set_env_variables.sh)

```bash
#!/bin/bash

# Defined some useful colors for echo outputs.
# Use BLUE for informational.
BLUE="\033[1;34m"
# Use Green for a successful action.
GREEN="\033[0;32m"
# Use YELLOW for warning informational and initiating actions.
YELLOW="\033[1;33m"
# No Color (used to stop or reset a color).
NC='\033[0m'

# The project directory.
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
>&2 echo -e "${BLUE}Current project dir - ${PROJECT_DIR}${NC}"

# .env-dev loading in the shell
DOT_ENV=.env-dev
DOT_ENV_FILE=${PROJECT_DIR}/${DOT_ENV}
function dotenv() {
    if [ -f "${DOT_ENV_FILE}" ]
    then
        set -a
        [ -f ${DOT_ENV_FILE} ] && . ${DOT_ENV_FILE}
        set +a
        >&2 echo -e "${GREEN}* Override environment variables set from the ${DOT_ENV} file.${NC}"
        >&2 echo -e "${GREEN}* DOT_ENV_FILE set to ${DOT_ENV_FILE}${NC}"
    else
        DOT_ENV_FILE=${PROJECT_DIR}/.env-none
        >&2 echo -e "${YELLOW}Not using a ${DOT_ENV} file${NC}"
    fi
}
# Run dotenv
dotenv

# If environment variables are set, use them. If not, use the defaults.
# Only need defaults for `DOT_ENV_FILE` and `FLASK_RUN_PORT` as they are used in the scripts.
# All other defaults are set in the `docker-compose.yml` file.
export DOT_ENV_FILE=${DOT_ENV_FILE:-}
export FLASK_RUN_PORT=${FLASK_RUN_PORT:-5000}
>&2 echo -e "${GREEN}* Default environment variables set that weren't overridden in the ${DOT_ENV} file or from the command line.${NC}"
```

Again, I define some nice colors for displaying console text to the user. This may help show the user what is happening process.

I capture the path to the project folder so that I can use absolute paths moving forward.

I define and call a function (`dotenv`) that looks for the `.env-dev` file. If it finds it, it goes through it and sets the variables with their values. If is doesn't, it explicitly sets the `DOT_ENV_FILE` variable to `.env-none`.

Finally, I export the needed environment variables values from the `.env-dev` or with fallback defaults.

Sometimes I end up setting environment variables on the command line for expedience sake. rather than going through all the variable on the command line to figure out what is set to what or trying to unset each of them manually, I can use the `reset_env_variables.sh` script to unset them all at once and reset the defaults.

Here is the script:

[`reset_env_variables.sh`](./reset_env_variables.sh)

```bash
#!/bin/bash

# Defined some useful colors for echo outputs.
# Use Green for a successful action.
GREEN="\033[0;32m"
# No Color (used to stop or reset a color).
NC='\033[0m'

# Unset any previously set environment variables.
unset DOT_ENV_FILE
unset FLASK_APP
unset FLASK_ENV
unset FLASK_RUN_PORT
unset LOG_TYPE
unset NO_AUTO_START
unset POSTGRES_DB
unset POSTGRES_DB_TEST
unset POSTGRES_HOST
unset POSTGRES_HOST_TEST
unset POSTGRES_PORT
unset POSTGRES_PORT_TEST
unset POSTGRES_PASSWORD
unset POSTGRES_PASSWORD_TEST
unset POSTGRES_USER
unset POSTGRES_USER_TEST
unset PYTHON_VERSION
unset SECRET_KEY
unset SNAKEVIZ_PORT
unset SSL_ENABLED

>&2 echo -e "${GREEN}* Environment variables unset.${NC}"

# Set the environment variables.
source ./set_env_variables.sh
```

Yet again, I define some nice colors for displaying console text to the user. This may help show the user what is happening process.

I then unset each environment variable.

Finally, I source the `set_env_variables.sh` script to get the variables back to defaults. Remember, the values set in the `.env-dev` file will be picked up and override the defaults in the `docker-compose.yml` file. By clearing that file before resetting environment variables, I can get the variables back to the original defaults.

## Developing

Now that I can start up my environment within a docker container with a single command (no python environments to install locally, no dependencies locally), I want to get to developing.

This next bit assumes VS Code is the IDE.

Here are some very helpful extensions for working with docker containers:

- [Docker](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-docker) by Microsoft

- [Docker Explorer](https://marketplace.visualstudio.com/items?itemName=formulahendry.docker-explorer) by Jun Han

With these installed, I can spin up my container and auto start the server. Right clicking on the container in the "DOCKER CONTAINERS" tab and selecting "Logs" will output the container logs to a terminal without needing to enter the container.

The extension I use most is the [Remote-Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension.

With this extension, I can start the container (I usually start the container without auto starting the server - `./start.sh -n`) and enter the container itself for developing. I keep a VS Code workspace file in my repo with the recommended extensions for inside the container defined in the `settings` block in `remote.containers.defaultExtensions`.

The first time I open the container, I open the VS Code workspace within the container. A notification opens and reminds me that there are recommended extensions. I install them inside the container. All the extensions in the container are installed in the root user's home folder. As this folder is maps to a volume, once the extensions are installed they persist between starts and stops and don't effect my regular local machine setup.

Now I can open files for the project within the container itself. The container now has a VS Code server also installed within the root user's home folder. For me, it looks and feels as if I am developing locally in a VS Code session, but it is all in the container. I can even use my local browser.

## Conclusion

It has taken me some time to get this dev setup working just right. I have been able to port it for other types of apps as well. It can make handing an app off to another developer very easy. They have very little setup and can get to the code right away.

Please give it a go and let share your thoughts with me.
