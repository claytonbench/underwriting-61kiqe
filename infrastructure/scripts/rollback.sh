#!/bin/bash
#
# rollback.sh - Rollback script for loan management system deployments
#
# This script handles rolling back deployments when issues are detected.
# It can revert ECS services to previous task definitions, restore database
# from backups, and roll back infrastructure changes.
#
# Version: 1.0
# Requires: aws-cli 2.0+, jq 1.6+, bash 4.0+

# Exit on error, enable pipefail
set -e
set -o pipefail

# Default values for global variables
ENVIRONMENT=""
AWS_REGION=${AWS_REGION:-"us-east-1"}
AWS_PROFILE=${AWS_PROFILE:-"default"}
ROLLBACK_TYPE="service"  # Default to service rollback
SERVICES="backend,frontend"  # Default to both services
PREVIOUS_VERSION=""  # Specific version to roll back to (optional)
BACKUP_ID=""  # Specific backup ID to restore from (optional)
SKIP_CONFIRMATION=false
FORCE_ROLLBACK=false

# Script location and logging
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
LOG_FILE="${SCRIPT_DIR}/rollback-$(date +%Y%m%d-%H%M%S).log"

# ANSI color codes for terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to display usage information
print_usage() {
    echo -e "${BLUE}Loan Management System Rollback Script${NC}"
    echo
    echo "This script handles rolling back deployments when issues are detected."
    echo "It can revert ECS services to previous task definitions, restore database"
    echo "from backups, and roll back infrastructure changes."
    echo
    echo -e "${YELLOW}Usage:${NC}"
    echo "  $0 [options]"
    echo
    echo -e "${YELLOW}Options:${NC}"
    echo "  -h, --help                   Display this help message and exit"
    echo "  -e, --environment ENV        Target environment (development, staging, production) (required)"
    echo "  -r, --region REGION          AWS region (default: $AWS_REGION)"
    echo "  -p, --profile PROFILE        AWS CLI profile to use (default: $AWS_PROFILE)"
    echo "  -t, --type TYPE              Rollback type (service, database, infrastructure, full) (default: $ROLLBACK_TYPE)"
    echo "  -s, --services SERVICES      Comma-separated list of services to roll back (default: $SERVICES)"
    echo "  -v, --version VERSION        Specific version to roll back to (optional)"
    echo "  -b, --backup-id ID           Specific database backup ID to restore from (optional)"
    echo "  -y, --yes                    Skip confirmation prompts"
    echo "  -f, --force                  Force rollback even if validation fails"
    echo
    echo -e "${YELLOW}Examples:${NC}"
    echo "  # Roll back services in development environment"
    echo "  $0 -e development"
    echo
    echo "  # Roll back specific service in production with a specific version"
    echo "  $0 -e production -t service -s backend -v v1.2.3"
    echo
    echo "  # Perform a full rollback in staging environment"
    echo "  $0 -e staging -t full -y"
    echo
    echo "  # Restore database from specific backup in production"
    echo "  $0 -e production -t database -b backup-2023-05-01-120000"
}

# Function to parse command line arguments
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -h|--help)
                print_usage
                exit 0
                ;;
            -e|--environment)
                ENVIRONMENT="$2"
                shift 2
                ;;
            -r|--region)
                AWS_REGION="$2"
                shift 2
                ;;
            -p|--profile)
                AWS_PROFILE="$2"
                shift 2
                ;;
            -t|--type)
                ROLLBACK_TYPE="$2"
                shift 2
                ;;
            -s|--services)
                SERVICES="$2"
                shift 2
                ;;
            -v|--version)
                PREVIOUS_VERSION="$2"
                shift 2
                ;;
            -b|--backup-id)
                BACKUP_ID="$2"
                shift 2
                ;;
            -y|--yes)
                SKIP_CONFIRMATION=true
                shift
                ;;
            -f|--force)
                FORCE_ROLLBACK=true
                shift
                ;;
            *)
                echo "Unknown option: $1"
                print_usage
                return 1
                ;;
        esac
    done

    # Validate required arguments
    if [[ -z "$ENVIRONMENT" ]]; then
        echo "Error: Environment (-e, --environment) is required"
        return 1
    fi

    # Validate environment value
    if [[ ! "$ENVIRONMENT" =~ ^(development|staging|production)$ ]]; then
        echo "Error: Environment must be one of: development, staging, production"
        return 1
    fi

    # Validate rollback type
    if [[ ! "$ROLLBACK_TYPE" =~ ^(service|database|infrastructure|full)$ ]]; then
        echo "Error: Rollback type must be one of: service, database, infrastructure, full"
        return 1
    fi

    return 0
}

