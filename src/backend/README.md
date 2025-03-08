# Loan Management System - Backend

Backend implementation for the educational loan management system. This Django-based application provides a comprehensive API for managing the entire loan lifecycle from application to funding.

## System Architecture

The backend is built using Django 4.2+ and Django REST Framework 3.14+, with a PostgreSQL database for data storage. The system follows a modular architecture with separate Django apps for different functional areas:

- Authentication: User authentication and authorization using Auth0
- Users: User profile management for borrowers, co-borrowers, and staff
- Schools: School and program management
- Applications: Loan application processing
- Underwriting: Application review and decision-making
- Documents: Document generation, storage, and e-signature integration
- Notifications: Email notifications using templates
- Funding: Loan disbursement tracking
- QC: Quality control review process
- Workflow: State machine for application status management
- Reporting: Reporting and analytics

## Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development without Docker)
- PostgreSQL 15+ (for local development without Docker)
- Redis 7.0+ (for local development without Docker)

## Development Setup

### Using Docker (Recommended)

1. Clone the repository
2. Navigate to the backend directory: `cd src/backend`
3. Create a `.env` file based on `.env.example`
4. Build and start the containers: `docker-compose up -d`
5. Run migrations: `docker-compose exec web python manage.py migrate`
6. Create a superuser: `docker-compose exec web python manage.py createsuperuser`
7. Access the API at http://localhost:8000/api/v1/
8. Access the admin interface at http://localhost:8000/admin/
9. API documentation is available at http://localhost:8000/api/docs/

### Local Development (Without Docker)

1. Clone the repository
2. Navigate to the backend directory: `cd src/backend`
3. Create a virtual environment: `python -m venv venv`
4. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`
5. Install dependencies: `pip install -r requirements-dev.txt`
6. Create a `.env` file based on `.env.example`
7. Run migrations: `python manage.py migrate`
8. Create a superuser: `python manage.py createsuperuser`
9. Start the development server: `python manage.py runserver`
10. Access the API at http://localhost:8000/api/v1/
11. Access the admin interface at http://localhost:8000/admin/
12. API documentation is available at http://localhost:8000/api/docs/

## Environment Variables

The following environment variables can be configured in your `.env` file:

```
# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0,web
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Database Settings
DB_NAME=loan_management_dev
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432

# Redis Settings
REDIS_URL=redis://redis:6379/1
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Auth0 Settings
AUTH0_DOMAIN=your-auth0-domain
AUTH0_API_AUDIENCE=your-auth0-audience

# DocuSign Settings
DOCUSIGN_INTEGRATION_KEY=your-docusign-key
DOCUSIGN_USER_ID=your-docusign-user-id
DOCUSIGN_BASE_URL=https://demo.docusign.net/restapi
DOCUSIGN_ACCOUNT_ID=your-docusign-account-id
DOCUSIGN_PRIVATE_KEY_PATH=path/to/private/key

# SendGrid Settings
SENDGRID_API_KEY=your-sendgrid-key
DEFAULT_FROM_EMAIL=noreply@loanmanagementsystem.com

# Encryption Settings
ENCRYPTION_KEY=your-encryption-key
```

## Project Structure

```
src/backend/
├── apps/                   # Django applications
│   ├── applications/       # Loan application processing
│   ├── authentication/     # User authentication
│   ├── documents/          # Document management
│   ├── funding/            # Loan funding
│   ├── notifications/      # Email notifications
│   ├── qc/                 # Quality control
│   ├── reporting/          # Reporting and analytics
│   ├── schools/            # School and program management
│   ├── underwriting/       # Application review
│   ├── users/              # User management
│   └── workflow/           # Application workflow
├── config/                 # Django project configuration
│   ├── middleware/         # Custom middleware
│   ├── settings/           # Environment-specific settings
│   ├── asgi.py             # ASGI configuration
│   ├── celery.py           # Celery configuration
│   ├── urls.py             # URL routing
│   └── wsgi.py             # WSGI configuration
├── core/                   # Core functionality
│   ├── exceptions.py       # Custom exceptions
│   ├── models.py           # Base model classes
│   ├── permissions.py      # Permission classes
│   └── serializers.py      # Base serializer classes
├── templates/              # HTML templates
├── utils/                  # Utility functions
│   ├── constants.py        # System constants
│   ├── encryption.py       # Data encryption utilities
│   ├── validators.py       # Validation utilities
│   └── storage.py          # File storage utilities
├── .dockerignore           # Docker ignore file
├── .env.example            # Example environment variables
├── .flake8                 # Flake8 configuration
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose configuration
├── manage.py               # Django management script
├── pytest.ini              # Pytest configuration
├── requirements.txt        # Production dependencies
└── requirements-dev.txt    # Development dependencies
```

## Running Tests

### Using Docker

```bash
docker-compose exec web pytest
```

To run tests with coverage:

```bash
docker-compose exec web pytest --cov=.
```

### Local Development

```bash
pytest
```

To run tests with coverage:

```bash
pytest --cov=.
```

### Test Categories

You can run specific test categories using markers:

```bash
pytest -m unit          # Run unit tests only
pytest -m integration   # Run integration tests only
pytest -m api           # Run API tests only
pytest -m model         # Run model tests only
```

## Code Quality

### Linting

```bash
flake8
```

### Code Formatting

```bash
black .
isort .
```

### Type Checking

```bash
mypy .
```

### Security Scanning

```bash
bandit -r .
safety check
```

### Pre-commit Hooks

Install pre-commit hooks to automatically check code quality before committing:

```bash
pre-commit install
```

## API Documentation

API documentation is generated using Swagger/OpenAPI and is available at:

- Swagger UI: http://localhost:8000/api/docs/
- ReDoc: http://localhost:8000/api/redoc/

The API follows RESTful principles with the following base URL structure:

```
/api/v1/{resource}/
```

All API endpoints require authentication using JWT tokens, which can be obtained through the Auth0 integration.

## Authentication

The system uses Auth0 for authentication. To authenticate API requests:

1. Obtain a JWT token from Auth0
2. Include the token in the Authorization header of your requests:

```
Authorization: Bearer {your_jwt_token}
```

For development and testing, you can also use Django's token authentication by:

1. Creating a token in the Django admin interface
2. Including the token in your requests:

```
Authorization: Token {your_token}
```

## Background Tasks

The system uses Celery for background task processing. Tasks include:

- Email notifications
- Document generation
- Scheduled reports

To run Celery workers:

```bash
# Using Docker
docker-compose up -d celery

# Local development
celery -A config worker -l info
```

To run the Celery beat scheduler for periodic tasks:

```bash
# Using Docker
docker-compose up -d celery-beat

# Local development
celery -A config beat -l info
```

## Deployment

The application is designed to be deployed using Docker containers. For production deployment, consider the following:

1. Use environment-specific settings in `config/settings/production.py`
2. Set appropriate environment variables for production
3. Use a production-ready web server like Gunicorn
4. Set up a reverse proxy like Nginx
5. Configure proper SSL/TLS certificates
6. Set up monitoring and logging

Refer to the infrastructure documentation for detailed deployment instructions.

## Contributing

1. Create a feature branch from `develop`
2. Make your changes
3. Ensure tests pass and code quality checks succeed
4. Submit a pull request to `develop`

Please follow these guidelines:

- Write tests for new features and bug fixes
- Follow the Django coding style
- Update documentation as needed
- Keep pull requests focused on a single change

## License

This project is proprietary and confidential. Unauthorized copying, distribution, or use is strictly prohibited.