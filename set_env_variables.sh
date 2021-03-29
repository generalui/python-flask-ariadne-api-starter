#!/bin/bash

GREEN="\033[0;32m"
YELLOW="\033[1;33m"
# No Color
NC='\033[0m'

# The project directory.
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
>&2 echo -e "${GREEN}Current project dir - ${PROJECT_DIR}${NC}"

# .env-dev loading in the shell
DOT_ENV_FILE=${PROJECT_DIR}/.env-dev
dotenv() {
    if [ -f "${DOT_ENV_FILE}" ]
    then
        set -a
        [ -f ${DOT_ENV_FILE} ] && . ${DOT_ENV_FILE}
        set +a
    else
        DOT_ENV_FILE=${PROJECT_DIR}/.env-none
        >&2 echo -e "${YELLOW}Not using a .env-dev file${NC}"
    fi
}
# Run dotenv
dotenv

# If environment variables are set, use them. If not, use the defaults.
export NO_AUTO_START=${NO_AUTO_START:null}
export DOT_ENV_FILE=${DOT_ENV_FILE}
export FLASK_APP=${FLASK_APP:-app.py}
export FLASK_ENV=${FLASK_ENV:-development}
export FLASK_RUN_PORT=${FLASK_RUN_PORT:-5000}
export LOG_TYPE=${LOG_TYPE:null}
export POSTGRES_DB=${POSTGRES_DB:-pfaas_dev}
export POSTGRES_DB_TEST=${POSTGRES_DB:-pfaas_test}
export POSTGRES_HOST=${POSTGRES_HOST:-host.docker.internal}
export POSTGRES_HOST_TEST=${POSTGRES_HOST:-host.docker.internal}
export POSTGRES_PORT=${POSTGRES_PORT:-5432}
export POSTGRES_PORT_TEST=${POSTGRES_PORT:-5432}
export POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-docker}
export POSTGRES_PASSWORD_TEST=${POSTGRES_PASSWORD:-docker}
export POSTGRES_USER=${POSTGRES_USER:-postgres}
export POSTGRES_USER_TEST=${POSTGRES_USER:-postgres}
export PYTHON_IMAGE_VERSION=${PYTHON_IMAGE_VERSION:-3.8-alpine}
export SECRET_KEY=${SECRET_KEY:-some_real_good_secret}
export SNAKEVIZ_PORT=${SNAKEVIZ_PORT:-8020}
export SSL_ENABLED=${SSL_ENABLED:null}