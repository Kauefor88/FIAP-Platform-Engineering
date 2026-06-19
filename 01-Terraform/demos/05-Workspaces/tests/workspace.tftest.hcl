# Teste nativo do Terraform (arquivo .tftest.hcl, TF 1.6+). Roda com 'terraform test'.
# Aqui validamos, SEM criar infra de verdade (command = plan), que o mapa de
# contexto entrega o tipo de instancia correto para o workspace atual.
#
# O 'terraform test' executa no workspace "default", cujo mapa define t3.micro.
# Este teste falha se alguem quebrar o mapa de contexto (ex: tipo invalido no
# Learner Lab, ou remover a entrada default).

run "default_usa_t3_micro" {
  command = plan

  assert {
    condition     = output.instance_type == "t3.micro"
    error_message = "No workspace default, o instance_type deveria ser t3.micro."
  }
}
