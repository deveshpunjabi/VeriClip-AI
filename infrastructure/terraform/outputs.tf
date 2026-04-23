output "cloud_run_url" {
  description = "URL of the deployed Cloud Run service"
  value       = module.cloud_run.service_url
}

output "project_id" {
  description = "GCP Project ID"
  value       = var.project_id
}

output "storage_buckets" {
  description = "Created Cloud Storage buckets"
  value       = module.storage.bucket_names
}
