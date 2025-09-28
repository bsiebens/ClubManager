# Using ubuntu as base image
FROM ubuntu:25.10

# Setting the working directory inside the container
WORKDIR /app

# Build-time arguments, to be supplied by environment variables
ENV DJANGO_DEBUG=true
ENV DJANGO_SECRETY_KEY=insecure-key
ENV DOMAIN_NAME="example.com"


# Install system dependencies and uv
# RUN apt-get update && apt-get install -y build-essential curl wget python3 supervisor caddy && rm -rf /var/lib/apt/lists/*
RUN apt-get update && apt-get install -y build-essential curl wget python3 certbot openssl libssl-dev && rm -rf /var/lib/apt/lists/*
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

# Copy and install python dependencies
COPY pyproject.toml.backup poetry.lock ./
RUN uv sync --no-group dev

# Copy rest of the application
COPY . .

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Collect static files and run migrations
RUN uv run --no-sync ./manage.py collectstatic --noinput
RUN uv run --no-sync ./manage.py migrate

# Expose port of the application
EXPOSE 80 8000

# COPY .config/Caddyfile /etc/caddy/Caddyfile
# COPY .config/supervisord.conf /etc/supervisord.conf

# CMD ["supervisord", "-c", "/etc/supervisord.conf"]
CMD ["/entrypoint.sh"]