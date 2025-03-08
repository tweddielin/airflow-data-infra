variable "aws_region" {
  description = "The AWS region to deploy resources"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "The name of the project"
  type        = string
  default     = "airflow-data-infra"
}

variable "environment" {
  description = "The environment (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "vpc_cidr" {
  description = "The CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "The availability zones to use"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b", "us-east-1c"]
}

variable "private_subnet_cidrs" {
  description = "The CIDR blocks for the private subnets"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
}

variable "public_subnet_cidrs" {
  description = "The CIDR blocks for the public subnets"
  type        = list(string)
  default     = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]
}

variable "db_name" {
  description = "The name of the database"
  type        = string
  default     = "airflow"
}

variable "db_username" {
  description = "The username for the database"
  type        = string
  default     = "airflow"
  sensitive   = true
}

variable "db_password" {
  description = "The password for the database"
  type        = string
  sensitive   = true
}

variable "db_instance_class" {
  description = "The instance class for the database"
  type        = string
  default     = "db.t3.medium"
}

variable "airflow_instance_type" {
  description = "The instance type for Airflow instances"
  type        = string
  default     = "t3.medium"
}

variable "monitoring_instance_type" {
  description = "The instance type for monitoring instances"
  type        = string
  default     = "t3.small"
}

variable "key_name" {
  description = "The name of the key pair to use for SSH access"
  type        = string
}

variable "airflow_webserver_count" {
  description = "The number of Airflow webserver instances"
  type        = number
  default     = 1
}

variable "airflow_scheduler_count" {
  description = "The number of Airflow scheduler instances"
  type        = number
  default     = 1
}

variable "airflow_worker_count" {
  description = "The number of Airflow worker instances"
  type        = number
  default     = 3
}

variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
  default = {
    Project     = "airflow-data-infra"
    ManagedBy   = "terraform"
  }
} 