# Function to set service names based on environment
set_service_names() {
    # Set cluster name based on environment
    case "$ENVIRONMENT" in
        development)
            CLUSTER_NAME="loan-management-dev"
            BACKEND_SERVICE="loan-management-backend-dev"
            FRONTEND_SERVICE="loan-management-frontend-dev"
            ;;
        staging)
            CLUSTER_NAME="loan-management-staging"
            BACKEND_SERVICE="loan-management-backend-staging"
            FRONTEND_SERVICE="loan-management-frontend-staging"
            ;;
        production)
            CLUSTER_NAME="loan-management-prod"
            BACKEND_SERVICE="loan-management-backend-prod"
            FRONTEND_SERVICE="loan-management-frontend-prod"
            ;;
        *)
            log_message "ERROR" "Unknown environment: $ENVIRONMENT"
            return 1
            ;;
    esac
}

# Function to confirm rollback with user
confirm_rollback() {
    if [[ "$SKIP_CONFIRMATION" = true ]]; then
        return 0
    fi
    
    echo ""
    echo -e "${YELLOW}!!! CAUTION: You are about to roll back the $ENVIRONMENT environment !!!${NC}"
    echo ""
    echo "Rollback details:"
    echo "  Environment: $ENVIRONMENT"
    echo "  Rollback type: $ROLLBACK_TYPE"
    
    if [[ "$ROLLBACK_TYPE" = "service" || "$ROLLBACK_TYPE" = "full" ]]; then
        echo "  Services: $SERVICES"
        if [[ -n "$PREVIOUS_VERSION" ]]; then
            echo "  Rolling back to version: $PREVIOUS_VERSION"
        else
            echo "  Rolling back to previous version"
        fi
    fi
    
    if [[ "$ROLLBACK_TYPE" = "database" || "$ROLLBACK_TYPE" = "full" ]]; then
        if [[ -n "$BACKUP_ID" ]]; then
            echo "  Restoring from backup ID: $BACKUP_ID"
        else
            echo "  Restoring from latest backup"
        fi
        echo -e "${RED}  WARNING: This will replace the current database content!${NC}"
    fi
    
    if [[ "$ROLLBACK_TYPE" = "infrastructure" || "$ROLLBACK_TYPE" = "full" ]]; then
        echo -e "${RED}  WARNING: Infrastructure rollback may have significant impact!${NC}"
    fi
    
    echo ""
    echo -e "${YELLOW}This action may cause service disruption and data changes.${NC}"
    read -p "Are you sure you want to proceed with rollback? (y/n): " -n 1 -r
    echo ""
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_message "INFO" "Rollback canceled by user"
        return 1
    fi
    
    return 0
}

# Function to get previous task definition for a service
get_previous_task_definition() {
    local service_name=$1
    
    log_message "INFO" "Retrieving previous task definition for $service_name"
    
    # List task definitions for the service family
    local family_name="${service_name}"
    local task_definitions=$(aws ecs list-task-definitions \
        --region "$AWS_REGION" \
        --profile "$AWS_PROFILE" \
        --family-prefix "$family_name" \
        --sort DESC \
        --query "taskDefinitionArns" \
        --output json)
    
    # Find the appropriate previous version
    local previous_task_def=""
    
    if [[ -n "$PREVIOUS_VERSION" ]]; then
        # Look for a specific version
        previous_task_def=$(echo "$task_definitions" | jq -r '.[] | select(contains(":'$PREVIOUS_VERSION'"))')
        
        if [[ -z "$previous_task_def" ]]; then
            log_message "ERROR" "Could not find task definition for version $PREVIOUS_VERSION"
            return 1
        fi
    else
        # Get the second task definition in the list (current one is the first)
        previous_task_def=$(echo "$task_definitions" | jq -r '.[1]')
        
        if [[ -z "$previous_task_def" || "$previous_task_def" == "null" ]]; then
            log_message "ERROR" "No previous task definition found for $service_name"
            return 1
        fi
    fi
    
    echo "$previous_task_def"
    return 0
}

