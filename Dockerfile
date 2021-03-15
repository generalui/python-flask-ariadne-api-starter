# Make the Python version into a variable so that it may be updated easily if / when needed. (ie "python3.8")
ARG pythonImageVersion

# Start with a bare Alpine Linux to keep the container image small
FROM tiangolo/uwsgi-nginx-flask:${pythonImageVersion}

# Designate the `/app` folder inside the container as the working directory.
WORKDIR /app

# Copy the app codebase to the `/app` folder inside the container.
COPY . /app

# `libpq` is needed for Postgres commands.
RUN apk add --no-cache libpq
# Install build tools for installing dependencies.
RUN apk add --no-cache --virtual .build-deps \
    gcc \
    musl-dev \
    postgresql-dev \
    linux-headers
# Install the PyPI dependencies using pip
RUN pip3 install --no-cache-dir -r requirements.txt
# Remove the build tools now that we are done with them.
RUN apk del --no-cache .build-deps
