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