# Function to roll back a specific service
rollback_service() {
    local service_name=$1
    
    log_message "INFO" "Rolling back service: $service_name"
    
    # Get previous task definition
    local previous_task_def=$(get_previous_task_definition "$service_name")
    
    if [[ -z "$previous_task_def" ]]; then
        log_message "ERROR" "Failed to get previous task definition for $service_name"
        return 1
    fi
    
    log_message "INFO" "Using previous task definition: $previous_task_def"
    
    # Update service to use previous task definition
    log_message "INFO" "Updating service to use previous task definition"
    aws ecs update-service \
        --cluster "$CLUSTER_NAME" \
        --service "$service_name" \
        --task-definition "$previous_task_def" \
        --region "$AWS_REGION" \
        --profile "$AWS_PROFILE" > /dev/null || {
        log_message "ERROR" "Failed to update service"
        return 1
    }
    
    # Wait for service to stabilize
    log_message "INFO" "Waiting for service to stabilize..."
    wait_for_service_stability "$service_name" || {
        if [[ "$FORCE_ROLLBACK" = true ]]; then
            log_message "WARNING" "Service failed to stabilize, but continuing due to force flag"
        else
            log_message "ERROR" "Service failed to stabilize"
            return 1
        fi
    }
    
    log_message "INFO" "Service rollback completed for $service_name"
    return 0
}

