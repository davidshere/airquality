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

resource "aws_dynamodb_table" "readings" {
  name         = "Readings"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "DeviceId"
  range_key    = "RecordedAt"
  point_in_time_recovery {
    enabled = true
  }

  attribute {
    name = "DeviceId"
    type = "S"
  }

  attribute {
    name = "RecordedAt"
    type = "S"
  }
}


resource "aws_s3_bucket" "airquality_bucket" {
  bucket = "davids-airquality-static"

  acl = "public-read"

  website {
    index_document = "index.html"
  }
  policy = jsonencode(
    {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": [
                "s3:GetObject"
            ],
            "Resource": [
                "arn:aws:s3:::davids-airquality-static/*"
            ]
        }
    ]
}
  )
}

module "template_files" {
  source = "hashicorp/dir/template"

  base_dir = "${path.module}/../airquality-api/build"
}

resource "aws_s3_bucket_object" "static_files" {
  for_each = module.template_files.files

  bucket = resource.aws_s3_bucket.airquality_bucket.bucket
  key = each.key
  content_type = each.value.content_type

  source= each.value.source_path
  content = each.value.content

  etag = each.value.digests.md5
}

