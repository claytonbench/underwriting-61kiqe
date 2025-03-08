#!/bin/bash
#
# backup-db.sh - PostgreSQL database backup script for loan management system
#
# This script creates and manages PostgreSQL database backups, uploads them to S3,
# and implements retention policies according to configuration.
#
# Version: 1.0
# Requires: postgresql-client-15, aws-cli 2.0+, bash 4.0+

set -e  # Exit immediately if a command exits with a non-zero status
set -o pipefail  # Return value of a pipeline is the status of the last command

# Default values for global variables
DB_NAME=${DB_NAME:-loan_management}
DB_USER=${DB_USER:-postgres}
DB_PASSWORD=${DB_PASSWORD:-postgres}
DB_HOST=${DB_HOST:-localhost}
DB_PORT=${DB_PORT:-5432}
BACKUP_TYPE=${BACKUP_TYPE:-full}
BACKUP_DIR=${BACKUP_DIR:-/tmp/db_backups}
S3_BUCKET=${S3_BUCKET:-}
S3_PREFIX=${S3_PREFIX:-backups}
RETENTION_DAYS=${RETENTION_DAYS:-30}
ENVIRONMENT=${ENVIRONMENT:-development}
AWS_PROFILE=${AWS_PROFILE:-default}
AWS_REGION=${AWS_REGION:-us-east-1}

# Script location and logging
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
LOG_FILE="${SCRIPT_DIR}/backup-db.log"

# ANSI color codes for terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to display usage information
print_usage() {
    echo -e "${BLUE}PostgreSQL Database Backup Script for Loan Management System${NC}"
    echo
    echo "This script creates and manages PostgreSQL database backups, uploads them to S3,"
    echo "and implements retention policies according to configuration."
    echo
    echo -e "${YELLOW}Usage:${NC}"
    echo "  $0 [options]"
    echo
    echo -e "${YELLOW}Options:${NC}"
    echo "  -h, --help             Display this help message and exit"
    echo "  -n, --db-name NAME     Database name (default: ${DB_NAME})"
    echo "  -u, --db-user USER     Database user (default: ${DB_USER})"
    echo "  -p, --db-password PWD  Database password (default: not shown)"
    echo "  -H, --db-host HOST     Database host (default: ${DB_HOST})"
    echo "  -P, --db-port PORT     Database port (default: ${DB_PORT})"
    echo "  -t, --type TYPE        Backup type (full, incremental, transaction_log) (default: ${BACKUP_TYPE})"
    echo "  -d, --backup-dir DIR   Local backup directory (default: ${BACKUP_DIR})"
    echo "  -b, --s3-bucket BUCKET S3 bucket for backup storage (required for S3 upload)"
    echo "  -s, --s3-prefix PREFIX S3 prefix/path for backups (default: ${S3_PREFIX})"
    echo "  -r, --retention DAYS   Number of days to retain backups (default: ${RETENTION_DAYS})"
    echo "  -e, --environment ENV  Target environment (development, staging, production) (default: ${ENVIRONMENT})"
    echo "  -a, --aws-profile PROF AWS CLI profile to use (default: ${AWS_PROFILE})"
    echo "  -g, --aws-region REG   AWS region for S3 operations (default: ${AWS_REGION})"
    echo
    echo -e "${YELLOW}Examples:${NC}"
    echo "  # Perform a full backup with default settings"
    echo "  $0 -t full"
    echo
    echo "  # Perform a transaction log backup and upload to S3"
    echo "  $0 -t transaction_log -b my-backup-bucket -s db/logs -e production"
    echo
    echo "  # Perform an incremental backup with custom database credentials"
    echo "  $0 -t incremental -n mydb -u dbuser -p dbpass -H db.example.com -P 5432"
}

