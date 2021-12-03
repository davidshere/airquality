/*

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
*/