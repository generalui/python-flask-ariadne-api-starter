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
