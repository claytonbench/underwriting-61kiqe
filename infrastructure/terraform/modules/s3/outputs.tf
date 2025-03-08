# Document storage bucket outputs
output "document_bucket_name" {
  description = "Name of the S3 bucket created for document storage"
  value       = aws_s3_bucket.document_bucket.id
}

output "document_bucket_arn" {
  description = "ARN of the S3 bucket created for document storage"
  value       = aws_s3_bucket.document_bucket.arn
}

output "document_bucket_domain_name" {
  description = "Domain name of the S3 bucket created for document storage"
  value       = aws_s3_bucket.document_bucket.bucket_domain_name
}

output "document_bucket_regional_domain_name" {
  description = "Regional domain name of the S3 bucket created for document storage"
  value       = aws_s3_bucket.document_bucket.bucket_regional_domain_name
}

# Logging bucket outputs
output "log_bucket_name" {
  description = "Name of the S3 bucket created for access logs"
  value       = aws_s3_bucket.log_bucket.id
}

output "log_bucket_arn" {
  description = "ARN of the S3 bucket created for access logs"
  value       = aws_s3_bucket.log_bucket.arn
}

# Replica bucket outputs (conditional on replication being enabled)
output "replica_bucket_name" {
  description = "Name of the replica S3 bucket created for disaster recovery"
  value       = var.enable_replication ? aws_s3_bucket.document_bucket_replica[0].id : null
}

output "replica_bucket_arn" {
  description = "ARN of the replica S3 bucket created for disaster recovery"
  value       = var.enable_replication ? aws_s3_bucket.document_bucket_replica[0].arn : null
}

# Replication role output (conditional on replication being enabled)
output "replication_role_arn" {
  description = "ARN of the IAM role created for S3 replication"
  value       = var.enable_replication ? aws_iam_role.replication_role[0].arn : null
}