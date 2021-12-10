resource "aws_dynamodb_table" "readings" {
  name         = "${var.env}-readings"

  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "DeviceId"
  range_key    = "RecordedAt"

  attribute {
    name = "DeviceId"
    type = "S"
  }

  attribute {
    name = "RecordedAt"
    type = "S"
  }
}
