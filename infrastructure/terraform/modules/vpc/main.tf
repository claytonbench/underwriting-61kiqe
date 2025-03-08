# Define common tags to be used across all resources
locals {
  common_tags = {
    Environment = var.environment
    Terraform   = "true"
    Project     = "LoanManagementSystem"
  }
}

# Create the main VPC for the loan management system
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = var.enable_dns_hostnames
  enable_dns_support   = var.enable_dns_support
  
  tags = {
    Name        = "${var.environment}-vpc"
    Environment = var.environment
  }
}

# Public subnets for resources that need internet access like load balancers
resource "aws_subnet" "public" {
  count                   = length(var.public_subnet_cidrs)
  vpc_id                  = aws_vpc.main.id
  cidr_block              = element(var.public_subnet_cidrs, count.index)
  availability_zone       = element(var.availability_zones, count.index)
  map_public_ip_on_launch = true
  
  tags = {
    Name        = "${var.environment}-public-subnet-${element(var.availability_zones, count.index)}"
    Environment = var.environment
    Tier        = "Public"
  }
}

# Private subnets for application resources that don't need direct internet access
resource "aws_subnet" "private" {
  count                   = length(var.private_subnet_cidrs)
  vpc_id                  = aws_vpc.main.id
  cidr_block              = element(var.private_subnet_cidrs, count.index)
  availability_zone       = element(var.availability_zones, count.index)
  map_public_ip_on_launch = false
  
  tags = {
    Name        = "${var.environment}-private-subnet-${element(var.availability_zones, count.index)}"
    Environment = var.environment
    Tier        = "Private"
  }
}

# Database subnets for data tier resources like RDS and ElastiCache
resource "aws_subnet" "database" {
  count                   = length(var.database_subnet_cidrs)
  vpc_id                  = aws_vpc.main.id
  cidr_block              = element(var.database_subnet_cidrs, count.index)
  availability_zone       = element(var.availability_zones, count.index)
  map_public_ip_on_launch = false
  
  tags = {
    Name        = "${var.environment}-database-subnet-${element(var.availability_zones, count.index)}"
    Environment = var.environment
    Tier        = "Database"
  }
}

# Internet Gateway to allow public subnets to access the internet
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id
  
  tags = {
    Name        = "${var.environment}-igw"
    Environment = var.environment
  }
}

# Elastic IPs for NAT Gateways
resource "aws_eip" "nat" {
  count = var.enable_nat_gateway ? (var.single_nat_gateway ? 1 : length(var.availability_zones)) : 0
  vpc   = true
  
  tags = {
    Name        = "${var.environment}-nat-eip-${count.index + 1}"
    Environment = var.environment
  }
}

# NAT Gateways to allow private subnets to access the internet
resource "aws_nat_gateway" "nat" {
  count         = var.enable_nat_gateway ? (var.single_nat_gateway ? 1 : length(var.availability_zones)) : 0
  allocation_id = element(aws_eip.nat.*.id, count.index)
  subnet_id     = element(aws_subnet.public.*.id, count.index)
  
  tags = {
    Name        = "${var.environment}-nat-gw-${count.index + 1}"
    Environment = var.environment
  }
  
  depends_on = [aws_internet_gateway.main]
}

# Route table for public subnets with route to internet gateway
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id
  
  tags = {
    Name        = "${var.environment}-public-rt"
    Environment = var.environment
  }
}

# Route to internet gateway for public subnets
resource "aws_route" "public_internet_gateway" {
  route_table_id         = aws_route_table.public.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.main.id
}

# Route tables for private subnets with routes to NAT gateways
resource "aws_route_table" "private" {
  count  = var.enable_nat_gateway ? (var.single_nat_gateway ? 1 : length(var.availability_zones)) : 0
  vpc_id = aws_vpc.main.id
  
  tags = {
    Name        = "${var.environment}-private-rt-${count.index + 1}"
    Environment = var.environment
  }
}

# Routes to NAT gateways for private subnets
resource "aws_route" "private_nat_gateway" {
  count                  = var.enable_nat_gateway ? (var.single_nat_gateway ? 1 : length(var.availability_zones)) : 0
  route_table_id         = element(aws_route_table.private.*.id, count.index)
  destination_cidr_block = "0.0.0.0/0"
  nat_gateway_id         = element(aws_nat_gateway.nat.*.id, var.single_nat_gateway ? 0 : count.index)
}

