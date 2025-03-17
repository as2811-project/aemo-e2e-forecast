terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.16"
    }
  }
  required_version = ">=1.2.0"
}

provider "aws" {
  region = "ap-southeast-2"
}

# S3 Resources : Creates the bucket, followed by creation of 'directories' to organise data and models
resource "aws_s3_bucket" "aemo-forecasts-bucket" {
  bucket = "${var.s3_bucket}"
}
resource "aws_s3_object" "aemo-raw-data" {
  bucket = aws_s3_bucket.aemo-forecasts-bucket.id
  key = "historical-data/"
}
resource "aws_s3_object" "landing-zone" {
  bucket = aws_s3_bucket.aemo-forecasts-bucket.id
  key    = "landing-zone/"
}
resource "aws_s3_object" "models" {
  bucket = aws_s3_bucket.aemo-forecasts-bucket.id
  key    = "models/"
}
resource "aws_s3_object" "curated-zone" {
  bucket = aws_s3_bucket.aemo-forecasts-bucket.id
  key = "curated-zone/"
}

# DynamoDB : Creates a DynamoDB table which will be used as a cache for the generated forecasts
resource "aws_dynamodb_table" "forecasts" {
  name = "aemo-forecasts"
  billing_mode = "PAY_PER_REQUEST"
  hash_key = "DateTime"

  attribute {
    name = "DateTime"
    type = "S"
  }
  ttl {
    attribute_name = "TimeToExist"
    enabled        = true
  }
}