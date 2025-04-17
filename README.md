# CraftyXhub

CraftyXhub is the official content platform for Crafty Technologies, featuring tech news, blog posts, payment solutions, and crypto innovations. Built with Laravel, Vue.js, and Inertia.js, it provides a modern, responsive user experience with powerful backend capabilities.

## Features

- **Interactive Blog System**: Post articles with rich content featuring categories, tags, and comments
- **User Authentication**: Secure login, registration, and profile management
- **Vector Search**: Powered by pgvector for semantic content search
- **Responsive Design**: Works seamlessly on mobile, tablet, and desktop devices
- **Dark Mode Support**: Toggle between light and dark themes for comfortable viewing
- **Social Features**: Like, bookmark, and share functionality for posts

## Tech Stack

- **Backend**: Laravel 12.x
- **Frontend**: Vue.js 3 with Inertia.js
- **Database**: PostgreSQL with pgvector extension
- **CSS**: Tailwind CSS
- **Containerization**: Docker

## Getting Started

### Prerequisites
- Docker and Docker Compose (for Docker installation)
- PHP 8.2+ (for traditional installation)
- Composer
- Node.js and NPM
- PostgreSQL with pgvector extension

### Installation with Docker (Recommended)

1. Clone the repository:
   ```
   git clone <repository-url>
   cd craftyXhub
   ```

2. Setup with Docker:
   
   **For Windows:**
   ```
   docker-setup.bat
   ```

   **For Linux/Mac:**
   ```
   chmod +x docker-setup.sh
   ./docker-setup.sh
   ```

3. The application will be available at:
   ```
   http://localhost
   ```

### Manual Docker Setup Steps

If you prefer to run the commands manually:

1. Copy the environment file:
   ```
   cp .env.docker .env
   ```

2. Build and start the containers:
   ```
   docker-compose build
   docker-compose up -d
   ```

3. Install dependencies and set up the application:
   ```
   docker-compose exec app composer install
   docker-compose exec app php artisan key:generate --ansi
   docker-compose exec app php artisan migrate
   docker-compose run --rm npm install
   docker-compose run --rm npm run build
   ```

### Traditional Installation (Without Docker)

1. Clone the repository:
   ```
   git clone <repository-url>
   cd craftyXhub
   ```

2. Install PHP dependencies:
   ```
   composer install
   ```

3. Copy the environment file and configure your database:
   ```
   cp .env.example .env
   ```
   Update the database settings in the .env file.

4. Generate application key:
   ```
   php artisan key:generate
   ```

5. Run migrations:
   ```
   php artisan migrate
   ```

6. Install Node.js dependencies:
   ```
   npm install
   ```

7. Build assets:
   ```
   npm run build
   ```

8. Start the development server:
   ```
   php artisan serve
   ```

9. The application will be available at:
   ```
   http://localhost:8000
   ```

## Development Workflow

### Docker Development

- **Code Changes**: PHP/Laravel changes are automatically reflected without rebuilding
- **Frontend Development**: Run `docker-compose run --rm npm run dev` for hot module reloading
- **Database Changes**: Run `docker-compose exec app php artisan migrate` after creating new migrations

### Common Docker Commands

- Start the containers:
  ```
  docker-compose up -d
  ```

- Stop the containers:
  ```
  docker-compose down
  ```

- View logs:
  ```
  docker-compose logs -f
  ```

- Access the PHP container:
  ```
  docker-compose exec app bash
  ```

- Run artisan commands:
  ```
  docker-compose exec app php artisan <command>
  ```

- Run NPM commands:
  ```
  docker-compose run --rm npm <command>
  ```

## Project Structure

- `app/` - Laravel PHP application code
- `resources/js/` - Vue.js components and pages
- `resources/css/` - Tailwind configuration and custom styles
- `database/migrations/` - Database migrations
- `docker/` - Docker configuration files
- `routes/` - Laravel routes