# Route table for database subnets
resource "aws_route_table" "database" {
  vpc_id = aws_vpc.main.id
  
  tags = {
    Name        = "${var.environment}-database-rt"
    Environment = var.environment
  }
}

# Associates public subnets with the public route table
resource "aws_route_table_association" "public" {
  count          = length(var.public_subnet_cidrs)
  subnet_id      = element(aws_subnet.public.*.id, count.index)
  route_table_id = aws_route_table.public.id
}

# Associates private subnets with private route tables
resource "aws_route_table_association" "private" {
  count          = length(var.private_subnet_cidrs)
  subnet_id      = element(aws_subnet.private.*.id, count.index)
  route_table_id = var.single_nat_gateway ? aws_route_table.private[0].id : element(aws_route_table.private.*.id, count.index)
}

# Associates database subnets with the database route table
resource "aws_route_table_association" "database" {
  count          = length(var.database_subnet_cidrs)
  subnet_id      = element(aws_subnet.database.*.id, count.index)
  route_table_id = aws_route_table.database.id
}

# Subnet group for RDS instances spanning multiple availability zones
resource "aws_db_subnet_group" "database" {
  count       = var.create_database_subnet_group ? 1 : 0
  name        = "${var.environment}-db-subnet-group"
  subnet_ids  = aws_subnet.database.*.id
  description = "Database subnet group for ${var.environment}"
  
  tags = {
    Name        = "${var.environment}-db-subnet-group"
    Environment = var.environment
  }
}

# Subnet group for ElastiCache clusters spanning multiple availability zones
resource "aws_elasticache_subnet_group" "cache" {
  count       = var.create_elasticache_subnet_group ? 1 : 0
  name        = "${var.environment}-elasticache-subnet-group"
  subnet_ids  = aws_subnet.database.*.id
  description = "ElastiCache subnet group for ${var.environment}"
  
  tags = {
    Name        = "${var.environment}-elasticache-subnet-group"
    Environment = var.environment
  }
}

# VPC Flow Logs for network traffic monitoring and security analysis
resource "aws_flow_log" "main" {
  count                = var.enable_vpc_flow_logs && var.flow_log_bucket_arn != "" ? 1 : 0
  log_destination      = var.flow_log_bucket_arn
  log_destination_type = "s3"
  traffic_type         = "ALL"
  vpc_id               = aws_vpc.main.id
  
  tags = {
    Name        = "${var.environment}-vpc-flow-log"
    Environment = var.environment
  }
}

# VPC Endpoint for S3 to allow private access without internet
resource "aws_vpc_endpoint" "s3" {
  count             = var.enable_s3_endpoint ? 1 : 0
  vpc_id            = aws_vpc.main.id
  service_name      = "com.amazonaws.${var.aws_region}.s3"
  vpc_endpoint_type = "Gateway"
  route_table_ids   = concat(aws_route_table.private.*.id, [aws_route_table.public.id, aws_route_table.database.id])
  
  tags = {
    Name        = "${var.environment}-s3-endpoint"
    Environment = var.environment
  }
}

# Outputs for use by other modules
output "vpc_id" {
  description = "The ID of the VPC"
  value       = aws_vpc.main.id
}

output "vpc_cidr" {
  description = "The CIDR block of the VPC"
  value       = aws_vpc.main.cidr_block
}

output "public_subnet_ids" {
  description = "List of IDs of public subnets"
  value       = aws_subnet.public.*.id
}

output "private_subnet_ids" {
  description = "List of IDs of private subnets"
  value       = aws_subnet.private.*.id
}

output "database_subnet_ids" {
  description = "List of IDs of database subnets"
  value       = aws_subnet.database.*.id
}

output "database_subnet_group_name" {
  description = "Name of the database subnet group"
  value       = join("", aws_db_subnet_group.database.*.name)
}

output "elasticache_subnet_group_name" {
  description = "Name of the ElastiCache subnet group"
  value       = join("", aws_elasticache_subnet_group.cache.*.name)
}

output "nat_gateway_ids" {
  description = "List of NAT Gateway IDs"
  value       = aws_nat_gateway.nat.*.id
}

output "availability_zones" {
  description = "List of availability zones used"
  value       = var.availability_zones
}

output "s3_endpoint_id" {
  description = "ID of S3 endpoint"
  value       = join("", aws_vpc_endpoint.s3.*.id)
}