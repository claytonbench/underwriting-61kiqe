#!/bin/bash
#
# init-db.sh - Initialize PostgreSQL database for the loan management system
#
# This script creates the database if it doesn't exist, applies migrations,
# creates an initial superuser, and loads essential reference data.
# It's designed to be run during initial deployment or in CI/CD pipelines
# to ensure proper database setup.
#
# Dependencies:
# - PostgreSQL client (psql) version 15
# - Python 3.11+ with Django

# Exit on any error
set -e

# Default values for database connection (can be overridden by environment variables)
DB_NAME=${DB_NAME:-"loan_management"}
DB_USER=${DB_USER:-"postgres"}
DB_PASSWORD=${DB_PASSWORD:-"postgres"}
DB_HOST=${DB_HOST:-"localhost"}
DB_PORT=${DB_PORT:-"5432"}

# Default values for admin user (can be overridden by environment variables)
ADMIN_EMAIL=${ADMIN_EMAIL:-"admin@example.com"}
ADMIN_PASSWORD=${ADMIN_PASSWORD:-"admin"}

# Django settings
DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE:-"config.settings.production"}

# Get the directory containing this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Print usage information
print_usage() {
    echo "Usage: $(basename $0) [options]"
    echo
    echo "Initialize PostgreSQL database for the loan management system."
    echo
    echo "Options:"
    echo "  -h, --help                 Show this help message and exit"
    echo "  -n, --name NAME            Database name (default: $DB_NAME)"
    echo "  -u, --user USER            Database user (default: $DB_USER)"
    echo "  -p, --password PASSWORD    Database password (default: ********)"
    echo "  -H, --host HOST            Database host (default: $DB_HOST)"
    echo "  -P, --port PORT            Database port (default: $DB_PORT)"
    echo "  -e, --admin-email EMAIL    Admin email (default: $ADMIN_EMAIL)"
    echo "  -a, --admin-password PWD   Admin password (default: ********)"
    echo "  -s, --settings MODULE      Django settings module (default: $DJANGO_SETTINGS_MODULE)"
    echo
    echo "Example:"
    echo "  $(basename $0) --name mydb --user dbuser --host db.example.com"
    echo
    echo "Environment variables:"
    echo "  The following environment variables can be used instead of command-line options:"
    echo "  DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT,"
    echo "  ADMIN_EMAIL, ADMIN_PASSWORD, DJANGO_SETTINGS_MODULE"
}

# Parse command-line arguments
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -h|--help)
                print_usage
                exit 0
                ;;
            -n|--name)
                DB_NAME="$2"
                shift 2
                ;;
            -u|--user)
                DB_USER="$2"
                shift 2
                ;;
            -p|--password)
                DB_PASSWORD="$2"
                shift 2
                ;;
            -H|--host)
                DB_HOST="$2"
                shift 2
                ;;
            -P|--port)
                DB_PORT="$2"
                shift 2
                ;;
            -e|--admin-email)
                ADMIN_EMAIL="$2"
                shift 2
                ;;
            -a|--admin-password)
                ADMIN_PASSWORD="$2"
                shift 2
                ;;
            -s|--settings)
                DJANGO_SETTINGS_MODULE="$2"
                shift 2
                ;;
            *)
                echo "Error: Unknown option: $1" >&2
                print_usage
                return 1
                ;;
        esac
    done

    # Validate required parameters
    if [[ -z "$DB_NAME" || -z "$DB_USER" || -z "$DB_PASSWORD" ]]; then
        echo "Error: Database name, user, and password are required." >&2
        print_usage
        return 1
    fi

    return 0
}

# Check if required dependencies are installed
check_dependencies() {
    local missing_deps=0

    # Check for psql
    if ! command -v psql &> /dev/null; then
        echo "Error: PostgreSQL client (psql) is not installed or not in PATH." >&2
        echo "Please install postgresql-client package version 15 or higher." >&2
        missing_deps=1
    else
        # Check PostgreSQL client version
        psql_version=$(psql --version | sed 's/psql (PostgreSQL) //')
        if [[ $(echo "$psql_version" | cut -d. -f1) -lt 15 ]]; then
            echo "Error: PostgreSQL client version 15 or higher is required (found $psql_version)." >&2
            missing_deps=1
        fi
    fi

    # Check for Python
    if ! command -v python &> /dev/null; then
        echo "Error: Python is not installed or not in PATH." >&2
        echo "Please install Python 3.11 or higher." >&2
        missing_deps=1
    else
        # Check Python version
        python_version=$(python --version 2>&1 | sed 's/Python //')
        if [[ $(echo "$python_version" | cut -d. -f1) -lt 3 || ($(echo "$python_version" | cut -d. -f1) -eq 3 && $(echo "$python_version" | cut -d. -f2) -lt 11) ]]; then
            echo "Error: Python 3.11 or higher is required (found $python_version)." >&2
            missing_deps=1
        fi
    fi

    return $missing_deps
}

