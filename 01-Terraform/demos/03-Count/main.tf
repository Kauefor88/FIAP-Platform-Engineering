# Provider declarado uma vez na raiz desta demo.
provider "aws" {
  region = var.aws_region

  # default_tags: tags de governanca aplicadas a todos os recursos do provider.
  default_tags {
    tags = {
      Project   = "vortex-mobility"
      ManagedBy = "terraform"
      Lab       = "01-terraform"
    }
  }
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

# Nem toda Availability Zone oferta todos os tipos de instancia. Em us-east-1, por
# exemplo, a AZ us-east-1e NAO oferta t3.micro. Descobrimos dinamicamente em quais
# AZs o tipo escolhido existe e usamos apenas as subnets dessas AZs.
data "aws_ec2_instance_type_offerings" "supported" {
  filter {
    name   = "instance-type"
    values = [var.instance_type]
  }
  location_type = "availability-zone"
}

locals {
  # Subnets publicas em AZs que ofertam o tipo de instancia escolhido, ordenadas
  # para um resultado deterministico (todo aluno obtem a mesma distribuicao).
  eligible_subnet_ids = sort([
    for s in data.aws_subnet.public : s.id
    if contains(toset(data.aws_ec2_instance_type_offerings.supported.locations), s.availability_zone)
  ])
}

# Application Load Balancer (aws_lb). Diferente do Classic ELB, o ALB opera na
# camada 7 (HTTP) e EXIGE subnets em pelo menos 2 Availability Zones — por isso
# entregamos a ele todas as subnets elegiveis, nao apenas uma.
resource "aws_lb" "web" {
  name               = "vortex-frota-alb"
  load_balancer_type = "application"
  subnets            = local.eligible_subnet_ids
  security_groups    = [aws_security_group.allow-ssh.id]
}

# O target group agrupa os alvos (as EC2) e define como verificar a saude deles.
resource "aws_lb_target_group" "web" {
  name     = "vortex-frota-tg"
  port     = 80
  protocol = "HTTP"
  vpc_id   = data.aws_vpc.vpc.id

  health_check {
    path                = "/"
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 3
    interval            = 6
  }
}

# O listener recebe o trafego HTTP na porta 80 e encaminha para o target group.
resource "aws_lb_listener" "web" {
  load_balancer_arn = aws_lb.web.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.web.arn
  }
}

# A frota de servidores. count = 2 cria duas EC2 identicas; alterar esse numero
# escala a frota para cima ou para baixo num unico apply. As instancias sao
# distribuidas entre as subnets elegiveis (AZs distintas) com element().
resource "aws_instance" "web" {
  count = 2

  instance_type          = var.instance_type
  ami                    = data.aws_ami.amazon_linux.id
  subnet_id              = element(local.eligible_subnet_ids, count.index)
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

# Registra cada instancia da frota no target group do ALB.
resource "aws_lb_target_group_attachment" "web" {
  count            = length(aws_instance.web)
  target_group_arn = aws_lb_target_group.web.arn
  target_id        = aws_instance.web[count.index].id
  port             = 80
}
