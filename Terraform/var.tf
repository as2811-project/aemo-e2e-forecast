locals {
  glue_src = "${path.root}/../pipeline/glue/"
}
variable "s3_bucket" {
  type = string
}
variable "project" {
  type = string
}