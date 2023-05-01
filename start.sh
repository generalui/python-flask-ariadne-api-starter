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
    >&2 echo -e "${BLUE}Reset environment variables requested${NC}"
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
    # Ensure the NO_AUTO_START environment variable is set to true.
    export NO_AUTO_START=true
fi

docker system prune --force

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

    function open_url()
    {
        [[ -x $BROWSER ]] && exec "$BROWSER" "$url"
        path=$(which xdg-open || which gnome-open || which open || which start) && exec "$path" "$url"
        >&2 echo -e "${YELLOW}Can't find the browser.${NC}"
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
            url=http://localhost:${FLASK_RUN_PORT}/graphiql
            open_url
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