# Function to roll back database
rollback_database() {
    log_message "INFO" "Rolling back database"
    
    # Source backup-db.sh for database functions
    source "$SCRIPT_DIR/backup-db.sh" || {
        log_message "ERROR" "Failed to source backup-db.sh"
        return 1
    }
    
    # Check database connection
    check_postgres_connection || {
        log_message "ERROR" "Database connection check failed"
        return 1
    }
    
    # Get database connection parameters from environment
    local DB_HOST=$DB_HOST
    local S3_BUCKET="${ENVIRONMENT}-loan-management-backups"
    local S3_PREFIX="database"
    local backup_file=""
    
    # If a specific backup ID is provided, use it
    if [[ -n "$BACKUP_ID" ]]; then
        log_message "INFO" "Using specified backup ID: $BACKUP_ID"
        backup_file="$BACKUP_ID.sql.gz"
    else
        # Find the most recent backup before the deployment
        log_message "INFO" "Finding most recent backup"
        local latest_backup=$(aws s3 ls "s3://$S3_BUCKET/$S3_PREFIX/" \
            --region "$AWS_REGION" \
            --profile "$AWS_PROFILE" \
            --recursive | sort -r | head -n 1 | awk '{print $4}')
        
        backup_file=$(basename "$latest_backup")
        log_message "INFO" "Using latest backup: $backup_file"
    fi
    
    # Create a temporary directory for the backup
    local temp_dir=$(mktemp -d)
    local backup_path="$temp_dir/$backup_file"
    
    # Download the backup file
    log_message "INFO" "Downloading backup file from S3"
    aws s3 cp "s3://$S3_BUCKET/$S3_PREFIX/$backup_file" "$backup_path" \
        --region "$AWS_REGION" \
        --profile "$AWS_PROFILE" || {
        log_message "ERROR" "Failed to download backup file"
        rm -rf "$temp_dir"
        return 1
    }
    
    # Stop application services to prevent writes during restore
    log_message "INFO" "Stopping application services before database restore"
    if [[ "$SERVICES" == *"backend"* ]]; then
        log_message "INFO" "Scaling down backend service"
        aws ecs update-service \
            --cluster "$CLUSTER_NAME" \
            --service "$BACKEND_SERVICE" \
            --desired-count 0 \
            --region "$AWS_REGION" \
            --profile "$AWS_PROFILE" > /dev/null || {
            log_message "WARNING" "Failed to scale down backend service, but continuing with restore"
        }
        
        # Wait for tasks to stop
        aws ecs wait services-stable \
            --cluster "$CLUSTER_NAME" \
            --services "$BACKEND_SERVICE" \
            --region "$AWS_REGION" \
            --profile "$AWS_PROFILE" || {
            log_message "WARNING" "Backend service did not stabilize at 0 tasks, but continuing with restore"
        }
    fi
    
    # Restore the database
    log_message "INFO" "Restoring database from backup"
    if [[ "$backup_file" == *.gz ]]; then
        gunzip -c "$backup_path" | PGPASSWORD="$DB_PASSWORD" psql \
            -h "$DB_HOST" \
            -p "$DB_PORT" \
            -U "$DB_USER" \
            -d "$DB_NAME" || {
            log_message "ERROR" "Failed to restore database"
            # Start services back up before exiting
            if [[ "$SERVICES" == *"backend"* ]]; then
                log_message "INFO" "Scaling backend service back up"
                aws ecs update-service \
                    --cluster "$CLUSTER_NAME" \
                    --service "$BACKEND_SERVICE" \
                    --desired-count 2 \
                    --region "$AWS_REGION" \
                    --profile "$AWS_PROFILE" > /dev/null
            fi
            rm -rf "$temp_dir"
            return 1
        }
    else
        PGPASSWORD="$DB_PASSWORD" psql \
            -h "$DB_HOST" \
            -p "$DB_PORT" \
            -U "$DB_USER" \
            -d "$DB_NAME" \
            -f "$backup_path" || {
            log_message "ERROR" "Failed to restore database"
            # Start services back up before exiting
            if [[ "$SERVICES" == *"backend"* ]]; then
                log_message "INFO" "Scaling backend service back up"
                aws ecs update-service \
                    --cluster "$CLUSTER_NAME" \
                    --service "$BACKEND_SERVICE" \
                    --desired-count 2 \
                    --region "$AWS_REGION" \
                    --profile "$AWS_PROFILE" > /dev/null
            fi
            rm -rf "$temp_dir"
            return 1
        }
    fi
    
    # Start services back up
    if [[ "$SERVICES" == *"backend"* ]]; then
        log_message "INFO" "Scaling backend service back up"
        aws ecs update-service \
            --cluster "$CLUSTER_NAME" \
            --service "$BACKEND_SERVICE" \
            --desired-count 2 \
            --region "$AWS_REGION" \
            --profile "$AWS_PROFILE" > /dev/null || {
            log_message "WARNING" "Failed to scale up backend service. Manual intervention required."
        }
    fi
    
    # Clean up
    rm -rf "$temp_dir"
    
    # Verify database restoration
    log_message "INFO" "Verifying database restoration"
    check_postgres_connection || {
        log_message "ERROR" "Database connection check failed after restoration"
        return 1
    }
    
    log_message "INFO" "Database rollback completed successfully"
    return 0
}