# Function to parse command line arguments
parse_arguments() {
    local TEMP=$(getopt -o hn:u:p:H:P:t:d:b:s:r:e:a:g: \
        --long help,db-name:,db-user:,db-password:,db-host:,db-port:,type:,backup-dir:,s3-bucket:,s3-prefix:,retention:,environment:,aws-profile:,aws-region: \
        -n 'backup-db.sh' -- "$@")

    if [ $? != 0 ]; then
        echo "Terminating..." >&2
        return 1
    fi

    eval set -- "$TEMP"

    while true; do
        case "$1" in
            -h | --help )
                print_usage
                exit 0
                ;;
            -n | --db-name )
                DB_NAME="$2"
                shift 2
                ;;
            -u | --db-user )
                DB_USER="$2"
                shift 2
                ;;
            -p | --db-password )
                DB_PASSWORD="$2"
                shift 2
                ;;
            -H | --db-host )
                DB_HOST="$2"
                shift 2
                ;;
            -P | --db-port )
                DB_PORT="$2"
                shift 2
                ;;
            -t | --type )
                BACKUP_TYPE="$2"
                shift 2
                ;;
            -d | --backup-dir )
                BACKUP_DIR="$2"
                shift 2
                ;;
            -b | --s3-bucket )
                S3_BUCKET="$2"
                shift 2
                ;;
            -s | --s3-prefix )
                S3_PREFIX="$2"
                shift 2
                ;;
            -r | --retention )
                RETENTION_DAYS="$2"
                shift 2
                ;;
            -e | --environment )
                ENVIRONMENT="$2"
                shift 2
                ;;
            -a | --aws-profile )
                AWS_PROFILE="$2"
                shift 2
                ;;
            -g | --aws-region )
                AWS_REGION="$2"
                shift 2
                ;;
            -- )
                shift
                break
                ;;
            * )
                echo "Internal error!"
                return 1
                ;;
        esac
    done

    # Validate backup type
    if [[ ! "$BACKUP_TYPE" =~ ^(full|incremental|transaction_log)$ ]]; then
        echo "Error: Invalid backup type: $BACKUP_TYPE. Must be one of: full, incremental, transaction_log" >&2
        return 1
    fi

    # Validate environment
    if [[ ! "$ENVIRONMENT" =~ ^(development|staging|production)$ ]]; then
        echo "Warning: Unconventional environment name: $ENVIRONMENT" >&2
    fi

    # Validate retention days is a positive integer
    if ! [[ "$RETENTION_DAYS" =~ ^[0-9]+$ ]] || [ "$RETENTION_DAYS" -lt 1 ]; then
        echo "Error: Retention days must be a positive integer" >&2
        return 1
    fi

    # If S3 bucket is specified, validate AWS settings
    if [ -n "$S3_BUCKET" ]; then
        if [ -z "$AWS_PROFILE" ] && [ -z "$AWS_ACCESS_KEY_ID" ]; then
            echo "Warning: Neither AWS_PROFILE nor AWS_ACCESS_KEY_ID is set. S3 upload may fail." >&2
        fi
    fi

    return 0
}

# Function to log messages
log_message() {
    local level=$1
    local message=$2
    local timestamp=$(date +"%Y-%m-%d %H:%M:%S")
    local log_entry="[$timestamp] [$level] $message"
    
    # Create log file if it doesn't exist
    if [ ! -f "$LOG_FILE" ]; then
        touch "$LOG_FILE" 2>/dev/null || {
            echo "Warning: Could not create log file at $LOG_FILE. Logging to stdout only."
        }
    }
    
    # Output to console with color
    case $level in
        INFO)
            echo -e "${GREEN}$log_entry${NC}"
            ;;
        WARNING)
            echo -e "${YELLOW}$log_entry${NC}"
            ;;
        ERROR)
            echo -e "${RED}$log_entry${NC}" >&2
            ;;
        *)
            echo -e "$log_entry"
            ;;
    esac
    
    # Append to log file
    if [ -f "$LOG_FILE" ] && [ -w "$LOG_FILE" ]; then
        echo "$log_entry" >> "$LOG_FILE"
    fi
}

# Function to check if required dependencies are installed
check_dependencies() {
    local missing_deps=0
    
    log_message "INFO" "Checking for required dependencies..."
    
    # Check for pg_dump
    if ! command -v pg_dump &> /dev/null; then
        log_message "ERROR" "pg_dump not found. Please install postgresql-client package."
        missing_deps=$((missing_deps + 1))
    else
        local pg_version=$(pg_dump --version | head -n 1 | awk '{print $3}')
        log_message "INFO" "Found pg_dump version: $pg_version"
    fi
    
    # Check for AWS CLI if S3 bucket is specified
    if [ -n "$S3_BUCKET" ]; then
        if ! command -v aws &> /dev/null; then
            log_message "ERROR" "AWS CLI not found. Please install aws-cli package."
            missing_deps=$((missing_deps + 1))
        else
            local aws_version=$(aws --version | awk '{print $1}' | cut -d/ -f2)
            log_message "INFO" "Found AWS CLI version: $aws_version"
        fi
    fi
    
    # Check for gzip
    if ! command -v gzip &> /dev/null; then
        log_message "ERROR" "gzip not found. Please install gzip package."
        missing_deps=$((missing_deps + 1))
    fi
    
    if [ $missing_deps -gt 0 ]; then
        log_message "ERROR" "$missing_deps required dependencies are missing."
        return 1
    fi
    
    log_message "INFO" "All required dependencies are available."
    return 0
}

