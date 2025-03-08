#!/bin/bash
#
# deploy.sh - Deployment script for the loan management system
#
# This script handles infrastructure provisioning, container deployment,
# database initialization, and post-deployment validation for different environments.
#
# Version: 1.0
# Requires: aws-cli 2.0+, terraform 1.0+, docker 20.0+, jq 1.6+, bash 4.0+

# Exit on error, enable pipefail
set -e
set -o pipefail

# Default values for global variables
ENVIRONMENT=""
AWS_REGION=${AWS_REGION:-"us-east-1"}
AWS_PROFILE=${AWS_PROFILE:-"default"}
TERRAFORM_DIR=${TERRAFORM_DIR:-"../terraform"}
BACKEND_DIR=${BACKEND_DIR:-"../../backend"}
FRONTEND_DIR=${FRONTEND_DIR:-"../../frontend"}
DOCKER_REGISTRY=""
BACKEND_IMAGE=${BACKEND_IMAGE:-"loan-management-backend"}
FRONTEND_IMAGE=${FRONTEND_IMAGE:-"loan-management-frontend"}
TAG=${TAG:-"latest"}
DB_HOST=""
DB_NAME=${DB_NAME:-"loan_management"}
DB_USER=${DB_USER:-"postgres"}
DB_PASSWORD=${DB_PASSWORD:-"postgres"}

# Script location and logging
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
LOG_FILE="${SCRIPT_DIR}/deploy-$(date +%Y%m%d-%H%M%S).log"

# Deployment flags
DEPLOY_INFRASTRUCTURE=true
DEPLOY_BACKEND=true
DEPLOY_FRONTEND=true
INITIALIZE_DATABASE=true
SKIP_CONFIRMATION=false
BLUE_GREEN_DEPLOYMENT=false
CANARY_PERCENTAGE=10
CANARY_DURATION=15

# ANSI color codes for terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to display usage information
print_usage() {
    echo -e "${BLUE}Loan Management System Deployment Script${NC}"
    echo
    echo "This script handles infrastructure provisioning, container deployment,"
    echo "database initialization, and post-deployment validation for different environments."
    echo
    echo -e "${YELLOW}Usage:${NC}"
    echo "  $0 [options]"
    echo
    echo -e "${YELLOW}Options:${NC}"
    echo "  -h, --help                     Display this help message and exit"
    echo "  -e, --environment ENV          Target environment (development, staging, production) (required)"
    echo "  -r, --region REGION            AWS region (default: $AWS_REGION)"
    echo "  -p, --profile PROFILE          AWS CLI profile to use (default: $AWS_PROFILE)"
    echo "  --skip-infrastructure          Skip infrastructure deployment"
    echo "  --skip-backend                 Skip backend deployment"
    echo "  --skip-frontend                Skip frontend deployment"
    echo "  --skip-database                Skip database initialization"
    echo "  --skip-confirmation            Skip confirmation prompts"
    echo "  --tag TAG                      Container image tag (default: $TAG)"
    echo "  --blue-green                   Use blue/green deployment (default for staging/production)"
    echo "  --canary-percentage PCT        Initial traffic percentage for canary deployment (default: $CANARY_PERCENTAGE)"
    echo "  --canary-duration MIN          Duration in minutes for canary deployment (default: $CANARY_DURATION)"
    echo
    echo -e "${YELLOW}Examples:${NC}"
    echo "  # Deploy everything to development environment"
    echo "  $0 -e development"
    echo
    echo "  # Deploy only backend and frontend to staging with blue/green deployment"
    echo "  $0 -e staging --skip-infrastructure --skip-database --blue-green"
    echo
    echo "  # Deploy to production with specific tag and AWS profile"
    echo "  $0 -e production --tag v1.0.0 -p production-profile --skip-confirmation"
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
            --skip-infrastructure)
                DEPLOY_INFRASTRUCTURE=false
                shift
                ;;
            --skip-backend)
                DEPLOY_BACKEND=false
                shift
                ;;
            --skip-frontend)
                DEPLOY_FRONTEND=false
                shift
                ;;
            --skip-database)
                INITIALIZE_DATABASE=false
                shift
                ;;
            --skip-confirmation)
                SKIP_CONFIRMATION=true
                shift
                ;;
            --tag)
                TAG="$2"
                shift 2
                ;;
            --blue-green)
                BLUE_GREEN_DEPLOYMENT=true
                shift
                ;;
            --canary-percentage)
                CANARY_PERCENTAGE="$2"
                shift 2
                ;;
            --canary-duration)
                CANARY_DURATION="$2"
                shift 2
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

    # Set default blue/green deployment based on environment
    if [[ "$ENVIRONMENT" == "staging" || "$ENVIRONMENT" == "production" ]]; then
        BLUE_GREEN_DEPLOYMENT=true
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
    if [[ ! -f "$LOG_FILE" ]]; then
        touch "$LOG_FILE" 2>/dev/null || {
            echo "Warning: Could not create log file at $LOG_FILE. Logging to stdout only."
        }
    fi
    
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
    if [[ -f "$LOG_FILE" ]] && [[ -w "$LOG_FILE" ]]; then
        echo "$log_entry" >> "$LOG_FILE"
    fi
}

