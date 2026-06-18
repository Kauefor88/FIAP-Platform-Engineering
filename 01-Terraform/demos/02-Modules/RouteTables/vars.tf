variable "project" {
  default = "fiap-lab"
}

data "aws_vpc" "vpc" {
  tags = {
    Name = var.project
  }
}

data "aws_internet_gateway" "igw" {
  filter {
    name   = "attachment.vpc-id"
    values = [data.aws_vpc.vpc.id]
  }
}

variable "env" {
  default = "prod"
}

output "vpc_id" {
  value = data.aws_vpc.vpc.id
}

variable "aws_region" {
  default = "us-east-1"
}