# Function to check PostgreSQL connection
check_postgres_connection() {
    log_message "INFO" "Checking PostgreSQL connection to $DB_HOST:$DB_PORT..."
    
    # Using PGPASSWORD environment variable to securely pass password to psql
    PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "SELECT 1" &> /dev/null
    
    if [ $? -eq 0 ]; then
        log_message "INFO" "Successfully connected to PostgreSQL database: $DB_NAME"
        return 0
    else
        log_message "ERROR" "Failed to connect to PostgreSQL database: $DB_NAME at $DB_HOST:$DB_PORT"
        return 1
    fi
}

# Function to create backup directory if it doesn't exist
create_backup_directory() {
    log_message "INFO" "Creating backup directory: $BACKUP_DIR"
    
    if [ ! -d "$BACKUP_DIR" ]; then
        mkdir -p "$BACKUP_DIR" || {
            log_message "ERROR" "Failed to create backup directory: $BACKUP_DIR"
            return 1
        }
    fi
    
    # Check if the directory is writable
    if [ ! -w "$BACKUP_DIR" ]; then
        log_message "ERROR" "Backup directory is not writable: $BACKUP_DIR"
        return 1
    fi
    
    log_message "INFO" "Backup directory is ready: $BACKUP_DIR"
    return 0
}

# Function to generate a backup filename
generate_backup_filename() {
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    local filename="${DB_NAME}_${ENVIRONMENT}_${BACKUP_TYPE}_${timestamp}.sql.gz"
    
    echo "$filename"
}

# Function to perform a full database backup
perform_full_backup() {
    local output_file=$1
    local full_path="${BACKUP_DIR}/${output_file}"
    
    log_message "INFO" "Starting full backup of database: $DB_NAME to $full_path"
    
    # Run pg_dump with appropriate options for a full backup
    # We pipe the output through gzip to compress it
    PGPASSWORD="$DB_PASSWORD" pg_dump \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        -F c \
        -b \
        -v \
        -f "${full_path%.gz}" || {
            log_message "ERROR" "Failed to create full backup"
            return 1
        }
    
    # Compress the backup
    gzip -f "${full_path%.gz}" || {
        log_message "ERROR" "Failed to compress backup file"
        return 1
    }
    
    # Check if backup file exists and has a reasonable size
    if [ -f "$full_path" ] && [ $(stat -c%s "$full_path") -gt 1000 ]; then
        log_message "INFO" "Full backup completed successfully: $(stat -c%s "$full_path") bytes"
        return 0
    else
        log_message "ERROR" "Backup file is missing or too small"
        return 1
    fi
}