# Function to set environment-specific variables
set_environment_variables() {
    log_message "INFO" "Setting environment-specific variables for $ENVIRONMENT"
    
    case "$ENVIRONMENT" in
        development)
            export TF_WORKSPACE="development"
            export TF_VAR_environment="development"
            export DOCKER_REGISTRY="123456789012.dkr.ecr.$AWS_REGION.amazonaws.com"
            export DB_HOST="loan-management-dev.cluster-xyz.us-east-1.rds.amazonaws.com"
            ;;
        staging)
            export TF_WORKSPACE="staging"
            export TF_VAR_environment="staging"
            export DOCKER_REGISTRY="123456789012.dkr.ecr.$AWS_REGION.amazonaws.com"
            export DB_HOST="loan-management-staging.cluster-xyz.us-east-1.rds.amazonaws.com"
            ;;
        production)
            export TF_WORKSPACE="production"
            export TF_VAR_environment="production"
            export DOCKER_REGISTRY="123456789012.dkr.ecr.$AWS_REGION.amazonaws.com"
            export DB_HOST="loan-management-prod.cluster-xyz.us-east-1.rds.amazonaws.com"
            ;;
        *)
            log_message "ERROR" "Unknown environment: $ENVIRONMENT"
            return 1
            ;;
    esac
    
    # Export AWS-related variables
    export AWS_DEFAULT_REGION="$AWS_REGION"
    export AWS_PROFILE="$AWS_PROFILE"
    
    # Export Docker image names with registry
    export BACKEND_IMAGE_TAG="$DOCKER_REGISTRY/$BACKEND_IMAGE:$TAG"
    export FRONTEND_IMAGE_TAG="$DOCKER_REGISTRY/$FRONTEND_IMAGE:$TAG"
    
    log_message "INFO" "Environment variables set successfully"
    return 0
}

# Function to check prerequisites
check_prerequisites() {
    log_message "INFO" "Checking prerequisites..."
    
    local missing_deps=0
    
    # Check for AWS CLI
    if ! command -v aws &> /dev/null; then
        log_message "ERROR" "AWS CLI not found. Please install aws-cli package."
        missing_deps=$((missing_deps + 1))
    else
        local aws_version=$(aws --version | awk '{print $1}' | cut -d/ -f2)
        log_message "INFO" "Found AWS CLI version: $aws_version"
    fi
    
    # Check for Terraform
    if ! command -v terraform &> /dev/null; then
        log_message "ERROR" "Terraform not found. Please install terraform package."
        missing_deps=$((missing_deps + 1))
    else
        local tf_version=$(terraform version | head -n 1 | cut -d' ' -f2)
        log_message "INFO" "Found Terraform version: $tf_version"
    fi
    
    # Check for Docker
    if ! command -v docker &> /dev/null; then
        log_message "ERROR" "Docker not found. Please install docker package."
        missing_deps=$((missing_deps + 1))
    else
        local docker_version=$(docker --version | cut -d' ' -f3 | tr -d ',')
        log_message "INFO" "Found Docker version: $docker_version"
    fi
    
    # Check for jq
    if ! command -v jq &> /dev/null; then
        log_message "ERROR" "jq not found. Please install jq package."
        missing_deps=$((missing_deps + 1))
    else
        local jq_version=$(jq --version | cut -d- -f2)
        log_message "INFO" "Found jq version: $jq_version"
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity --profile "$AWS_PROFILE" &> /dev/null; then
        log_message "ERROR" "AWS credentials for profile $AWS_PROFILE are invalid or not configured."
        missing_deps=$((missing_deps + 1))
    else
        local aws_account=$(aws sts get-caller-identity --profile "$AWS_PROFILE" --query 'Account' --output text)
        log_message "INFO" "Using AWS account: $aws_account"
    fi
    
    if [[ $missing_deps -gt 0 ]]; then
        log_message "ERROR" "$missing_deps required dependencies are missing."
        return 1
    fi
    
    log_message "INFO" "All prerequisites are met."
    return 0
}

