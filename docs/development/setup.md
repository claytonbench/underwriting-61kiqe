# Development Environment Setup Guide

## Introduction

This document provides comprehensive instructions for setting up the development environment for the Loan Management System. The system consists of a Django backend, React frontend, and several supporting services. Following these instructions will ensure a consistent development environment across the team.

## Prerequisites

Before setting up the development environment, ensure you have the following software installed on your system:

### Required Software

- **Docker**: Version 20.0 or higher
- **Docker Compose**: Version 2.0 or higher
- **Git**: Version 2.0 or higher
- **VS Code** (recommended) or your preferred IDE

Optional for local development without Docker:
- **Python**: Version 3.11 or higher
- **Node.js**: Version 18.0 or higher
- **npm**: Version 8.0 or higher or **yarn**: Version 1.22 or higher

### System Requirements

- **CPU**: 4 cores or more recommended
- **RAM**: Minimum 8GB, 16GB recommended
- **Disk Space**: At least 10GB of free space
- **Operating System**: Windows 10/11, macOS 10.15+, or Linux (Ubuntu 20.04+ recommended)

### Access Requirements

You will need the following access permissions:

- GitHub repository access
- Auth0 development tenant credentials (for authentication testing)
- AWS development account access (optional, for S3 integration testing)

## Getting Started

Follow these steps to set up your development environment:

### Clone the Repository

```bash
# Clone the repository
git clone https://github.com/your-organization/loan-management-system.git

# Navigate to the project directory
cd loan-management-system
```

### Environment Configuration

Create the necessary environment files for local development:

#### Backend Environment (.env file)
```bash
# Copy the example environment file
cp src/backend/.env.example src/backend/.env

# Edit the .env file with your local settings
# Required variables include:
# - SECRET_KEY: Django secret key
# - AUTH0_DOMAIN: Your Auth0 domain
# - AUTH0_API_IDENTIFIER: Auth0 API identifier
# Optional variables for external services:
# - SENDGRID_API_KEY: For email testing
# - AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY: For S3 testing
# - DOCUSIGN_INTEGRATION_KEY: For e-signature testing
```

#### Frontend Environment (.env.development file)
```bash
# Copy the example environment file
cp src/web/.env.development.example src/web/.env.development

# Edit the .env.development file with your local settings
# Required variables include:
# - REACT_APP_API_URL: Backend API URL (http://localhost:8000/api)
# - REACT_APP_AUTH0_DOMAIN: Your Auth0 domain
# - REACT_APP_AUTH0_CLIENT_ID: Auth0 client ID
# - REACT_APP_AUTH0_AUDIENCE: Auth0 API audience
```

## Docker-based Development Setup

The recommended way to set up the development environment is using Docker, which ensures consistency across different development machines.

### Backend Setup

To set up the backend development environment:

```bash
# Navigate to the backend directory
cd src/backend

# Start the backend services
docker-compose up -d

# Create a superuser for the Django admin
docker-compose exec web python manage.py createsuperuser

# Apply migrations
docker-compose exec web python manage.py migrate

# Load initial data (if available)
docker-compose exec web python manage.py loaddata initial_data

# The backend API will be available at http://localhost:8000/api
# The Django admin interface will be available at http://localhost:8000/admin
```

### Frontend Setup

To set up the frontend development environment:

```bash
# Navigate to the frontend directory
cd src/web

# Start the frontend development server
docker-compose up -d

# The frontend application will be available at http://localhost:3000
```

### Running Both Services

For convenience, you can use the root docker-compose file to run both backend and frontend services:

```bash
# From the project root directory
docker-compose -f infrastructure/docker/docker-compose.yml up -d

# This will start all services including:
# - Backend (Django)
# - Frontend (React)
# - Database (PostgreSQL)
# - Cache (Redis)
# - Celery workers
# - Celery beat scheduler
```

### Docker Services Overview

The development environment includes the following Docker services:

| Service | Description | Port |
|---------|-------------|------|
| web | Django backend application | 8000 |
| db | PostgreSQL database | 5432 |
| redis | Redis for caching and message broker | 6379 |
| celery | Celery worker for background tasks | - |
| celery-beat | Celery beat for scheduled tasks | - |
| frontend | React frontend application | 3000 |

### Docker Commands Reference

Useful Docker commands for development:

```bash
# View running containers
docker-compose ps

# View logs for a specific service
docker-compose logs -f web

# Restart a specific service
docker-compose restart web

# Stop all services
docker-compose down

# Rebuild services after dependency changes
docker-compose up -d --build

# Run Django management commands
docker-compose exec web python manage.py <command>

# Run tests
docker-compose exec web pytest

# Access PostgreSQL
docker-compose exec db psql -U postgres -d loan_management_dev
```

## Local Development Setup (Without Docker)

If you prefer to run the services directly on your local machine without Docker, follow these steps:

### Backend Setup

To set up the backend locally:

```bash
# Navigate to the backend directory
cd src/backend

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Set up environment variables
# Make sure to create and configure the .env file

# Apply migrations
python manage.py migrate

# Create a superuser
python manage.py createsuperuser

# Run the development server
python manage.py runserver

# The backend API will be available at http://localhost:8000/api
```

