terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.27"
    }
  }

  required_version = ">= 0.14.9"
}


provider "aws" {
  profile = "default"
  region  = "us-west-2"
}

module "airquality_dev" {
  source = "./modules/airquality-app-deployment/"

  env = "dev"
}

module "airquality_prod" {
  source = "./modules/airquality-app-deployment/"

  env = "prod"
}

/*
# Assigning my static site to davidshere.net
resource "aws_route53_zone" "www" {
  name = "davidshere.net"
}

resource "aws_route53_record" "www" {
  zone_id = resource.aws_route53_zone.www.zone_id
  name    = "davidshere.net"
  type    = "A"

  alias {
    name                   = module.airquality_prod.aws_s3_bucket.airquality_bucket.website_endpoint
    zone_id                = module.airquality_prod.aws_s3_bucket.airquality_bucket.hosted_zone_id
    evaluate_target_health = false
  }
}

*/