# Function to confirm deployment
confirm_deployment() {
    if [[ "$SKIP_CONFIRMATION" = true ]]; then
        return 0
    fi
    
    echo ""
    echo -e "${YELLOW}You are about to deploy to $ENVIRONMENT environment${NC}"
    echo ""
    echo "Deployment details:"
    echo "  Infrastructure: $(if [[ "$DEPLOY_INFRASTRUCTURE" = true ]]; then echo "Yes"; else echo "No"; fi)"
    echo "  Backend: $(if [[ "$DEPLOY_BACKEND" = true ]]; then echo "Yes"; else echo "No"; fi)"
    echo "  Frontend: $(if [[ "$DEPLOY_FRONTEND" = true ]]; then echo "Yes"; else echo "No"; fi)"
    echo "  Database: $(if [[ "$INITIALIZE_DATABASE" = true ]]; then echo "Yes"; else echo "No"; fi)"
    echo "  Image tag: $TAG"
    echo "  Deployment type: $(if [[ "$BLUE_GREEN_DEPLOYMENT" = true ]]; then echo "Blue/Green"; else echo "In-place"; fi)"
    echo ""
    
    read -p "Do you want to continue? (y/n): " -n 1 -r
    echo ""
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_message "INFO" "Deployment canceled by user"
        return 1
    fi
    
    return 0
}

# Function to deploy infrastructure using Terraform
deploy_infrastructure() {
    if [[ "$DEPLOY_INFRASTRUCTURE" != true ]]; then
        log_message "INFO" "Skipping infrastructure deployment"
        return 0
    fi
    
    log_message "INFO" "Deploying infrastructure using Terraform"
    
    # Change to Terraform directory
    cd "$TERRAFORM_DIR" || {
        log_message "ERROR" "Failed to change to Terraform directory: $TERRAFORM_DIR"
        return 1
    }
    
    # Initialize Terraform
    log_message "INFO" "Initializing Terraform"
    if ! terraform init; then
        log_message "ERROR" "Failed to initialize Terraform"
        return 1
    fi
    
    # Select workspace
    log_message "INFO" "Selecting Terraform workspace: $TF_WORKSPACE"
    if ! terraform workspace select "$TF_WORKSPACE" 2>/dev/null; then
        log_message "INFO" "Workspace doesn't exist, creating it"
        if ! terraform workspace new "$TF_WORKSPACE"; then
            log_message "ERROR" "Failed to create Terraform workspace: $TF_WORKSPACE"
            return 1
        fi
    fi
    
    # Apply Terraform configuration
    log_message "INFO" "Applying Terraform configuration"
    if [[ "$SKIP_CONFIRMATION" = true ]]; then
        if ! terraform apply -auto-approve; then
            log_message "ERROR" "Failed to apply Terraform configuration"
            return 1
        fi
    else
        if ! terraform apply; then
            log_message "ERROR" "Failed to apply Terraform configuration"
            return 1
        fi
    fi
    
    # Get outputs and store them for later use
    log_message "INFO" "Getting Terraform outputs"
    export TF_OUTPUT_JSON=$(terraform output -json)
    
    # Extract specific outputs we need
    export DB_HOST=$(echo "$TF_OUTPUT_JSON" | jq -r '.database_endpoint.value')
    export CLUSTER_NAME=$(echo "$TF_OUTPUT_JSON" | jq -r '.ecs_cluster_name.value')
    export BACKEND_SERVICE_NAME=$(echo "$TF_OUTPUT_JSON" | jq -r '.backend_service_name.value')
    export FRONTEND_SERVICE_NAME=$(echo "$TF_OUTPUT_JSON" | jq -r '.frontend_service_name.value')
    export CLOUDFRONT_DISTRIBUTION_ID=$(echo "$TF_OUTPUT_JSON" | jq -r '.cloudfront_distribution_id.value')
    
    log_message "INFO" "Infrastructure deployment completed"
    return 0
}

