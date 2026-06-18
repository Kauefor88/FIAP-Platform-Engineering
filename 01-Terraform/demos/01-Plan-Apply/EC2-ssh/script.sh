#!/bin/bash

# Amazon Linux 2023 usa dnf e entrega nginx direto nos repositorios padrao
# (o antigo amazon-linux-extras nao existe mais nessa versao).
sudo dnf update -y
sudo dnf install -y nginx

# Garante que o nginx suba agora e tambem apos reboot.
sudo systemctl enable --now nginx
