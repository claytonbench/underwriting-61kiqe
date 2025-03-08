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
  value       = var.create_database_subnet_group ? aws_db_subnet_group.database[0].name : ""
}

output "elasticache_subnet_group_name" {
  description = "Name of the ElastiCache subnet group"
  value       = var.create_elasticache_subnet_group ? aws_elasticache_subnet_group.cache[0].name : ""
}

output "nat_gateway_ids" {
  description = "List of NAT Gateway IDs"
  value       = aws_nat_gateway.nat.*.id
}

output "availability_zones" {
  description = "List of availability zones used"
  value       = var.availability_zones
}

output "public_route_table_id" {
  description = "ID of the public route table"
  value       = aws_route_table.public.id
}

output "private_route_table_ids" {
  description = "List of IDs of private route tables"
  value       = aws_route_table.private.*.id
}

output "database_route_table_id" {
  description = "ID of the database route table"
  value       = aws_route_table.database.id
}

output "s3_endpoint_id" {
  description = "ID of the S3 VPC endpoint if created"
  value       = var.enable_s3_endpoint ? aws_vpc_endpoint.s3[0].id : ""
}