# Function to build and push Docker images
build_and_push_images() {
    log_message "INFO" "Building and pushing Docker images"
    
    # Login to ECR
    log_message "INFO" "Logging in to ECR"
    aws ecr get-login-password --region "$AWS_REGION" --profile "$AWS_PROFILE" | docker login --username AWS --password-stdin "$DOCKER_REGISTRY" || {
        log_message "ERROR" "Failed to log in to ECR"
        return 1
    }
    
    # Build and push backend image
    if [[ "$DEPLOY_BACKEND" = true ]]; then
        log_message "INFO" "Building backend image"
        cd "$BACKEND_DIR" || {
            log_message "ERROR" "Failed to change to backend directory: $BACKEND_DIR"
            return 1
        }
        
        docker build -t "$BACKEND_IMAGE" --build-arg ENVIRONMENT="$ENVIRONMENT" . || {
            log_message "ERROR" "Failed to build backend image"
            return 1
        }
        
        log_message "INFO" "Tagging backend image as $BACKEND_IMAGE_TAG"
        docker tag "$BACKEND_IMAGE" "$BACKEND_IMAGE_TAG" || {
            log_message "ERROR" "Failed to tag backend image"
            return 1
        }
        
        log_message "INFO" "Pushing backend image to ECR"
        docker push "$BACKEND_IMAGE_TAG" || {
            log_message "ERROR" "Failed to push backend image"
            return 1
        }
        
        log_message "INFO" "Backend image pushed successfully"
    else
        log_message "INFO" "Skipping backend image build and push"
    fi
    
    # Build and push frontend image
    if [[ "$DEPLOY_FRONTEND" = true ]]; then
        log_message "INFO" "Building frontend image"
        cd "$FRONTEND_DIR" || {
            log_message "ERROR" "Failed to change to frontend directory: $FRONTEND_DIR"
            return 1
        }
        
        docker build -t "$FRONTEND_IMAGE" --build-arg ENVIRONMENT="$ENVIRONMENT" . || {
            log_message "ERROR" "Failed to build frontend image"
            return 1
        }
        
        log_message "INFO" "Tagging frontend image as $FRONTEND_IMAGE_TAG"
        docker tag "$FRONTEND_IMAGE" "$FRONTEND_IMAGE_TAG" || {
            log_message "ERROR" "Failed to tag frontend image"
            return 1
        }
        
        log_message "INFO" "Pushing frontend image to ECR"
        docker push "$FRONTEND_IMAGE_TAG" || {
            log_message "ERROR" "Failed to push frontend image"
            return 1
        }
        
        log_message "INFO" "Frontend image pushed successfully"
    else
        log_message "INFO" "Skipping frontend image build and push"
    fi
    
    # Return to script directory
    cd "$SCRIPT_DIR"
    
    log_message "INFO" "Image build and push completed"
    return 0
}

