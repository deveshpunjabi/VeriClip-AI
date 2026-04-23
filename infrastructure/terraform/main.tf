# VeriClip AI - Main Terraform Configuration
terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
  backend "gcs" {
    bucket = "vericlip-ai-terraform-state"
    prefix = "terraform/state"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Enable required APIs
resource "google_project_service" "apis" {
  for_each = toset([
    "run.googleapis.com",
    "aiplatform.googleapis.com",
    "firestore.googleapis.com",
    "storage.googleapis.com",
    "pubsub.googleapis.com",
  ])
  project            = var.project_id
  service            = each.value
  disable_on_destroy = false
}

# Cloud Run Service
module "cloud_run" {
  source = "./modules/cloud_run"
  project_id = var.project_id
  region     = var.region
}

# Vertex AI
module "vertex_ai" {
  source = "./modules/vertex_ai"
  project_id = var.project_id
  region     = var.region
}

# Firebase
module "firebase" {
  source = "./modules/firebase"
  project_id = var.project_id
}

# Storage
module "storage" {
  source = "./modules/storage"
  project_id = var.project_id
}
