data "aws_iam_policy_document" "glue_assume_role_policy" {
  statement {
    sid = ""
    effect = "Allow"
    actions = ["sts:AssumeRole"]
    principals {
      type = "Service"
      identifiers = ["glue.amazonaws.com"]
    }
  }
}

data "aws_iam_policy_document" "glue_policy_document" {
  statement {
    effect = "Allow"
    resources = ["arn:aws:s3:::${var.s3_bucket}/*"]
    actions = [
      "s3:PutObject",
      "s3:GetObject",
      "s3:DeleteObject"
    ]
  }
}

resource "aws_iam_policy" "data_lake_access_policy" {
  name        = "s3DataLakePolicy-${var.s3_bucket}"
  description = "allows for running glue job in the glue console and access the S3 bucket containing the data"
  policy      = data.aws_iam_policy_document.glue_policy_document.json
  tags = {
    Application = var.project
  }
}

resource "aws_iam_role" "glue_service_role" {
name = "aws_glue_job_runner"
assume_role_policy = data.aws_iam_policy_document.glue_assume_role_policy.json
tags = {
Application = var.project
}
}

resource "aws_iam_role_policy_attachment" "data_lake_permissions" {
  role = aws_iam_role.glue_service_role.name
  policy_arn = aws_iam_policy.data_lake_access_policy.arn
}

# Lambda IAM Role
data "aws_iam_policy_document" "lambda_assume_role_policy" {
  statement {
    effect = "Allow"
    actions = ["sts:AssumeRole"]
    principals {
      type = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

data "aws_iam_policy_document" "lambda_policy_document" {
  statement {
    effect = "Allow"
    resources = ["arn:aws:s3:::${var.s3_bucket}/*"]
    actions = [
      "s3:PutObject",
      "s3:GetObject",
      "s3:ListBucket",
      "s3:DeleteObject"
    ]
  }

  statement {
    effect = "Allow"
    resources = ["*"]
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
  }
}

resource "aws_iam_policy" "lambda_s3_policy" {
  name        = "lambda-s3-access-policy-${var.s3_bucket}"
  description = "Allows Lambda functions to access the S3 bucket and write logs"
  policy      = data.aws_iam_policy_document.lambda_policy_document.json
  tags = {
    Application = var.project
  }
}

resource "aws_iam_role" "lambda_execution_role" {
  name = "lambda_execution_role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role_policy.json
  tags = {
    Application = var.project
  }
}

resource "aws_iam_role_policy_attachment" "lambda_s3_policy_attachment" {
  role       = aws_iam_role.lambda_execution_role.name
  policy_arn = aws_iam_policy.lambda_s3_policy.arn
}

# Step Functions IAM Role
data "aws_iam_policy_document" "step_functions_assume_role_policy" {
  statement {
    effect = "Allow"
    actions = ["sts:AssumeRole"]
    principals {
      type = "Service"
      identifiers = ["states.amazonaws.com"]
    }
  }
}

data "aws_iam_policy_document" "step_functions_policy_document" {
  statement {
    effect = "Allow"
    resources = ["*"]
    actions = [
      "lambda:InvokeFunction"
    ]
  }

  statement {
    effect = "Allow"
    resources = ["*"]
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
  }
}

resource "aws_iam_policy" "step_functions_policy" {
  name        = "step-functions-invoke-lambda-policy"
  description = "Allows Step Functions to invoke Lambda functions"
  policy      = data.aws_iam_policy_document.step_functions_policy_document.json
  tags = {
    Application = var.project
  }
}

resource "aws_iam_role" "step_functions_execution_role" {
  name = "step_functions_execution_role"
  assume_role_policy = data.aws_iam_policy_document.step_functions_assume_role_policy.json
  tags = {
    Application = var.project
  }
}

resource "aws_iam_role_policy_attachment" "step_functions_policy_attachment" {
  role       = aws_iam_role.step_functions_execution_role.name
  policy_arn = aws_iam_policy.step_functions_policy.arn
}