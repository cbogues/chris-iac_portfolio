terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Local state for now (matches okta/). Remote backend migration is a
  # stretch goal, see repo root README.
}

provider "aws" {
  region = var.aws_region
}