# Function to roll back infrastructure
rollback_infrastructure() {
    log_message "INFO" "Rolling back infrastructure changes"
    
    # Change to Terraform directory
    cd "$SCRIPT_DIR/../terraform" || {
        log_message "ERROR" "Failed to change to Terraform directory"
        return 1
    }
    
    # Initialize Terraform
    log_message "INFO" "Initializing Terraform"
    terraform init -backend=true || {
        log_message "ERROR" "Failed to initialize Terraform"
        return 1
    }
    
    # Select workspace based on environment
    log_message "INFO" "Selecting Terraform workspace: $ENVIRONMENT"
    if ! terraform workspace select "$ENVIRONMENT" 2>/dev/null; then
        log_message "ERROR" "Failed to select Terraform workspace: $ENVIRONMENT"
        return 1
    }
    
    # Determine rollback approach based on inputs
    if [[ -n "$PREVIOUS_VERSION" ]]; then
        log_message "INFO" "Rolling back infrastructure to version: $PREVIOUS_VERSION"
        
        # Checkout specific state version for infrastructure
        git -C "$SCRIPT_DIR/../terraform" checkout "$PREVIOUS_VERSION" || {
            log_message "ERROR" "Failed to checkout infrastructure version: $PREVIOUS_VERSION"
            return 1
        }
    else
        log_message "INFO" "Rolling back infrastructure to previous state"
        
        # This is simplified - in a real environment, you might use Terraform state management,
        # or have versioned tfstate files in S3 that can be restored
        terraform state pull > terraform.tfstate.backup-current
        
        # List state versions in S3 backend (assuming S3 backend is used)
        local state_versions=$(aws s3api list-object-versions \
            --bucket "loan-management-terraform-state" \
            --key "$ENVIRONMENT/terraform.tfstate" \
            --region "$AWS_REGION" \
            --profile "$AWS_PROFILE" \
            --query 'Versions[?!IsLatest]' \
            --output json)
        
        # Get the previous state version ID
        local previous_version_id=$(echo "$state_versions" | jq -r '.[0].VersionId')
        
        # Get the previous state version
        aws s3api get-object \
            --bucket "loan-management-terraform-state" \
            --key "$ENVIRONMENT/terraform.tfstate" \
            --version-id "$previous_version_id" \
            --region "$AWS_REGION" \
            --profile "$AWS_PROFILE" \
            terraform.tfstate.previous || {
            log_message "ERROR" "Failed to get previous Terraform state"
            return 1
        }
        
        # Use the previous state
        mv terraform.tfstate.previous terraform.tfstate
    fi
    
    # Apply Terraform configuration
    log_message "INFO" "Applying Terraform configuration"
    local apply_cmd="terraform apply"
    
    # Add auto-approve if confirmation is skipped
    if [[ "$SKIP_CONFIRMATION" = true ]]; then
        apply_cmd="$apply_cmd -auto-approve"
    fi
    
    # Run the command
    $apply_cmd || {
        log_message "ERROR" "Failed to apply Terraform configuration"
        return 1
    }
    
    log_message "INFO" "Infrastructure rollback completed"
    return 0
}

# Function to wait for service stability
wait_for_service_stability() {
    local service_name=$1
    
    log_message "INFO" "Waiting for service to stabilize: $service_name"
    
    # Set timeout based on environment (longer for production)
    local timeout=600  # 10 minutes default
    if [[ "$ENVIRONMENT" = "production" ]]; then
        timeout=1200  # 20 minutes for production
    fi
    
    # Wait for service to stabilize
    aws ecs wait services-stable \
        --cluster "$CLUSTER_NAME" \
        --services "$service_name" \
        --region "$AWS_REGION" \
        --profile "$AWS_PROFILE" || {
        log_message "ERROR" "Service failed to stabilize within timeout period"
        return 1
    }
    
    log_message "INFO" "Service has stabilized: $service_name"
    return 0
}

