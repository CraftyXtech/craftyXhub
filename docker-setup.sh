#!/bin/bash

# Copy .env.docker to .env for Docker use
cp .env.docker .env

# Build the Docker containers
docker-compose build

# Start the containers
docker-compose up -d

# Install Composer dependencies
docker-compose exec app composer install

# Generate application key (if not already set)
docker-compose exec app php artisan key:generate --ansi

# Run database migrations
docker-compose exec app php artisan migrate

# Install NPM dependencies
docker-compose run --rm npm install

# Build assets
docker-compose run --rm npm run build

echo "Docker setup completed successfully!"
echo "Your Laravel application is now running at: http://localhost" 