### Frontend Setup

To set up the frontend locally:

```bash
# Navigate to the frontend directory
cd src/web

# Install dependencies
yarn install
# or with npm
npm install

# Set up environment variables
# Make sure to create and configure the .env.development file

# Run the development server
yarn start
# or with npm
npm start

# The frontend application will be available at http://localhost:3000
```

### Local Database Setup

For local development without Docker, you'll need to install and configure PostgreSQL and Redis:

1. **PostgreSQL Setup**:
   - Install PostgreSQL 15 or higher
   - Create a database: `createdb loan_management_dev`
   - Update the `.env` file with your database credentials

2. **Redis Setup**:
   - Install Redis 7 or higher
   - Start the Redis server
   - Update the `.env` file with your Redis connection details

3. **Celery Setup**:
   - In a separate terminal, start the Celery worker:
     ```bash
     cd src/backend
     celery -A celery_app worker --loglevel=info
     ```
   - In another terminal, start the Celery beat scheduler:
     ```bash
     cd src/backend
     celery -A celery_app beat --loglevel=info
     ```

## Development Workflow

This section describes the recommended development workflow for the project.

### Git Workflow

We follow a feature branch workflow:

1. Create a new branch for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   # or for bugfixes
   git checkout -b bugfix/issue-description
   ```

2. Make your changes, commit them with descriptive messages

3. Push your branch to GitHub:
   ```bash
   git push -u origin feature/your-feature-name
   ```

4. Create a pull request on GitHub

5. After review and approval, your changes will be merged

Ensure your code follows the project's coding standards with proper formatting, linting, and testing. The project uses GitHub Actions for CI/CD, which automatically runs tests, linting, and builds on every pull request and push to main branches.

### Backend Development

When developing backend features:

1. Create or modify Django models in the appropriate app
2. Run migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```
3. Implement views, serializers, and services
4. Write tests for your changes
5. Run tests to ensure everything works:
   ```bash
   pytest
   # or with coverage
   pytest --cov=.
   ```
6. Format your code:
   ```bash
   black .
   isort .
   ```
7. Run linting checks:
   ```bash
   flake8
   ```

### Frontend Development

When developing frontend features:

1. Create or modify React components in the appropriate directory
2. Implement state management using Redux/Redux Toolkit
3. Write tests for your components and logic
4. Run tests to ensure everything works:
   ```bash
   yarn test
   # or with coverage
   yarn test --coverage
   ```
5. Format your code:
   ```bash
   yarn format
   ```
6. Run linting checks:
   ```bash
   yarn lint
   ```

### API Integration

When working on features that require backend and frontend integration:

1. Define the API contract first
2. Implement the backend API endpoint
3. Test the API using tools like Postman or curl
4. Implement the frontend API client
5. Connect the frontend components to the API
6. Test the integration end-to-end

### Code Standards

Adhere to the following code standards for consistent codebase:

**Backend (Python/Django)**:
- Follow PEP 8 style guide with a 100-character line length
- Use Black and isort for code formatting
- Write docstrings for all functions, classes, and modules
- Maintain 80%+ test coverage for all code
- Follow Django's best practices for models, views, and authentication

**Frontend (TypeScript/React)**:
- Follow the ESLint configuration with Prettier formatting
- Use TypeScript interfaces and types for all components and functions
- Organize components using the feature-based folder structure
- Use React hooks and functional components instead of class components
- Write unit tests for all components and utilities

### Continuous Integration

The project uses GitHub Actions for continuous integration. The CI pipeline includes:

1. **Code Quality Checks**:
   - Linting (flake8, ESLint)
   - Formatting (black, isort, prettier)
   - Type checking (mypy, TypeScript)

2. **Automated Testing**:
   - Unit tests for backend and frontend
   - Integration tests for API endpoints
   - End-to-end tests for critical workflows

3. **Security Scanning**:
   - Dependency vulnerability scanning
   - SAST (Static Application Security Testing)
   - Container image scanning

4. **Build Verification**:
   - Backend package build
   - Frontend asset compilation
   - Docker image building

All pull requests must pass these checks before being merged. The configuration for these workflows is stored in the `.github/workflows` directory.

## Testing

This section covers how to run tests for the project.

### Backend Testing

The backend uses pytest for testing:

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=.

# Run tests for a specific app
pytest src/backend/apps/users/

# Run a specific test file
pytest src/backend/apps/users/tests/test_models.py

# Run a specific test
pytest src/backend/apps/users/tests/test_models.py::TestUserModel::test_create_user
```

With Docker:
```bash
docker-compose exec web pytest
```

### Frontend Testing

The frontend uses Jest and React Testing Library for testing:

```bash
# Run all tests
yarn test

# Run tests with coverage
yarn test --coverage

# Run tests in watch mode
yarn test --watch

# Run a specific test file
yarn test src/components/UserForm/UserForm.test.tsx
```

With Docker:
```bash
docker-compose exec frontend yarn test
```

### End-to-End Testing

End-to-end tests use Cypress:

```bash
# Open Cypress test runner
cd src/web
yarn cypress:open

