# Preparing the application package
data "archive_file" "lambda_airquality_archive" {
  type = "zip"

  source {
    content  = ""
    filename = "app/__init__.py"
  }

  source {
    content  = file("${path.root}/../airquality-api/app/response.py")
    filename = "app/response.py"
  }

  source {
    content  = file("${path.root}/../airquality-api/app/aqi.py")
    filename = "app/aqi.py"
  }

  source {
    content = file("${path.root}/../airquality-api/app/connection.py")
    filename = "app/connection.py"
  }

  source {
    content = file("${path.root}/../airquality-api/app/reading.py")
    filename = "app/reading.py"
  }

  source {
    content = file("${path.root}/../airquality-api/app/lambda.py")
    filename = "app/lambda.py"
  }

  output_path = "${path.root}/airquality.zip"
}


resource "aws_s3_bucket" "airquality_lambda_bucket" {
  bucket = "airquality-lambda-${var.env}"
  acl    = "private"
}

resource "aws_s3_bucket_object" "lambda_package" {
  bucket = aws_s3_bucket.airquality_lambda_bucket.id
  key    = "airquality.zip"
  source = data.archive_file.lambda_airquality_archive.output_path
  etag   = filemd5("${data.archive_file.lambda_airquality_archive.output_path}")

}

# Defining the lambda function
resource "aws_lambda_function" "airquality_app" {
  function_name = "airquality-web-${var.env}"

  s3_bucket = aws_s3_bucket.airquality_lambda_bucket.id
  s3_key    = aws_s3_bucket_object.lambda_package.key

  runtime = "python3.8"
  handler = "app.lambda.handler"

  source_code_hash = filemd5("${data.archive_file.lambda_airquality_archive.output_path}")

  role = aws_iam_role.lambda_exec.arn

  environment {
    variables = {
      TZ =  "America/Los_Angeles"
    }
  }
}


resource "aws_cloudwatch_log_group" "airquality_web" {
  name = "/aws/lambda/${aws_lambda_function.airquality_app.function_name}"

  retention_in_days = 30
}

# IAM Roles and Policies
resource "aws_iam_role" "lambda_exec" {
  name = "serverless_lambda_${var.env}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Sid    = ""
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_execution_policy_attachment" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_policy" "lambda_dynamo_read_policy" {
  name        = "dynamo-read-policy-${var.env}"
  description = "A policy to allow lambda to read a specific dynamo table"

  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Action" : [
          "dynamodb:Query",
          "dynamodb:PutItem"
        ],
        "Effect" : "Allow",
        "Resource" : "${aws_dynamodb_table.readings.arn}"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_dynamo_read_policy_attachment" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = aws_iam_policy.lambda_dynamo_read_policy.arn
}

# API Gateway
resource "aws_apigatewayv2_api" "lambda" {
  name          = "airquality_gateway_${var.env}"
  protocol_type = "HTTP"

  cors_configuration {
    allow_origins = ["*"]
    allow_methods = ["POST", "GET", "OPTIONS"]
    allow_headers = ["content-type"]
    max_age = 300
  }

}

resource "aws_apigatewayv2_stage" "lambda" {
  api_id = aws_apigatewayv2_api.lambda.id

  name        = "${var.env}"
  auto_deploy = true

  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.api_gw.arn

    format = jsonencode({
      requestId               = "$context.requestId"
      sourceIp                = "$context.identity.sourceIp"
      requestTime             = "$context.requestTime"
      protocol                = "$context.protocol"
      httpMethod              = "$context.httpMethod"
      resourcePath            = "$context.resourcePath"
      routeKey                = "$context.routeKey"
      status                  = "$context.status"
      responseLength          = "$context.responseLength"
      integrationErrorMessage = "$context.integrationErrorMessage"
      }
    )
  }
}

resource "aws_apigatewayv2_integration" "airquality_reading_data" {
  api_id = aws_apigatewayv2_api.lambda.id

  integration_uri    = aws_lambda_function.airquality_app.invoke_arn
  integration_type   = "AWS_PROXY"
  integration_method = "POST"
}

resource "aws_apigatewayv2_route" "get_readings" {
  api_id = aws_apigatewayv2_api.lambda.id

  route_key = "GET /data"
  target    = "integrations/${aws_apigatewayv2_integration.airquality_reading_data.id}"
}

resource "aws_cloudwatch_log_group" "api_gw" {
  name = "/aws/api_gw/${aws_apigatewayv2_api.lambda.name}"

  retention_in_days = 30
}

resource "aws_lambda_permission" "api_gw" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.airquality_app.function_name
  principal     = "apigateway.amazonaws.com"

  source_arn = "${aws_apigatewayv2_api.lambda.execution_arn}/*/*"
}