# Function to verify the success of the rollback
verify_rollback() {
    local rollback_type=$1
    
    log_message "INFO" "Verifying rollback success for type: $rollback_type"
    
    case "$rollback_type" in
        service)
            # Verify service health
            for service in ${SERVICES//,/ }; do
                if [[ "$service" == "backend" ]]; then
                    # Check backend service health
                    log_message "INFO" "Checking backend service health"
                    local backend_status=$(aws ecs describe-services \
                        --cluster "$CLUSTER_NAME" \
                        --services "$BACKEND_SERVICE" \
                        --region "$AWS_REGION" \
                        --profile "$AWS_PROFILE" \
                        --query 'services[0].status' \
                        --output text)
                    
                    if [[ "$backend_status" != "ACTIVE" ]]; then
                        log_message "ERROR" "Backend service is not active: $backend_status"
                        return 1
                    fi
                    
                    # Check for running tasks
                    local backend_running_count=$(aws ecs describe-services \
                        --cluster "$CLUSTER_NAME" \
                        --services "$BACKEND_SERVICE" \
                        --region "$AWS_REGION" \
                        --profile "$AWS_PROFILE" \
                        --query 'services[0].runningCount' \
                        --output text)
                    
                    if [[ "$backend_running_count" -lt 1 ]]; then
                        log_message "ERROR" "Backend service has no running tasks"
                        return 1
                    fi
                    
                    log_message "INFO" "Backend service is healthy with $backend_running_count running tasks"
                fi
                
                if [[ "$service" == "frontend" ]]; then
                    # Check frontend service health
                    log_message "INFO" "Checking frontend service health"
                    local frontend_status=$(aws ecs describe-services \
                        --cluster "$CLUSTER_NAME" \
                        --services "$FRONTEND_SERVICE" \
                        --region "$AWS_REGION" \
                        --profile "$AWS_PROFILE" \
                        --query 'services[0].status' \
                        --output text)
                    
                    if [[ "$frontend_status" != "ACTIVE" ]]; then
                        log_message "ERROR" "Frontend service is not active: $frontend_status"
                        return 1
                    fi
                    
                    # Check for running tasks
                    local frontend_running_count=$(aws ecs describe-services \
                        --cluster "$CLUSTER_NAME" \
                        --services "$FRONTEND_SERVICE" \
                        --region "$AWS_REGION" \
                        --profile "$AWS_PROFILE" \
                        --query 'services[0].runningCount' \
                        --output text)
                    
                    if [[ "$frontend_running_count" -lt 1 ]]; then
                        log_message "ERROR" "Frontend service has no running tasks"
                        return 1
                    fi
                    
                    log_message "INFO" "Frontend service is healthy with $frontend_running_count running tasks"
                fi
            done
            ;;
            
        database)
            # Verify database connectivity and basic queries
            log_message "INFO" "Verifying database connectivity and integrity"
            
            check_postgres_connection || {
                log_message "ERROR" "Database connection check failed"
                return 1
            }
            
            # Try a simple query to verify database functionality
            PGPASSWORD="$DB_PASSWORD" psql \
                -h "$DB_HOST" \
                -p "$DB_PORT" \
                -U "$DB_USER" \
                -d "$DB_NAME" \
                -c "SELECT count(*) FROM information_schema.tables;" > /dev/null || {
                log_message "ERROR" "Failed to execute test query on database"
                return 1
            }
            
            log_message "INFO" "Database verification passed"
            ;;
            
        infrastructure)
            # Verify key infrastructure components
            log_message "INFO" "Verifying infrastructure state"
            
            # Check cluster existence
            aws ecs describe-clusters \
                --clusters "$CLUSTER_NAME" \
                --region "$AWS_REGION" \
                --profile "$AWS_PROFILE" \
                --query 'clusters[0].status' \
                --output text | grep -q "ACTIVE" || {
                log_message "ERROR" "ECS cluster is not active"
                return 1
            }
            
            # Check RDS instance status
            local db_identifier="loan-management-$ENVIRONMENT"
            aws rds describe-db-instances \
                --db-instance-identifier "$db_identifier" \
                --region "$AWS_REGION" \
                --profile "$AWS_PROFILE" \
                --query 'DBInstances[0].DBInstanceStatus' \
                --output text | grep -q "available" || {
                log_message "ERROR" "RDS instance is not available"
                return 1
            }
            
            log_message "INFO" "Infrastructure verification passed"
            ;;
            
        full)
            # Verify all components
            verify_rollback "service" || return 1
            verify_rollback "database" || return 1
            verify_rollback "infrastructure" || return 1
            ;;
            
        *)
            log_message "ERROR" "Unknown rollback type for verification: $rollback_type"
            return 1
            ;;
    esac
    
    log_message "INFO" "Rollback verification completed successfully"
    return 0
}

