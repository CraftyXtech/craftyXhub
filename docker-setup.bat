@echo off
echo Setting up Docker environment for CraftyXhub...

REM Copy .env.docker to .env for Docker use
copy .env.docker .env

REM Build the Docker containers
docker-compose build

REM Start the containers
docker-compose up -d

REM Install Composer dependencies
docker-compose exec app composer install

REM Generate application key (if not already set)
docker-compose exec app php artisan key:generate --ansi

REM Run database migrations
docker-compose exec app php artisan migrate

REM Install NPM dependencies
docker-compose run --rm npm install

REM Build assets
docker-compose run --rm npm run build

echo Docker setup completed successfully!
echo Your Laravel application is now running at: http://localhost 