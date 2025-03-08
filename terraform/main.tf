terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
  
  backend "s3" {
    bucket = "terraform-state-airflow-data-infra"
    key    = "terraform.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region = var.aws_region
}

# VPC and Networking
module "vpc" {
  source = "./modules/vpc"
  
  vpc_name        = "${var.project_name}-vpc"
  vpc_cidr        = var.vpc_cidr
  azs             = var.availability_zones
  private_subnets = var.private_subnet_cidrs
  public_subnets  = var.public_subnet_cidrs
  
  tags = var.tags
}

# Security Groups
module "security_groups" {
  source = "./modules/security_groups"
  
  vpc_id      = module.vpc.vpc_id
  project_name = var.project_name
  
  tags = var.tags
}

# S3 Buckets
module "s3" {
  source = "./modules/s3"
  
  project_name = var.project_name
  environment  = var.environment
  
  raw_data_bucket_name     = "${var.project_name}-raw-data-${var.environment}"
  processed_data_bucket_name = "${var.project_name}-processed-data-${var.environment}"
  
  tags = var.tags
}

# RDS PostgreSQL
module "rds" {
  source = "./modules/rds"
  
  project_name    = var.project_name
  environment     = var.environment
  vpc_id          = module.vpc.vpc_id
  subnet_ids      = module.vpc.private_subnet_ids
  security_group_ids = [module.security_groups.rds_sg_id]
  
  db_name         = var.db_name
  db_username     = var.db_username
  db_password     = var.db_password
  db_instance_class = var.db_instance_class
  
  tags = var.tags
}

# EC2 Instances for Airflow
module "airflow" {
  source = "./modules/airflow"
  
  project_name    = var.project_name
  environment     = var.environment
  vpc_id          = module.vpc.vpc_id
  subnet_ids      = module.vpc.private_subnet_ids
  security_group_ids = [module.security_groups.airflow_sg_id]
  
  instance_type   = var.airflow_instance_type
  key_name        = var.key_name
  
  webserver_count = var.airflow_webserver_count
  scheduler_count = var.airflow_scheduler_count
  worker_count    = var.airflow_worker_count
  
  db_host         = module.rds.db_endpoint
  db_name         = var.db_name
  db_username     = var.db_username
  db_password     = var.db_password
  
  s3_raw_data_bucket      = module.s3.raw_data_bucket_name
  s3_processed_data_bucket = module.s3.processed_data_bucket_name
  
  tags = var.tags
}

# Monitoring (Prometheus and Grafana)
module "monitoring" {
  source = "./modules/monitoring"
  
  project_name    = var.project_name
  environment     = var.environment
  vpc_id          = module.vpc.vpc_id
  subnet_ids      = module.vpc.private_subnet_ids
  security_group_ids = [module.security_groups.monitoring_sg_id]
  
  instance_type   = var.monitoring_instance_type
  key_name        = var.key_name
  
  airflow_webserver_ips = module.airflow.webserver_private_ips
  airflow_scheduler_ips = module.airflow.scheduler_private_ips
  airflow_worker_ips    = module.airflow.worker_private_ips
  
  tags = var.tags
}

# Load Balancer
module "load_balancer" {
  source = "./modules/load_balancer"
  
  project_name    = var.project_name
  environment     = var.environment
  vpc_id          = module.vpc.vpc_id
  subnet_ids      = module.vpc.public_subnet_ids
  security_group_ids = [module.security_groups.lb_sg_id]
  
  airflow_webserver_ids = module.airflow.webserver_instance_ids
  monitoring_instance_ids = module.monitoring.instance_ids
  
  tags = var.tags
} 