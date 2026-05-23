terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

# -----------------------------------------------------------------------------
# Mock Application Load Balancer (Origin)
# This represents the Flask Backend
# -----------------------------------------------------------------------------
resource "aws_lb" "flask_backend" {
  name               = "flask-backend-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = ["sg-0123456789abcdef0"]
  subnets            = ["subnet-abcde012", "subnet-bcde012a"]
}
