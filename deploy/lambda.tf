
data "archive_file" "lambda_airquality_archive" {
  type = "zip"

  source {
    content=""
    filename = "app/__init__.py"
  }

  source {
    content=file("${path.module}/../airquality-api/app/response.py")
    filename = "app/response.py"
  }

  source {
    content=file("${path.module}/../airquality-api/app/aqi.py")
    filename = "app/aqi.py"
  }

  output_path = "${path.module}/airquality.zip"
}


resource "aws_s3_bucket" "airquality_lambda_bucket" {
  bucket = "airquality-lambda"
  acl = "private"
}

resource "aws_s3_bucket_object" "lambda_package" {
   bucket = aws_s3_bucket.airquality_lambda_bucket.id
   key = "airquality.zip"
   source = data.archive_file.lambda_airquality_archive.output_path 
   etag = filemd5("${data.archive_file.lambda_airquality_archive.output_path}")

}

resource "aws_lambda_function" "airquality_app" {
  function_name = "AirqualityWeb"

  s3_bucket = aws_s3_bucket.airquality_lambda_bucket.id
  s3_key = aws_s3_bucket_object.lambda_package.key

  runtime = "python3.8"
  handler = "app.response.get_last_day_bucketed_aqi"

  source_code_hash = filemd5("${data.archive_file.lambda_airquality_archive.output_path}")

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