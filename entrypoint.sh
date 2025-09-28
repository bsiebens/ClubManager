#!/bin/bash

# Start temporary HTTP server for Certbot challenges
certbot certonly --standalone --non-interactive --agree-tos --register-unsafely-without-email -d $DOMAIN

# Launch daphne
uv run daphne -e ssl:8000:privateKey=/etc/letsencrypt/live/$DOMAIN/privkey.pem:certKey=/etc/letsencrypt/live/$DOMAIN/fullchain.pem ClubManager.asgi:application

