terraform {
  required_version = ">= 1.10"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  # Bucket is passed at init: terraform init -backend-config="bucket=<TF_STATE_BUCKET>"
  backend "s3" {
    key          = "prod/terraform.tfstate"
    region       = "ap-southeast-1"
    encrypt      = true
    use_lockfile = true
  }
}

provider "aws" {
  region = "ap-southeast-1"
  default_tags {
    tags = {
      Project     = "pro-sports-bet"
      Environment = "prod"
      ManagedBy   = "terraform"
    }
  }
}

data "aws_caller_identity" "current" {}

module "storage" {
  source = "../../modules/storage"
  name   = "psb-data-${data.aws_caller_identity.current.account_id}"
}

module "ecr" {
  source = "../../modules/ecr"
  name   = "psb-jobs"
}

output "data_bucket" {
  value = module.storage.bucket_name
}

output "ecr_repository_url" {
  value = module.ecr.repository_url
}
