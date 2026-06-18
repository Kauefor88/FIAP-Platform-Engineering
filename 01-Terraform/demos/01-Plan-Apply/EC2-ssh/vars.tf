variable "aws_region" {
  description = "Regiao AWS onde a infraestrutura sera criada."
  default     = "us-east-1"
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

variable "key_name" {
  description = "Nome do par de chaves usado para acesso SSH (criado no setup do Learner Lab)."
  default     = "vockey"
}

variable "path_to_key" {
  description = "Caminho local da chave privada usada pelo provisioner remote-exec."
  default     = "/home/vscode/.ssh/vockey.pem"
}

variable "instance_username" {
  description = "Usuario padrao da AMI Amazon Linux para conexao SSH."
  default     = "ec2-user"
}
