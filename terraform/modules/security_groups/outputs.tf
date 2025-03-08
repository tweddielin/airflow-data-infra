output "airflow_sg_id" {
  description = "The ID of the Airflow security group"
  value       = aws_security_group.airflow.id
}

output "rds_sg_id" {
  description = "The ID of the RDS security group"
  value       = aws_security_group.rds.id
}

output "monitoring_sg_id" {
  description = "The ID of the monitoring security group"
  value       = aws_security_group.monitoring.id
}

output "lb_sg_id" {
  description = "The ID of the load balancer security group"
  value       = aws_security_group.lb.id
} 