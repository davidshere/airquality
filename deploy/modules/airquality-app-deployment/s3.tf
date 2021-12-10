resource "aws_s3_bucket" "airquality_bucket" {
  bucket = "home-airquality-${var.env}"

  acl = "public-read"

  website {
    index_document = "index.html"
  }
  policy = jsonencode(
    {
      "Version" : "2012-10-17",
      "Statement" : [
        {
          "Sid" : "PublicReadGetObject",
          "Effect" : "Allow",
          "Principal" : "*",
          "Action" : [
            "s3:GetObject"
          ],
          "Resource" : [
            "arn:aws:s3:::home-airquality-${var.env}/*"
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

  bucket       = resource.aws_s3_bucket.airquality_bucket.bucket
  key          = each.key
  content_type = each.value.content_type

  source  = each.value.source_path
  content = each.value.content

  etag = each.value.digests.md5
}