# Function to update ECS task definitions
update_task_definitions() {
    log_message "INFO" "Updating ECS task definitions"
    
    # Return if neither backend nor frontend is being deployed
    if [[ "$DEPLOY_BACKEND" != true ]] && [[ "$DEPLOY_FRONTEND" != true ]]; then
        log_message "INFO" "Skipping task definition updates"
        return 0
    fi
    
    # Update backend task definition
    if [[ "$DEPLOY_BACKEND" = true ]]; then
        log_message "INFO" "Updating backend task definition"
        
        # Get current task definition
        local backend_task_def_arn=$(aws ecs describe-services \
            --cluster "$CLUSTER_NAME" \
            --services "$BACKEND_SERVICE_NAME" \
            --region "$AWS_REGION" \
            --profile "$AWS_PROFILE" \
            --query 'services[0].taskDefinition' \
            --output text)
        
        # Get current task definition JSON
        local backend_task_def=$(aws ecs describe-task-definition \
            --task-definition "$backend_task_def_arn" \
            --region "$AWS_REGION" \
            --profile "$AWS_PROFILE")
        
        # Create new task definition with updated image
        local new_backend_task_def=$(echo "$backend_task_def" | \
            jq --arg IMAGE "$BACKEND_IMAGE_TAG" \
            '.taskDefinition | .containerDefinitions[0].image = $IMAGE | {containerDefinitions: .containerDefinitions, family: .family, taskRoleArn: .taskRoleArn, executionRoleArn: .executionRoleArn, networkMode: .networkMode, volumes: .volumes, placementConstraints: .placementConstraints, requiresCompatibilities: .requiresCompatibilities, cpu: .cpu, memory: .memory}')
        
        # Register new task definition
        local new_backend_task_def_arn=$(aws ecs register-task-definition \
            --region "$AWS_REGION" \
            --profile "$AWS_PROFILE" \
            --cli-input-json "$new_backend_task_def" \
            --query 'taskDefinition.taskDefinitionArn' \
            --output text)
        
        export BACKEND_TASK_DEFINITION_ARN="$new_backend_task_def_arn"
        log_message "INFO" "Backend task definition updated: $BACKEND_TASK_DEFINITION_ARN"
    fi
    
    # Update frontend task definition
    if [[ "$DEPLOY_FRONTEND" = true ]]; then
        log_message "INFO" "Updating frontend task definition"
        
        # Get current task definition
        local frontend_task_def_arn=$(aws ecs describe-services \
            --cluster "$CLUSTER_NAME" \
            --services "$FRONTEND_SERVICE_NAME" \
            --region "$AWS_REGION" \
            --profile "$AWS_PROFILE" \
            --query 'services[0].taskDefinition' \
            --output text)
        
        # Get current task definition JSON
        local frontend_task_def=$(aws ecs describe-task-definition \
            --task-definition "$frontend_task_def_arn" \
            --region "$AWS_REGION" \
            --profile "$AWS_PROFILE")
        
        # Create new task definition with updated image
        local new_frontend_task_def=$(echo "$frontend_task_def" | \
            jq --arg IMAGE "$FRONTEND_IMAGE_TAG" \
            '.taskDefinition | .containerDefinitions[0].image = $IMAGE | {containerDefinitions: .containerDefinitions, family: .family, taskRoleArn: .taskRoleArn, executionRoleArn: .executionRoleArn, networkMode: .networkMode, volumes: .volumes, placementConstraints: .placementConstraints, requiresCompatibilities: .requiresCompatibilities, cpu: .cpu, memory: .memory}')
        
        # Register new task definition
        local new_frontend_task_def_arn=$(aws ecs register-task-definition \
            --region "$AWS_REGION" \
            --profile "$AWS_PROFILE" \
            --cli-input-json "$new_frontend_task_def" \
            --query 'taskDefinition.taskDefinitionArn' \
            --output text)
        
        export FRONTEND_TASK_DEFINITION_ARN="$new_frontend_task_def_arn"
        log_message "INFO" "Frontend task definition updated: $FRONTEND_TASK_DEFINITION_ARN"
    fi
    
    log_message "INFO" "Task definition updates completed"
    return 0
}

