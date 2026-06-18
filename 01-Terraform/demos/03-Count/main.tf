# Provider declarado uma vez na raiz desta demo.
provider "aws" {
  region = var.aws_region
}

variable "project" {
  default = "fiap-lab"
}

# A rede (VPC + subnets publicas) ja foi criada na demo 02-Modules. Aqui apenas
# descobrimos esses recursos por tag, em vez de recria-los.
data "aws_vpc" "vpc" {
  tags = {
    Name = var.project
  }
}

data "aws_subnets" "all" {
  filter {
    name   = "tag:Tier"
    values = ["Public"]
  }
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.vpc.id]
  }
}

data "aws_subnet" "public" {
  for_each = toset(data.aws_subnets.all.ids)
  id       = each.value
}

# Escolhe aleatoriamente uma subnet publica para hospedar as instancias da frota.
resource "random_shuffle" "random_subnet" {
  input        = [for s in data.aws_subnet.public : s.id]
  result_count = 1
}

# Classic Load Balancer (aws_elb): distribui o trafego HTTP entre as instancias.
resource "aws_elb" "web" {
  name = "terraform-example-elb"

  subnets         = data.aws_subnets.all.ids
  security_groups = [aws_security_group.allow-ssh.id]

  listener {
    instance_port     = 80
    instance_protocol = "http"
    lb_port           = 80
    lb_protocol       = "http"
  }

  health_check {
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 3
    target              = "HTTP:80/"
    interval            = 6
  }

  # As instancias da frota sao registradas automaticamente no ELB.
  instances = aws_instance.web[*].id
}

# A frota de servidores. count = 2 cria duas EC2 identicas; alterar esse numero
# escala a frota para cima ou para baixo num unico apply.
resource "aws_instance" "web" {
  instance_type = "t3.micro"
  ami           = data.aws_ami.amazon_linux.id

  count = 2

  subnet_id              = random_shuffle.random_subnet.result[0]
  vpc_security_group_ids = [aws_security_group.allow-ssh.id]
  key_name               = var.key_name

  provisioner "file" {
    source      = "script.sh"
    destination = "/tmp/script.sh"
  }

  provisioner "remote-exec" {
    inline = [
      "chmod +x /tmp/script.sh",
      "sudo /tmp/script.sh",
    ]
  }

  connection {
    user        = var.instance_username
    private_key = file(var.path_to_key)
    host        = self.public_dns
  }

  tags = {
    Name = format("nginx-%03d", count.index + 1)
  }
}