# Check if PostgreSQL server is available and accessible
check_postgres_connection() {
    echo "Checking PostgreSQL connection..."
    
    # Use PGPASSWORD environment variable to avoid password prompt
    export PGPASSWORD="$DB_PASSWORD"
    
    if ! psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -c "SELECT 1" postgres &> /dev/null; then
        echo "Error: Cannot connect to PostgreSQL server at $DB_HOST:$DB_PORT." >&2
        echo "Please check your connection parameters and ensure the server is running." >&2
        return 1
    fi
    
    echo "PostgreSQL connection successful."
    return 0
}

# Create the database if it doesn't exist
create_database_if_not_exists() {
    echo "Checking if database '$DB_NAME' exists..."
    
    # Check if database exists
    export PGPASSWORD="$DB_PASSWORD"
    if psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -lqt | cut -d \| -f 1 | grep -qw "$DB_NAME"; then
        echo "Database '$DB_NAME' already exists."
    else
        echo "Creating database '$DB_NAME'..."
        psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -c "CREATE DATABASE $DB_NAME WITH ENCODING 'UTF8' LC_COLLATE='en_US.UTF-8' LC_CTYPE='en_US.UTF-8' TEMPLATE=template0;" postgres
        echo "Database '$DB_NAME' created successfully."
    fi
    
    return 0
}

# Apply Django migrations to set up database schema
apply_migrations() {
    echo "Applying database migrations..."
    
    # Set Django settings module
    export DJANGO_SETTINGS_MODULE="$DJANGO_SETTINGS_MODULE"
    export DATABASE_URL="postgres://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME"
    
    # Navigate to Django project root (assuming standard structure)
    cd "$SCRIPT_DIR/../../"
    
    # Apply migrations
    if ! python manage.py migrate --no-input; then
        echo "Error: Failed to apply database migrations." >&2
        return 1
    fi
    
    echo "Database migrations applied successfully."
    return 0
}

# Create initial superuser for admin access
create_superuser() {
    echo "Checking if superuser exists..."
    
    # Set Django settings module
    export DJANGO_SETTINGS_MODULE="$DJANGO_SETTINGS_MODULE"
    export DATABASE_URL="postgres://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME"
    
    # Navigate to Django project root
    cd "$SCRIPT_DIR/../../"
    
    # Check if superuser already exists
    if python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); print(User.objects.filter(email='$ADMIN_EMAIL', is_superuser=True).exists())" | grep -q "True"; then
        echo "Superuser with email '$ADMIN_EMAIL' already exists."
    else
        echo "Creating superuser with email '$ADMIN_EMAIL'..."
        # Create superuser using Django management command
        python manage.py shell -c "
from django.contrib.auth import get_user_model;
User = get_user_model();
if not User.objects.filter(email='$ADMIN_EMAIL').exists():
    User.objects.create_superuser('$ADMIN_EMAIL', '$ADMIN_EMAIL', '$ADMIN_PASSWORD');
    print('Superuser created successfully.');
else:
    print('User with this email already exists, but is not a superuser.');
"
    fi
    
    return 0
}

# Load initial reference data from fixtures
load_initial_data() {
    echo "Loading initial reference data..."
    
    # Set Django settings module
    export DJANGO_SETTINGS_MODULE="$DJANGO_SETTINGS_MODULE"
    export DATABASE_URL="postgres://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME"
    
    # Navigate to Django project root
    cd "$SCRIPT_DIR/../../"
    
    # Define fixtures to load in the correct order
    declare -a fixtures=(
        "roles_permissions"
        "document_templates"
        "notification_templates"
        "school_programs"
    )
    
    # Load each fixture
    for fixture in "${fixtures[@]}"; do
        echo "Loading fixture: $fixture"
        if ! python manage.py loaddata "$fixture"; then
            echo "Warning: Failed to load fixture '$fixture'. This may be expected if the fixture doesn't exist." >&2
        fi
    done
    
    echo "Initial reference data loaded successfully."
    return 0
}

# Main function
main() {
    # Parse command-line arguments
    if ! parse_arguments "$@"; then
        return 1
    fi
    
    # Check if required dependencies are installed
    if ! check_dependencies; then
        return 1
    fi
    
    # Check PostgreSQL connection
    if ! check_postgres_connection; then
        return 1
    fi
    
    # Create database if it doesn't exist
    if ! create_database_if_not_exists; then
        return 1
    fi
    
    # Apply migrations
    if ! apply_migrations; then
        return 1
    fi
    
    # Create superuser
    if ! create_superuser; then
        return 1
    fi
    
    # Load initial data
    if ! load_initial_data; then
        return 1
    fi
    
    echo "Database initialization completed successfully."
    return 0
}

# Export functions that may be useful to other scripts
export -f check_postgres_connection

# Only run main if the script is being executed directly (not sourced)
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
    exit $?
fi