# Function to deploy services
deploy_services() {
    log_message "INFO" "Deploying services"
    
    # Return if neither backend nor frontend is being deployed
    if [[ "$DEPLOY_BACKEND" != true ]] && [[ "$DEPLOY_FRONTEND" != true ]]; then
        log_message "INFO" "Skipping service deployment"
        return 0
    fi
    
    # Get deployment IDs for tracking
    local backend_deployment_id=""
    local frontend_deployment_id=""
    
    # Deploy using blue/green deployment if enabled
    if [[ "$BLUE_GREEN_DEPLOYMENT" = true ]]; then
        log_message "INFO" "Using blue/green deployment"
        
        # For backend service
        if [[ "$DEPLOY_BACKEND" = true ]]; then
            log_message "INFO" "Creating CodeDeploy deployment for backend service"
            
            # Get CodeDeploy application and deployment group
            local backend_codedeploy_app="${BACKEND_SERVICE_NAME}-app"
            local backend_deployment_group="${BACKEND_SERVICE_NAME}-deployment-group"
            
            # Create deployment
            local backend_deployment=$(aws deploy create-deployment \
                --region "$AWS_REGION" \
                --profile "$AWS_PROFILE" \
                --application-name "$backend_codedeploy_app" \
                --deployment-group-name "$backend_deployment_group" \
                --revision "revisionType=AppSpecContent,appSpecContent={content='{\"version\":1,\"Resources\":[{\"TargetService\":{\"Type\":\"AWS::ECS::Service\",\"Properties\":{\"TaskDefinition\":\"$BACKEND_TASK_DEFINITION_ARN\",\"LoadBalancerInfo\":{\"ContainerName\":\"backend\",\"ContainerPort\":8000}}}}]}',}" \
                --deployment-config-name "CodeDeployDefault.ECSCanary$(echo "$CANARY_PERCENTAGE" | tr -d "0")" \
                --description "Deploying version $TAG to $ENVIRONMENT environment")
            
            backend_deployment_id=$(echo "$backend_deployment" | jq -r '.deploymentId')
            log_message "INFO" "Backend deployment created: $backend_deployment_id"
        fi
        
        # For frontend service
        if [[ "$DEPLOY_FRONTEND" = true ]]; then
            log_message "INFO" "Creating CodeDeploy deployment for frontend service"
            
            # Get CodeDeploy application and deployment group
            local frontend_codedeploy_app="${FRONTEND_SERVICE_NAME}-app"
            local frontend_deployment_group="${FRONTEND_SERVICE_NAME}-deployment-group"
            
            # Create deployment
            local frontend_deployment=$(aws deploy create-deployment \
                --region "$AWS_REGION" \
                --profile "$AWS_PROFILE" \
                --application-name "$frontend_codedeploy_app" \
                --deployment-group-name "$frontend_deployment_group" \
                --revision "revisionType=AppSpecContent,appSpecContent={content='{\"version\":1,\"Resources\":[{\"TargetService\":{\"Type\":\"AWS::ECS::Service\",\"Properties\":{\"TaskDefinition\":\"$FRONTEND_TASK_DEFINITION_ARN\",\"LoadBalancerInfo\":{\"ContainerName\":\"frontend\",\"ContainerPort\":80}}}}]}',}" \
                --deployment-config-name "CodeDeployDefault.ECSCanary$(echo "$CANARY_PERCENTAGE" | tr -d "0")" \
                --description "Deploying version $TAG to $ENVIRONMENT environment")
            
            frontend_deployment_id=$(echo "$frontend_deployment" | jq -r '.deploymentId')
            log_message "INFO" "Frontend deployment created: $frontend_deployment_id"
        fi
        
        # Wait for deployments to complete
        if [[ -n "$backend_deployment_id" ]]; then
            log_message "INFO" "Waiting for backend deployment to complete..."
            aws deploy wait deployment-successful \
                --region "$AWS_REGION" \
                --profile "$AWS_PROFILE" \
                --deployment-id "$backend_deployment_id" || {
                log_message "ERROR" "Backend deployment failed"
                return 1
            }
            log_message "INFO" "Backend deployment completed successfully"
        fi
        
        if [[ -n "$frontend_deployment_id" ]]; then
            log_message "INFO" "Waiting for frontend deployment to complete..."
            aws deploy wait deployment-successful \
                --region "$AWS_REGION" \
                --profile "$AWS_PROFILE" \
                --deployment-id "$frontend_deployment_id" || {
                log_message "ERROR" "Frontend deployment failed"
                return 1
            }
            log_message "INFO" "Frontend deployment completed successfully"
        fi
    else
        # Use direct ECS service update (in-place deployment)
        log_message "INFO" "Using in-place ECS deployment"
        
        # Update backend service
        if [[ "$DEPLOY_BACKEND" = true ]]; then
            log_message "INFO" "Updating backend ECS service"
            aws ecs update-service \
                --cluster "$CLUSTER_NAME" \
                --service "$BACKEND_SERVICE_NAME" \
                --task-definition "$BACKEND_TASK_DEFINITION_ARN" \
                --region "$AWS_REGION" \
                --profile "$AWS_PROFILE" > /dev/null || {
                log_message "ERROR" "Failed to update backend service"
                return 1
            }
            log_message "INFO" "Backend service update initiated"
        fi
        
        # Update frontend service
        if [[ "$DEPLOY_FRONTEND" = true ]]; then
            log_message "INFO" "Updating frontend ECS service"
            aws ecs update-service \
                --cluster "$CLUSTER_NAME" \
                --service "$FRONTEND_SERVICE_NAME" \
                --task-definition "$FRONTEND_TASK_DEFINITION_ARN" \
                --region "$AWS_REGION" \
                --profile "$AWS_PROFILE" > /dev/null || {
                log_message "ERROR" "Failed to update frontend service"
                return 1
            }
            log_message "INFO" "Frontend service update initiated"
        fi
        
        # Wait for services to stabilize
        if [[ "$DEPLOY_BACKEND" = true ]]; then
            log_message "INFO" "Waiting for backend service to stabilize..."
            aws ecs wait services-stable \
                --cluster "$CLUSTER_NAME" \
                --services "$BACKEND_SERVICE_NAME" \
                --region "$AWS_REGION" \
                --profile "$AWS_PROFILE" || {
                log_message "ERROR" "Backend service failed to stabilize"
                return 1
            }
            log_message "INFO" "Backend service stable"
        fi
        
        if [[ "$DEPLOY_FRONTEND" = true ]]; then
            log_message "INFO" "Waiting for frontend service to stabilize..."
            aws ecs wait services-stable \
                --cluster "$CLUSTER_NAME" \
                --services "$FRONTEND_SERVICE_NAME" \
                --region "$AWS_REGION" \
                --profile "$AWS_PROFILE" || {
                log_message "ERROR" "Frontend service failed to stabilize"
                return 1
            }
            log_message "INFO" "Frontend service stable"
        fi
    fi
    
    log_message "INFO" "Service deployment completed"
    return 0
}