# Run Cypress tests headlessly
yarn cypress:run
```

## IDE Setup

This section provides recommendations for setting up your IDE for development.

### VS Code Configuration

VS Code is the recommended IDE for this project. Install the following extensions:

- Python extension (Microsoft)
- Pylance for Python language server
- ESLint for JavaScript/TypeScript linting
- Prettier for code formatting
- Docker extension for managing containers
- GitLens for enhanced Git integration
- Jest Runner for running tests

Recommended workspace settings (`.vscode/settings.json`):

```json
{
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  },
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "python.formatting.blackArgs": ["--line-length", "100"],
  "[python]": {
    "editor.formatOnSave": true
  },
  "[javascript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[typescript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[typescriptreact]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  }
}
```

### PyCharm Configuration

If you prefer PyCharm for backend development:

1. Open the `src/backend` directory as a project
2. Configure the Python interpreter to use the virtual environment or Docker Python interpreter
3. Install the following plugins:
   - Black formatter
   - Flake8 linter
   - Docker integration

4. Configure code style to match the project's standards:
   - Line length: 100
   - Use Black formatter
   - Enable Flake8 linting

### WebStorm Configuration

If you prefer WebStorm for frontend development:

1. Open the `src/web` directory as a project
2. Install the following plugins:
   - ESLint
   - Prettier
   - Jest

3. Configure code style to match the project's standards:
   - Enable ESLint integration
   - Enable Prettier as the default formatter
   - Configure Jest for running tests

## External Services Configuration

This section explains how to configure external services for local development.

### Auth0 Configuration

To set up Auth0 for local development:

1. Create a free Auth0 account at https://auth0.com
2. Create a new tenant for development
3. Create a Single Page Application for the frontend
4. Create an API for the backend
5. Configure the following settings:
   - Allowed Callback URLs: `http://localhost:3000/callback`
   - Allowed Logout URLs: `http://localhost:3000`
   - Allowed Web Origins: `http://localhost:3000`
6. Update your environment files with the Auth0 credentials

### AWS S3 Configuration

For S3 document storage testing:

1. Create an AWS account or use the development account
2. Create an S3 bucket for development
3. Create an IAM user with S3 access permissions
4. Generate access keys for the IAM user
5. Update your backend `.env` file with the AWS credentials

Alternatively, you can use MinIO as a local S3-compatible service:

```bash
# Add MinIO service to docker-compose.yml
minio:
  image: minio/minio
  ports:
    - "9000:9000"
    - "9001:9001"
  environment:
    - MINIO_ROOT_USER=minioadmin
    - MINIO_ROOT_PASSWORD=minioadmin
  command: server /data --console-address ":9001"
  volumes:
    - minio_data:/data
```

Then update your backend `.env` file to use MinIO instead of AWS S3.

### SendGrid Configuration

For email testing:

1. Create a SendGrid account or use the development account
2. Create an API key with mail send permissions
3. Update your backend `.env` file with the SendGrid API key

For local development without SendGrid, you can configure Django to output emails to the console:

```python
# In development.py settings
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

### DocuSign Configuration

For e-signature testing:

1. Create a DocuSign developer account
2. Create an integration key
3. Generate an RSA keypair
4. Update your backend `.env` file with the DocuSign credentials

For local development without DocuSign, the system includes a mock implementation that simulates the e-signature process.

## Troubleshooting

Common issues and their solutions:

### Docker Issues

| Issue | Solution |
|-------|----------|
| Port already in use | Stop the service using the port or change the port mapping in docker-compose.yml |
| Container fails to start | Check logs with `docker-compose logs <service>` |
| Volume permission issues | Ensure proper permissions on mounted directories |
| Docker Compose version mismatch | Update Docker Compose to version 2.0 or higher |

### Backend Issues

| Issue | Solution |
|-------|----------|
| Migrations conflicts | Reset the database or manually resolve conflicts |
| Package installation fails | Check Python version compatibility or use Docker |
| Environment variables not loaded | Ensure .env file exists and is properly formatted |
| Database connection errors | Verify database credentials and connection settings |

### Frontend Issues

| Issue | Solution |
|-------|----------|
| Node modules installation fails | Clear node_modules and package-lock.json, then reinstall |
| TypeScript errors | Update TypeScript version or fix type definitions |
| API connection errors | Check API URL in environment variables |
| Auth0 authentication issues | Verify Auth0 configuration and credentials |

### Common Error Messages

| Error | Solution |
|-------|----------|
| `ModuleNotFoundError` | Check import paths and installed packages |
| `ProgrammingError: relation does not exist` | Run migrations to create database tables |
| `TypeError: Cannot read property of undefined` | Check for null/undefined values in JavaScript code |
| `Network Error` | Check API server is running and accessible |

## Additional Resources

- [Project README](../../README.md)
- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework Documentation](https://www.django-rest-framework.org/)
- [React Documentation](https://reactjs.org/docs/getting-started.html)
- [Redux Documentation](https://redux.js.org/)
- [Material-UI Documentation](https://mui.com/material-ui/getting-started/)