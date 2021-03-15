# Python Flask Ariadne API Starter

A GraphQL API that serves data from a PostgreSQL Database. This is built in Python with Flask and Ariadne and developed and deployed in Docker.

## Status

### Staging

<!-- [![coverage report](https://github.com/???)](https://github.com/???) -->

## Dependencies

- [Git](https://git-scm.com/) To clone this repo!
- [Docker Desktop](https://www.docker.com/products/docker-desktop) (`docker`)
- [Visual Studio Code](https://code.visualstudio.com/) (`code`) - this is optional, but sure makes everything a lot easier.
- A PostgreSQL server. See [Running PostgreSQL in Docker](#running-postgresql-in-docker) for more info.

## Development

The instructions below assume that there is a PostgreSQL server running locally with the Database installed. If this is not the case, please see information on [running PostgreSQL in Docker](#running-postgres-in-docker) below.

To change any of the environment variables used by the app see [Environment Variables](#environment-variables) below.

The first time you checkout the project, run the following command to build the docker image, start the container, and start the API:

```sh
./start.sh
```

This will build the Docker image and run the container. Once the container is created, the Flask server will be started. Then a command prompt should open from within the container (looks like: `bash-5.0#`).

The GraphiQL playground interface should open automatically in your browser.

**Note:** If you get _'Version in "./docker-compose.yml" is unsupported.'_, please update your version of Docker Desktop.

**Optional:** If you choose to use VS Code, you can use the [Remote-Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension to develop from within the container itself. Using this approach, you don't need to install Python or any dependencies (besides Docker and VS Code itself) as everything is already installed inside the container. There is a volume mapped to your user .ssh folder so that your ssh keys are available inside the container as well as your user .gitconfig file. The user folder inside the container is also mapped to a volume so that it persists between starts and stops of the container. This means you may create a .bash_profile or similar for yourself within the container and it will persist between container starts and stops.

To exit the container's command prompt, type `exit` and enter. This will bring you back to your local command prompt.

The following command will stop the server and container:

```sh
./stop.sh
```

Restart the container with the following command:

```sh
./start.sh
```

If there are changes made to the container or image, first, stop the container `./stop.sh`, then rebuild it and restarted it with `./start.sh --build` or `./start.sh -b`.

### Non-Dockerized

If you choose NOT to use the dockerized development method above, please ensure the following are installed:

- [Python](https://www.python.org/) - version 3.8
- All the packages in the [`requirements-main.txt`](./requirements-main.txt) file at the versions specified.
- All the packages in the [`requirements-dev.txt`](./requirements-dev.txt) file at the versions specified.

See [https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/) for information on installing Python packages for a specific project.

Start the app with the following called from the root of the project:

```sh
source ./set_env_variables.sh && python run.py
```

### Running PostgreSQL in Docker

A simple way to get PostgreSQL running locally is to use Docker. Here is a simple Dockerized PostgreSQL server with pgAdmin:

["postgres_docker" on Github](https://github.com/generalui/postgres_docker)

#### Linux ONLY

If you are running on a Linux operating system the default connection to the docker container `host.docker.internal` will not work. To connect to the local dockerized PostgreSQL DB, ensure there is a `.env-dev` file ([`.env-SAMPLE`](./.env-SAMPLE) can be used as a reference.) In the `.env-dev` file, ensure the `POSTGRES_HOST` variable is set to `172.17.0.1`

```.env
POSTGRES_HOST=172.17.0.1
```

### Connecting to a different Database

Alternatively, the app may be set up to connect to the existing staging database or another database.

To connect to a different database (ie staging), the `.env-dev` file must also be used with values similar to:

```.env
POSTGRES_DB={get_the_database_name}
POSTGRES_HOST={get_the_database_host}
POSTGRES_PASSWORD={get_the_database_password}
POSTGRES_USER={get_the_database_user}
```

### Environment Variables

All the environment variables used by the app have defaults. To set the environment variables, simply run the following bash script from the root of the [`project folder`](./):

```sh
source set_env_variables.sh
```

The default environment variables' values may be over-written by adding the value to a `.env-dev` file in the root of the [`project folder`](./). This file is not versioned in the repository.

The [`.env-SAMPLE`](./.env-SAMPLE) file is an example of what the `.env-dev` could be like and may be used as a reference.

To reset the environment variables to the defaults (still using the values in the `.env-dev` file), run the following bash script in the root of the [`project folder`](./):

```sh
source reset_env_variables.sh
```

### Building the Database

The app uses [Flask-Migrate](https://flask-migrate.readthedocs.io/en/latest/#) to manage migrations.

Once the PostgreSQL server is set up, a database must be created. Before `Flask-Migrate` can be used, the database MUST already be created. [Miguel Grinberg](http://miguelgrinberg.com), the creator of `Flask-Migrate` explains why [here](https://github.com/miguelgrinberg/Flask-Migrate/issues/145.)

Locally, there should be a dev database and a test database. Like:

- `my_db_dev` - for development
- `my_db_test` - for testing

Once created, initialize the migrations from the command line at the root of the [`project folder`](./):

```sh
flask db init
```

This will create a `migrations` folder in the root of the app.

Now, create the initial migration with:

```sh
flask db migrate -m "Initial migration."
```

This creates the `alembic_version` table in the database to track migrations. This also creates a migration file in the [`migrations`](./migrations) folder. **NOTE** The resulting migrations are executed in alphabetical order in the `versions` folder but the files are not necessarily created in order. Sometimes, changing the beginning of the hash name on the migration files to get them in the order they need to be built is necessary.

Now execute the migrations with.

```sh
flask db upgrade
```

As and/or if models are changed or created, run

```sh
flask db migrate -m "Some message that describes the database change."
```

again to create a new migration.

This will create a new migration file.

Once again, run

```sh
flask db upgrade
```

to execute any new migrations.

## Testing

All tests are in the [`tests/`](./tests/) folder.

See: [TESTING.md](./tests/TESTING.md) in the [`tests/`](./tests/) folder

## Performance Profiling

See: [PROFILING.md](./api/telemetry/PROFILING.md) in the [`api/telemetry/`](./api/telemetry/) folder

## Logging

See: [LOGGING.md](./api/logger/LOGGING.md) in the [`api/logger/`](./api/logger/) folder
