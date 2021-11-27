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

resource "aws_instance" "app_server" {
  ami           = "ami-0d9d50fd562c1ed4e"
  instance_type = "t4g.nano"
  key_name = "linux-desktop-key-pair"
  vpc_security_group_ids = [aws_security_group.main.id]


  tags = {
    Name = "AirQualityAppServer"
  }
}

resource "aws_security_group" "main" {
  egress = [
    {
      cidr_blocks = [ "0.0.0.0/0", ]
      description = ""
      from_port = 0
      ipv6_cidr_blocks = []
      prefix_list_ids = []
      protocol = "-1"
      security_groups = []
      self = false
      to_port = 0
    }
  ]
  ingress = [
    {
      cidr_blocks = [ "0.0.0.0/0", ]
      description = ""
      from_port = 22
      ipv6_cidr_blocks = []
      prefix_list_ids = []
      protocol = "tcp"
      security_groups = []
      self = false
      to_port = 22
    }
  ]
}

resource "aws_dynamodb_table" "readings" {
  name = "Readings"
  billing_mode = "PAY_PER_REQUEST"
  hash_key = "DeviceId"
  range_key = "RecordedAt"
  
  attribute {
    name = "DeviceId"
		type = "S"
  }

  attribute {
    name = "RecordedAt"
    type = "S"
  }
}

