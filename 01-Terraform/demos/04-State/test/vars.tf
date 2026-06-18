variable "aws_region" {
  default = "us-east-1"
}

# Busca dinamica da Amazon Linux 2023 mais recente, evitando AMIs hardcoded que expiram.
data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-2023.*-x86_64"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

variable "project" {
  default = "lab-fiap"
}

variable "nomeGrupo" {
  default = "teste"
}

variable "env" {
  default = "prod"
}
