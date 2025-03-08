output "raw_data_bucket_name" {
  description = "The name of the raw data bucket"
  value       = aws_s3_bucket.raw_data.bucket
}

output "raw_data_bucket_arn" {
  description = "The ARN of the raw data bucket"
  value       = aws_s3_bucket.raw_data.arn
}

output "processed_data_bucket_name" {
  description = "The name of the processed data bucket"
  value       = aws_s3_bucket.processed_data.bucket
}

output "processed_data_bucket_arn" {
  description = "The ARN of the processed data bucket"
  value       = aws_s3_bucket.processed_data.arn
} 