variable "project_name" {
  description = "The name of the project"
  type        = string
}

variable "environment" {
  description = "The environment (dev, staging, prod)"
  type        = string
}

variable "raw_data_bucket_name" {
  description = "The name of the raw data bucket"
  type        = string
}

variable "processed_data_bucket_name" {
  description = "The name of the processed data bucket"
  type        = string
}

variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
  default     = {}
} 