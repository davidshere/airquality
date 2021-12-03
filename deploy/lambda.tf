/*
data "archive_file" "lambda_airquality_archive" {
  type = "zip"

  source_dir = "${path.module}/../airquality-api/"
  output_path = "${path.module}/airquality.zip"

  excludes = [
    "venv/lib/python3.8/site-packages/boto3",
    "venv/lib/python3.8/site-packages/botocore"
  ]
}
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin 402878705062.dkr.ecr.us-west-2.amazonaws.com


resource "aws_s3_bucket" "airquality_web_bucket" {
  bucket = "airquality-lambda"
  acl = "private"
}

resource "aws_s3_bucket_object" "lambda_package" {
   bucket = aws_s3_bucket.airquality_web_bucket.id
   key = "airquality.zip"
   source = "airquality.zip" 
   etag = filemd5("airquality.zip")

}

resource "aws_lambda_function" "airquality_app" {
  function_name = "AirqualityWeb"

  s3_bucket = aws_s3_bucket.airquality_web_bucket.id
  s3_key = aws_s3_bucket_object.lambda_package.key

  runtime = "python3.8"
  handler = "run.http_server"

  source_code_hash = filemd5("airquality.zip")

  role = aws_iam_role.lambda_exec.arn
}


resource "aws_cloudwatch_log_group" "airquality_web" {
  name = "/aws/lambda/${aws_lambda_function.airquality_app.function_name}"

  retention_in_days = 30
}

resource "aws_iam_role" "lambda_exec" {
  name = "serverless_lambda"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Sid    = ""
      Principal = {
        Service = "lambda.amazonaws.com"
      }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_policy" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}
*/