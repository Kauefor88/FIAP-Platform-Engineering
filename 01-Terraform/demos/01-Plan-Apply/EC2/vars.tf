variable "aws_region" {
  description = "Regiao AWS onde a infraestrutura sera criada."
  default     = "us-east-1"
}

# Em vez de fixar AMIs antigas por regiao (que expiram com o tempo), buscamos
# dinamicamente a Amazon Linux 2023 mais recente publicada pela propria AWS.
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
