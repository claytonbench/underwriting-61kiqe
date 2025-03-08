output "redis_endpoint" {
  description = "Primary endpoint address of the Redis replication group"
  value       = aws_elasticache_replication_group.redis.primary_endpoint_address
}

output "redis_port" {
  description = "Port number on which the Redis cluster accepts connections"
  value       = aws_elasticache_replication_group.redis.port
}

output "redis_replication_group_id" {
  description = "Identifier of the Redis replication group"
  value       = aws_elasticache_replication_group.redis.id
}

output "redis_reader_endpoint" {
  description = "Reader endpoint address for the Redis replication group"
  value       = aws_elasticache_replication_group.redis.reader_endpoint_address
}

output "redis_arn" {
  description = "ARN (Amazon Resource Name) of the Redis replication group"
  value       = aws_elasticache_replication_group.redis.arn
}

output "redis_engine_version_actual" {
  description = "Actual engine version being used by the Redis cluster"
  value       = aws_elasticache_replication_group.redis.engine_version_actual
}

output "redis_cluster_enabled" {
  description = "Flag indicating if cluster mode is enabled"
  value       = aws_elasticache_replication_group.redis.cluster_enabled
}