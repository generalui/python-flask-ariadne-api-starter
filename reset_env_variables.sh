#!/bin/bash

# Unset any previously set environment variables.
unset NO_AUTO_START
unset DOT_ENV_FILE
unset FLASK_APP
unset FLASK_ENV
unset FLASK_RUN_PORT
unset LOG_TYPE
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
unset PYTHON_IMAGE_VERSION
unset SECRET_KEY
unset SNAKEVIZ_PORT
unset SSL_ENABLED

# Set the environment variables.
source ./set_env_variables.sh
