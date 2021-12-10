output "web_address" {
    description = "Website of airquality for this environment"
    value = resource.aws_s3_bucket.airquality_bucket
}