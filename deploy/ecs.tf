

resource "aws_ecr_repository" "airquality_repo" {
  name = "airquality-repo"
}


resource "aws_cloudwatch_log_group" "api_logs" {
  name = "api-logs"

}

resource "aws_ecs_cluster" "airquality_web" {
  name = "airquality-web"

  configuration {
    execute_command_configuration {
      logging = "OVERRIDE"

      log_configuration {
        cloud_watch_encryption_enabled = true
        cloud_watch_log_group_name     = aws_cloudwatch_log_group.api_logs.name
      }
    }
  }
}

data "aws_iam_role" "ecs_task_execution_role" {
  name = "ecsTaskExecutionRole"
}



resource "aws_ecs_task_definition" "airquality_webapp" {
  family = "airquality-webapp"
  requires_compatibilities = ["FARGATE"]
  network_mode = "awsvpc"
  cpu = 256
  memory = 512
  execution_role_arn = data.aws_iam_role.ecs_task_execution_role.arn
  container_definitions = jsonencode([{
    name      = "airquality-api"
    image     = "402878705062.dkr.ecr.us-west-2.amazonaws.com/airquality-repo:airquality_api"
    essential = true
    portMappings = [
      {
        containerPort = 5000
        hostPort      = 5000
        protocol = "tcp"
      }
    ]
  }])

}


resource "aws_ecs_service" "airquality_api" {
  name            = "airquality-api"
  cluster         = aws_ecs_cluster.airquality_web.arn
  task_definition = aws_ecs_task_definition.airquality_webapp.arn
  desired_count   = 0
  launch_type     = "FARGATE"
  network_configuration {
    subnets = ["subnet-06e55213c335afde8"]
    assign_public_ip = true
  }
}