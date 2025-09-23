# Using ubuntu as base image
FROM ubuntu:25.10

# Setting the working directory inside the container
WORKDIR /app

# Build-time arguments, to be supplied by environment variables
ARG DJANGO_DEBUG
ARG DJANGO_SECRETY_KEY
# ARG DJANGO_DATABASE_URL

# Install system dependencies and uv
RUN apt-get update && apt-get install -y build-essential curl wget python3 supervisor caddy && rm -rf /var/lib/apt/lists/*
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:${PATH}"

# Copy and install python dependencies
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root --without dev

# Copy rest of the application
COPY . .

# Collect static files and run migrations
RUN poetry run python manage.py collectstatic --noinput
RUN poetry run python manage.py migrate

# Expose port of the application
EXPOSE 80

COPY .config/Caddyfile /etc/caddy/Caddyfile
COPY .config/supervisord.conf /etc/supervisord.conf

CMD ["supervisord", "-c", "/etc/supervisord.conf"]