# Function to initialize database
initialize_database() {
    if [[ "$INITIALIZE_DATABASE" != true ]]; then
        log_message "INFO" "Skipping database initialization"
        return 0
    fi
    
    log_message "INFO" "Initializing database"
    
    # Source the database initialization script to use its functions
    source "$SCRIPT_DIR/init-db.sh" || {
        log_message "ERROR" "Failed to source init-db.sh"
        return 1
    }
    
    # Check database connection
    log_message "INFO" "Checking database connection"
    if ! check_postgres_connection; then
        log_message "ERROR" "Database connection check failed"
        return 1
    fi
    
    # Create database backup before making changes
    log_message "INFO" "Creating database backup before initialization"
    if [[ -f "$SCRIPT_DIR/backup-db.sh" ]]; then
        bash "$SCRIPT_DIR/backup-db.sh" -t full -n "$DB_NAME" -u "$DB_USER" -p "$DB_PASSWORD" -H "$DB_HOST" -e "$ENVIRONMENT" || {
            log_message "WARNING" "Database backup failed, but continuing with initialization"
        }
    else
        log_message "WARNING" "backup-db.sh not found, skipping backup"
    fi
    
    # Apply database migrations
    log_message "INFO" "Applying database migrations"
    export DJANGO_SETTINGS_MODULE="config.settings.$ENVIRONMENT"
    cd "$SCRIPT_DIR/../../" || {
        log_message "ERROR" "Failed to change to project root directory"
        return 1
    }
    
    python manage.py migrate --noinput || {
        log_message "ERROR" "Database migration failed"
        return 1
    }
    
    # Load initial data if this is a fresh installation
    if [[ "$ENVIRONMENT" == "development" ]] || [[ "$ENVIRONMENT" == "staging" ]]; then
        log_message "INFO" "Loading initial reference data"
        python manage.py loaddata roles_permissions document_templates notification_templates || {
            log_message "WARNING" "Failed to load some fixtures, but continuing deployment"
        }
    fi
    
    log_message "INFO" "Database initialization completed"
    return 0
}

# Function to invalidate CloudFront cache
invalidate_cache() {
    if [[ "$DEPLOY_FRONTEND" != true ]] || [[ -z "$CLOUDFRONT_DISTRIBUTION_ID" ]]; then
        log_message "INFO" "Skipping CloudFront cache invalidation"
        return 0
    fi
    
    log_message "INFO" "Invalidating CloudFront cache"
    
    # Create invalidation
    local invalidation_id=$(aws cloudfront create-invalidation \
        --distribution-id "$CLOUDFRONT_DISTRIBUTION_ID" \
        --paths "/*" \
        --region "$AWS_REGION" \
        --profile "$AWS_PROFILE" \
        --query 'Invalidation.Id' \
        --output text)
    
    log_message "INFO" "Cache invalidation created: $invalidation_id"
    
    # Wait for invalidation to complete
    log_message "INFO" "Waiting for cache invalidation to complete..."
    aws cloudfront wait invalidation-completed \
        --distribution-id "$CLOUDFRONT_DISTRIBUTION_ID" \
        --id "$invalidation_id" \
        --region "$AWS_REGION" \
        --profile "$AWS_PROFILE" || {
        log_message "WARNING" "Failed to wait for cache invalidation, but deployment can continue"
    }
    
    log_message "INFO" "Cache invalidation completed"
    return 0
}