# Function to run basic smoke tests
run_smoke_tests() {
    log_message "INFO" "Running smoke tests"
    
    # Get endpoint information based on environment
    local backend_url=""
    local frontend_url=""
    
    case "$ENVIRONMENT" in
        development)
            backend_url="loan-management-dev-alb-1234567890.us-east-1.elb.amazonaws.com"
            frontend_url="dev.loan-management-system.example.com"
            ;;
        staging)
            backend_url="loan-management-staging-alb-1234567890.us-east-1.elb.amazonaws.com"
            frontend_url="staging.loan-management-system.example.com"
            ;;
        production)
            backend_url="loan-management-prod-alb-1234567890.us-east-1.elb.amazonaws.com"
            frontend_url="loan-management-system.example.com"
            ;;
    esac
    
    # Test backend health endpoint
    if [[ "$SERVICES" == *"backend"* || "$ROLLBACK_TYPE" == "full" ]]; then
        log_message "INFO" "Testing backend health endpoint"
        
        # Simple curl to backend health endpoint
        curl -s -f -o /dev/null "http://${backend_url}/api/health/" || {
            log_message "ERROR" "Backend health check failed"
            if [[ "$FORCE_ROLLBACK" != true ]]; then
                return 1
            fi
        }
        
        # Check API response for a simple endpoint
        local api_response=$(curl -s "http://${backend_url}/api/health/")
        if ! echo "$api_response" | grep -q "healthy"; then
            log_message "ERROR" "Backend API response check failed"
            if [[ "$FORCE_ROLLBACK" != true ]]; then
                return 1
            fi
        fi
        
        log_message "INFO" "Backend smoke test passed"
    fi
    
    # Test frontend accessibility
    if [[ "$SERVICES" == *"frontend"* || "$ROLLBACK_TYPE" == "full" ]]; then
        log_message "INFO" "Testing frontend accessibility"
        
        # Simple curl to frontend
        curl -s -f -o /dev/null "https://${frontend_url}/" || {
            log_message "ERROR" "Frontend accessibility check failed"
            if [[ "$FORCE_ROLLBACK" != true ]]; then
                return 1
            fi
        }
        
        log_message "INFO" "Frontend smoke test passed"
    fi
    
    log_message "INFO" "Smoke tests completed successfully"
    return 0
}

# Function to send notifications about rollback
notify_rollback() {
    local status=$1
    local details=$2
    
    log_message "INFO" "Sending rollback notification: $status"
    
    # Prepare notification message
    local message="Rollback in $ENVIRONMENT environment: $status"
    message+="\nRollback type: $ROLLBACK_TYPE"
    message+="\nServices: $SERVICES"
    message+="\nTimestamp: $(date)"
    message+="\nDetails: $details"
    
    # Send SNS notification if in staging or production
    if [[ "$ENVIRONMENT" == "staging" || "$ENVIRONMENT" == "production" ]]; then
        local sns_topic="arn:aws:sns:${AWS_REGION}:123456789012:loan-management-${ENVIRONMENT}-alerts"
        
        aws sns publish \
            --topic-arn "$sns_topic" \
            --subject "Rollback Notification - $ENVIRONMENT - $status" \
            --message "$message" \
            --region "$AWS_REGION" \
            --profile "$AWS_PROFILE" > /dev/null || {
            log_message "WARNING" "Failed to send SNS notification"
        }
    fi
    
    # For all environments, you could also send to Slack or another system
    # This is a placeholder for that integration
    
    log_message "INFO" "Rollback notification sent"
}

# Function to perform cleanup after rollback
cleanup() {
    # Remove any temporary files or artifacts
    log_message "INFO" "Performing cleanup"
    
    # If there are any temporary directories created during rollback, remove them
    if [[ -d "/tmp/rollback-${ENVIRONMENT}-$$" ]]; then
        rm -rf "/tmp/rollback-${ENVIRONMENT}-$$"
    fi
    
    # If temp files were created for backups, clean them up
    find /tmp -name "loan-management-*-backup-*" -mtime +1 -type f -delete 2>/dev/null || true
    
    log_message "INFO" "Cleanup completed"
}

