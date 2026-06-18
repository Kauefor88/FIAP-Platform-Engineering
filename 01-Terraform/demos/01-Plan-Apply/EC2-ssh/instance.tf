resource "aws_instance" "example" {
  ami           = data.aws_ami.amazon_linux.id
  instance_type = "t3.micro"
  key_name      = var.key_name

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
}