# Function to run smoke tests
run_smoke_tests() {
    log_message "INFO" "Running smoke tests"
    
    # Get ALB DNS name for backend and frontend
    local backend_url=""
    local frontend_url=""
    
    if [[ "$DEPLOY_BACKEND" = true ]]; then
        backend_url=$(echo "$TF_OUTPUT_JSON" | jq -r '.backend_load_balancer_dns.value')
        
        if [[ -n "$backend_url" ]]; then
            log_message "INFO" "Testing backend health endpoint"
            if curl -s -f -o /dev/null "http://${backend_url}/api/health/"; then
                log_message "INFO" "Backend health check passed"
            else
                log_message "ERROR" "Backend health check failed"
                return 1
            fi
        fi
    fi
    
    if [[ "$DEPLOY_FRONTEND" = true ]]; then
        frontend_url=$(echo "$TF_OUTPUT_JSON" | jq -r '.frontend_url.value')
        
        if [[ -n "$frontend_url" ]]; then
            log_message "INFO" "Testing frontend accessibility"
            if curl -s -f -o /dev/null "https://${frontend_url}/"; then
                log_message "INFO" "Frontend accessibility check passed"
            else
                log_message "ERROR" "Frontend accessibility check failed"
                return 1
            fi
        fi
    fi
    
    log_message "INFO" "Smoke tests completed successfully"
    return 0
}

# Function to clean up after deployment
cleanup() {
    log_message "INFO" "Performing cleanup"
    
    # Remove any temporary files
    if [[ -d "/tmp/deploy-${ENVIRONMENT}-$$" ]]; then
        rm -rf "/tmp/deploy-${ENVIRONMENT}-$$"
    fi
    
    # Prune old Docker images if we built new ones
    if [[ "$DEPLOY_BACKEND" = true ]] || [[ "$DEPLOY_FRONTEND" = true ]]; then
        log_message "INFO" "Pruning Docker images"
        docker image prune -f
    fi
    
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
    
    # Set environment-specific variables
    set_environment_variables
    exit_code=$?
    if [[ $exit_code -ne 0 ]]; then
        return $exit_code
    fi
    
    # Check prerequisites
    check_prerequisites
    exit_code=$?
    if [[ $exit_code -ne 0 ]]; then
        return $exit_code
    fi
    
    # Create log file
    touch "$LOG_FILE" 2>/dev/null || {
        echo "Warning: Could not create log file at $LOG_FILE. Logging to stdout only."
    }
    
    log_message "INFO" "Starting deployment to $ENVIRONMENT environment"
    
    # Confirm deployment
    confirm_deployment
    exit_code=$?
    if [[ $exit_code -ne 0 ]]; then
        return $exit_code
    fi
    
    # Deploy infrastructure
    if [[ "$DEPLOY_INFRASTRUCTURE" = true ]]; then
        deploy_infrastructure
        exit_code=$?
        if [[ $exit_code -ne 0 ]]; then
            log_message "ERROR" "Infrastructure deployment failed"
            return $exit_code
        fi
    fi
    
    # Build and push Docker images
    build_and_push_images
    exit_code=$?
    if [[ $exit_code -ne 0 ]]; then
        log_message "ERROR" "Image build and push failed"
        return $exit_code
    fi
    
    # Update task definitions
    update_task_definitions
    exit_code=$?
    if [[ $exit_code -ne 0 ]]; then
        log_message "ERROR" "Task definition update failed"
        return $exit_code
    fi
    
    # Deploy services
    deploy_services
    exit_code=$?
    if [[ $exit_code -ne 0 ]]; then
        log_message "ERROR" "Service deployment failed"
        return $exit_code
    fi
    
    # Initialize database
    if [[ "$INITIALIZE_DATABASE" = true ]]; then
        initialize_database
        exit_code=$?
        if [[ $exit_code -ne 0 ]]; then
            log_message "ERROR" "Database initialization failed"
            return $exit_code
        fi
    fi
    
    # Invalidate cache
    invalidate_cache
    exit_code=$?
    if [[ $exit_code -ne 0 ]]; then
        log_message "WARNING" "Cache invalidation failed, but deployment can continue"
    fi
    
    # Run smoke tests
    run_smoke_tests
    exit_code=$?
    if [[ $exit_code -ne 0 ]]; then
        log_message "ERROR" "Smoke tests failed"
        return $exit_code
    fi
    
    # Perform cleanup
    cleanup
    
    log_message "INFO" "Deployment to $ENVIRONMENT environment completed successfully"
    return 0
}

# Export functions that may be used by other scripts
export -f set_environment_variables
export -f check_prerequisites
export -f log_message

# Execute main function if script is being run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
    exit $?
fi