# Function to perform an incremental backup
perform_incremental_backup() {
    local output_file=$1
    local full_path="${BACKUP_DIR}/${output_file}"
    
    log_message "INFO" "Starting incremental backup of database: $DB_NAME to $full_path"
    
    # Check if WAL archiving is enabled
    local wal_enabled=$(PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -t -c "SHOW wal_level;")
    
    if [[ "$wal_enabled" != *"replica"* && "$wal_enabled" != *"logical"* ]]; then
        log_message "ERROR" "PostgreSQL WAL archiving is not properly configured. wal_level must be 'replica' or 'logical'."
        return 1
    fi
    
    # Get the last archived WAL file
    local last_wal=$(PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT pg_walfile_name(pg_current_wal_lsn());")
    
    # Create temporary directory for WAL files
    local temp_wal_dir="${BACKUP_DIR}/wal_temp_$$"
    mkdir -p "$temp_wal_dir" || {
        log_message "ERROR" "Failed to create temporary WAL directory"
        return 1
    }
    
    # Use pg_basebackup to get WAL files
    PGPASSWORD="$DB_PASSWORD" pg_basebackup \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -D "$temp_wal_dir" \
        -X stream \
        --checkpoint=fast \
        --progress || {
            log_message "ERROR" "Failed to perform incremental backup"
            rm -rf "$temp_wal_dir"
            return 1
        }
    
    # Compress the WAL files
    tar -czf "$full_path" -C "$temp_wal_dir" . || {
        log_message "ERROR" "Failed to compress WAL files"
        rm -rf "$temp_wal_dir"
        return 1
    }
    
    # Clean up temporary directory
    rm -rf "$temp_wal_dir"
    
    # Check if backup file exists and has a reasonable size
    if [ -f "$full_path" ] && [ $(stat -c%s "$full_path") -gt 1000 ]; then
        log_message "INFO" "Incremental backup completed successfully: $(stat -c%s "$full_path") bytes"
        return 0
    else
        log_message "ERROR" "Backup file is missing or too small"
        return 1
    fi
}

# Function to perform a transaction log backup
perform_transaction_log_backup() {
    local output_file=$1
    local full_path="${BACKUP_DIR}/${output_file}"
    
    log_message "INFO" "Starting transaction log backup of database: $DB_NAME to $full_path"
    
    # Create temporary directory for transaction logs
    local temp_log_dir="${BACKUP_DIR}/txlog_temp_$$"
    mkdir -p "$temp_log_dir" || {
        log_message "ERROR" "Failed to create temporary transaction log directory"
        return 1
    }
    
    # Use pg_basebackup with --wal-method=fetch to get transaction logs
    PGPASSWORD="$DB_PASSWORD" pg_basebackup \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -D "$temp_log_dir" \
        --wal-method=fetch \
        --progress || {
            log_message "ERROR" "Failed to perform transaction log backup"
            rm -rf "$temp_log_dir"
            return 1
        }
    
    # Compress the transaction logs
    tar -czf "$full_path" -C "$temp_log_dir" pg_wal || {
        log_message "ERROR" "Failed to compress transaction logs"
        rm -rf "$temp_log_dir"
        return 1
    }
    
    # Clean up temporary directory
    rm -rf "$temp_log_dir"
    
    # Check if backup file exists and has a reasonable size
    if [ -f "$full_path" ] && [ $(stat -c%s "$full_path") -gt 1000 ]; then
        log_message "INFO" "Transaction log backup completed successfully: $(stat -c%s "$full_path") bytes"
        return 0
    else
        log_message "ERROR" "Backup file is missing or too small"
        return 1
    fi
}

# Function to upload backup to S3
upload_to_s3() {
    local local_file=$1
    local full_path="${BACKUP_DIR}/${local_file}"
    
    # Skip if no S3 bucket is specified
    if [ -z "$S3_BUCKET" ]; then
        log_message "WARNING" "No S3 bucket specified. Skipping upload."
        return 0
    fi
    
    log_message "INFO" "Uploading backup to S3: s3://${S3_BUCKET}/${S3_PREFIX}/${local_file}"
    
    # Set up AWS CLI profile if specified
    local profile_arg=""
    if [ -n "$AWS_PROFILE" ]; then
        profile_arg="--profile $AWS_PROFILE"
    fi
    
    # Set up AWS CLI region if specified
    local region_arg=""
    if [ -n "$AWS_REGION" ]; then
        region_arg="--region $AWS_REGION"
    fi
    
    # Upload to S3
    aws $profile_arg $region_arg s3 cp "$full_path" "s3://${S3_BUCKET}/${S3_PREFIX}/${local_file}" || {
        log_message "ERROR" "Failed to upload backup to S3"
        return 1
    }
    
    # Verify upload by checking if file exists in S3
    aws $profile_arg $region_arg s3 ls "s3://${S3_BUCKET}/${S3_PREFIX}/${local_file}" &>/dev/null || {
        log_message "ERROR" "Failed to verify backup upload to S3"
        return 1
    }
    
    log_message "INFO" "Successfully uploaded backup to S3"
    return 0
}

# Function to clean up old backups based on retention policy
cleanup_old_backups() {
    log_message "INFO" "Cleaning up backups older than $RETENTION_DAYS days"
    
    # Skip if no S3 bucket is specified
    if [ -z "$S3_BUCKET" ]; then
        log_message "INFO" "Cleaning up local backups only"
    else
        log_message "INFO" "Cleaning up backups in S3 and locally"
        
        # Set up AWS CLI profile if specified
        local profile_arg=""
        if [ -n "$AWS_PROFILE" ]; then
            profile_arg="--profile $AWS_PROFILE"
        fi
        
        # Set up AWS CLI region if specified
        local region_arg=""
        if [ -n "$AWS_REGION" ]; then
            region_arg="--region $AWS_REGION"
        fi
        
        # Calculate cutoff date (current date - retention days)
        local cutoff_date=$(date -d "$RETENTION_DAYS days ago" +%s)
        
        # List objects in S3 bucket with the specified prefix
        local objects=$(aws $profile_arg $region_arg s3 ls "s3://${S3_BUCKET}/${S3_PREFIX}/" --recursive)
        
        # Process each object
        echo "$objects" | while read -r line; do
            # Skip empty lines
            [ -z "$line" ] && continue
            
            # Extract date and key from ls output
            local obj_date=$(echo "$line" | awk '{print $1" "$2}')
            local obj_key=$(echo "$line" | awk '{$1=$2=$3=""; print $0}' | sed 's/^[ \t]*//')
            
            # Convert object date to seconds since epoch
            local obj_epoch=$(date -d "$obj_date" +%s)
            
            # Check if object is older than cutoff date
            if [ "$obj_epoch" -lt "$cutoff_date" ]; then
                log_message "INFO" "Deleting old backup from S3: $obj_key"
                aws $profile_arg $region_arg s3 rm "s3://${S3_BUCKET}/$obj_key" || {
                    log_message "WARNING" "Failed to delete old backup from S3: $obj_key"
                }
            fi
        done
    fi
    
    # Clean up local backup directory
    log_message "INFO" "Deleting local backups older than $RETENTION_DAYS days"
    find "$BACKUP_DIR" -name "*.sql.gz" -type f -mtime +$RETENTION_DAYS -delete
    
    log_message "INFO" "Backup cleanup completed"
    return 0
}

# Function to verify backup integrity
verify_backup() {
    local backup_file=$1
    local full_path="${BACKUP_DIR}/${backup_file}"
    
    log_message "INFO" "Verifying backup integrity: $backup_file"
    
    # Check if backup file exists and is not empty
    if [ ! -f "$full_path" ]; then
        log_message "ERROR" "Backup file not found: $full_path"
        return 1
    fi
    
    if [ ! -s "$full_path" ]; then
        log_message "ERROR" "Backup file is empty: $full_path"
        return 1
    fi
    
    # For full backups, check if the file can be read by pg_restore
    if [ "$BACKUP_TYPE" = "full" ]; then
        # Test if the backup can be read
        if [[ "$full_path" == *.gz ]]; then
            gunzip -c "$full_path" | pg_restore --list > /dev/null 2>&1 || {
                log_message "ERROR" "Backup file is corrupt or invalid format"
                return 1
            }
        else
            pg_restore --list "$full_path" > /dev/null 2>&1 || {
                log_message "ERROR" "Backup file is corrupt or invalid format"
                return 1
            }
        fi
    elif [ "$BACKUP_TYPE" = "incremental" ] || [ "$BACKUP_TYPE" = "transaction_log" ]; then
        # For incremental or transaction log backups, check if the archive can be listed
        tar -tzf "$full_path" > /dev/null 2>&1 || {
            log_message "ERROR" "Backup archive is corrupt or invalid format"
            return 1
        }
    fi
    
    log_message "INFO" "Backup verification completed successfully"
    return 0
}

# Main function
main() {
    local exit_code=0
    
    # Parse command line arguments
    parse_arguments "$@" || {
        print_usage
        return 1
    }
    
    log_message "INFO" "Starting database backup process for $DB_NAME (type: $BACKUP_TYPE, environment: $ENVIRONMENT)"
    
    # Check dependencies
    check_dependencies || {
        log_message "ERROR" "Missing required dependencies. Aborting."
        return 1
    }
    
    # Check PostgreSQL connection
    check_postgres_connection || {
        log_message "ERROR" "Cannot connect to PostgreSQL database. Aborting."
        return 1
    }
    
    # Create backup directory
    create_backup_directory || {
        log_message "ERROR" "Failed to create backup directory. Aborting."
        return 1
    }
    
    # Generate backup filename
    local backup_filename=$(generate_backup_filename)
    log_message "INFO" "Using backup filename: $backup_filename"
    
    # Perform backup based on type
    case "$BACKUP_TYPE" in
        full)
            perform_full_backup "$backup_filename" || exit_code=1
            ;;
        incremental)
            perform_incremental_backup "$backup_filename" || exit_code=1
            ;;
        transaction_log)
            perform_transaction_log_backup "$backup_filename" || exit_code=1
            ;;
        *)
            log_message "ERROR" "Unknown backup type: $BACKUP_TYPE"
            exit_code=1
            ;;
    esac
    
    if [ $exit_code -eq 0 ]; then
        # Verify backup integrity
        verify_backup "$backup_filename" || {
            log_message "ERROR" "Backup verification failed"
            exit_code=1
        }
        
        # Upload to S3 if a bucket is specified
        if [ -n "$S3_BUCKET" ] && [ $exit_code -eq 0 ]; then
            upload_to_s3 "$backup_filename" || exit_code=1
        fi
        
        # Clean up old backups
        if [ $exit_code -eq 0 ]; then
            cleanup_old_backups || log_message "WARNING" "Backup cleanup failed but backup was created successfully"
        fi
    fi
    
    if [ $exit_code -eq 0 ]; then
        log_message "INFO" "Database backup process completed successfully"
    else
        log_message "ERROR" "Database backup process failed"
    fi
    
    return $exit_code
}

# Execute main function with all arguments
main "$@"