# Main function
main() {
    local exit_code=0
    
    # Parse command line arguments
    parse_arguments "$@"
    exit_code=$?
    if [[ $exit_code -ne 0 ]]; then
        return $exit_code
    fi
    
    # Source the deploy script to use its functions
    source "$SCRIPT_DIR/deploy.sh" || {
        echo "ERROR: Failed to source deploy.sh"
        return 1
    }
    
    # Set environment-specific variables
    set_environment_variables
    exit_code=$?
    if [[ $exit_code -ne 0 ]]; then
        return $exit_code
    }
    
    # Set service names based on environment
    set_service_names
    
    # Create log file
    touch "$LOG_FILE" 2>/dev/null || {
        echo "WARNING: Could not create log file at $LOG_FILE. Logging to stdout only."
    }
    
    log_message "INFO" "Starting rollback process for $ENVIRONMENT environment (type: $ROLLBACK_TYPE)"
    
    # Confirm rollback
    confirm_rollback
    exit_code=$?
    if [[ $exit_code -ne 0 ]]; then
        return $exit_code
    }
    
    # Perform rollback based on type
    case "$ROLLBACK_TYPE" in
        service)
            # Roll back each specified service
            for service in ${SERVICES//,/ }; do
                if [[ "$service" == "backend" ]]; then
                    rollback_service "$BACKEND_SERVICE" || exit_code=1
                elif [[ "$service" == "frontend" ]]; then
                    rollback_service "$FRONTEND_SERVICE" || exit_code=1
                else
                    log_message "WARNING" "Unknown service: $service"
                fi
            done
            ;;
            
        database)
            # Roll back database
            rollback_database || exit_code=1
            ;;
            
        infrastructure)
            # Roll back infrastructure
            rollback_infrastructure || exit_code=1
            ;;
            
        full)
            # Perform full rollback in the correct order
            log_message "INFO" "Performing full rollback"
            
            # 1. First roll back services to minimize impact while other components are rolling back
            for service in ${SERVICES//,/ }; do
                if [[ "$service" == "backend" ]]; then
                    rollback_service "$BACKEND_SERVICE" || exit_code=1
                elif [[ "$service" == "frontend" ]]; then
                    rollback_service "$FRONTEND_SERVICE" || exit_code=1
                fi
            done
            
            # 2. Roll back database
            if [[ $exit_code -eq 0 || "$FORCE_ROLLBACK" = true ]]; then
                rollback_database || exit_code=1
            fi
            
            # 3. Roll back infrastructure
            if [[ $exit_code -eq 0 || "$FORCE_ROLLBACK" = true ]]; then
                rollback_infrastructure || exit_code=1
            fi
            ;;
            
        *)
            log_message "ERROR" "Unknown rollback type: $ROLLBACK_TYPE"
            exit_code=1
            ;;
    esac
    
    # Verify rollback success
    if [[ $exit_code -eq 0 || "$FORCE_ROLLBACK" = true ]]; then
        verify_rollback "$ROLLBACK_TYPE" || {
            if [[ "$FORCE_ROLLBACK" != true ]]; then
                exit_code=1
            fi
        }
    fi
    
    # Run smoke tests
    if [[ $exit_code -eq 0 || "$FORCE_ROLLBACK" = true ]]; then
        run_smoke_tests || {
            if [[ "$FORCE_ROLLBACK" != true ]]; then
                exit_code=1
            fi
        }
    fi
    
    # Send notification about rollback status
    if [[ $exit_code -eq 0 ]]; then
        notify_rollback "SUCCESS" "Rollback completed successfully"
    else
        notify_rollback "FAILURE" "Rollback failed with errors. Check logs for details."
    fi
    
    # Perform cleanup
    cleanup
    
    if [[ $exit_code -eq 0 ]]; then
        log_message "INFO" "Rollback process completed successfully"
    else
        log_message "ERROR" "Rollback process failed with errors"
    fi
    
    return $exit_code
}

# Execute main function if script is being run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
    exit $?
fi