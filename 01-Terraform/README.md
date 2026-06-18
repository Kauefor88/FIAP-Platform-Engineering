# 01 — Terraform / Infraestrutura como Código

> **Mês 1 na Vortex Mobility.**
> Você acaba de entrar como Platform Engineer na **Vortex Mobility**, uma startup brasileira de micromobilidade (e-scooters e e-bikes) que está escalando de 3 para 30 cidades. No seu primeiro dia, **Helena Marques**, Head de Engenharia de Plataforma, te chama numa sala de reunião:
>
> > *— "A infraestrutura inteira da Vortex foi criada na mão, clicando no console da AWS. Funciona, mas ninguém sabe recriar. Se a conta cair, ou se um estagiário apagar uma VPC, a gente leva dias para voltar — e nem temos certeza de que volta igual. Quero toda a nossa infraestrutura como **código versionado**: que eu consiga destruir e recriar idêntica, num comando, com histórico de quem mudou o quê."*
>
> Essa é a sua missão deste mês. Você vai aprender Terraform construindo, passo a passo, a base que a Vortex precisa.

Este módulo é a porta de entrada da disciplina de Platform Engineering. São **5 demos guiadas em sala** + **2 exercícios** que você faz sozinho para fixar. Cada demo é um passo concreto da jornada da Vortex: sair do "clicado no console" para o "tudo em código, reproduzível e auditável".

A pergunta-âncora que carregamos por todo o módulo (e por toda a disciplina) é simples: **quanto tempo a Vortex leva para recriar toda a sua infraestrutura do zero, de forma confiável?** No começo deste módulo a resposta é "dias, na mão, e ninguém tem certeza". No final, é "um `terraform apply`".

## A jornada das 5 demos

As demos contam uma história em sequência — cada uma resolve uma dor que a anterior deixou exposta:

| # | Demo | O que você faz | A dor que resolve | Tempo |
|---|------|----------------|-------------------|-------|
| **01.1** | **[Plan e Apply](demos/01-Plan-Apply/README.md)** | Provisiona a primeira EC2 da Vortex via código: `init` → `plan` → `apply` → `destroy`. Depois sobe um servidor Nginx com provisioner. | "Como eu descrevo **um** recurso em código em vez de clicar?" | ~30 min |
| **01.2** | **[Módulos](demos/02-Modules/README.md)** | Componentiza a rede da Vortex em módulos reutilizáveis: uma VPC com subnets públicas em todas as AZs + route tables para o Internet Gateway. | "Como eu **reutilizo** e organizo blocos de rede sem copiar e colar?" | ~25 min |
| **01.3** | **[Count](demos/03-Count/README.md)** | Escala a frota de servidores web da Vortex atrás de um Classic Load Balancer só mudando um número (`count`). | "Como eu **escalo** de 2 para 10 servidores sem reescrever tudo?" | ~30 min |
| **01.4** | **[State remoto](demos/04-State/README.md)** | Move o estado do Terraform para um bucket S3 compartilhado, para o time inteiro colaborar sem corromper o estado. | "Como o **time todo** trabalha na mesma infra sem se atropelar?" | ~20 min |
| **01.5** | **[Workspaces](demos/05-Workspaces/README.md)** | Isola ambientes `dev` e `prod` com o mesmo código, usando workspaces e um estado por ambiente. | "Como eu separo **dev de prod** sem duplicar o código?" | ~25 min |

> [!TIP]
> Faça as demos na ordem. Cada uma assume conceitos da anterior, e a demo 01.3 (Count) usa a rede criada na demo 01.2 (Módulos).

## Os 2 exercícios

Para fixar, dois exercícios curtos que você resolve sozinho (a proposta é sua: escrever o HCL do zero a partir da documentação oficial):

| Exercício | O que você pratica | Liga-se à demo |
|-----------|--------------------|----------------|
| **[Count com SQS](exercicios/count/README.md)** | Criar N filas SQS parametrizando com `variable` + `count`. | 01.3 |
| **[State e Workspace com EC2](exercicios/State-e-workspace/README.md)** | Data source de AMI dinâmica + 2 EC2 por workspace + estado remoto no S3. | 01.4 e 01.5 |

## Principais pontos de aprendizagem do módulo

- o ciclo de vida do Terraform: `init` → `plan` → `apply` → `destroy`
- como descrever recursos AWS declarativamente em HCL
- modularização e reúso de configuração
- escalar recursos com `count`
- estado remoto compartilhado (backend S3) para trabalho em equipe
- isolamento de ambientes com workspaces

## Pré-requisitos do módulo

Antes de começar **qualquer** demo:

- [ ] Codespaces da disciplina aberto com terminal funcional ([setup inicial](../00-create-codespaces/README.md))
- [ ] Credenciais AWS do Academy atualizadas no Codespaces
- [ ] Terraform instalado (o devcontainer já entrega) — valide com `terraform -version`
- [ ] Par de chaves `vockey` disponível em `/home/vscode/.ssh/vockey.pem` (criado no setup)

Valide rapidamente:

```bash
aws sts get-caller-identity && terraform -version
```

Se retornar o JSON com seu `Account`/`Arn` e a versão do Terraform (1.x), você está pronto.

## Modernização do código (2026)

Todo o HCL deste módulo foi atualizado para o Terraform moderno:

- `required_version >= 1.6` e provider `hashicorp/aws ~> 6.0` declarados em cada raiz (`versions.tf`)
- sem interpolação legada do estilo 0.11 (`"${var.x}"` virou `var.x`)
- AMIs descobertas dinamicamente via `data "aws_ami"` (Amazon Linux 2023), em vez de IDs fixos que expiram

## Custo do módulo

As demos criam recursos pagos por hora (EC2, ELB). São baratos e efêmeros, mas **só se você destruir ao final de cada lab**.

| Recurso | Custo aproximado | Observação |
|---------|------------------|------------|
| EC2 `t3.micro` | ~$0,01/h cada | a demo Count chega a rodar 3 |
| Classic ELB | ~$0,025/h | só na demo Count |
| VPC, subnets, route tables, SQS | grátis ou desprezível | — |

> [!CAUTION]
> **Sempre rode `terraform destroy -auto-approve` ao final de cada demo.** Esquecer uma EC2 + ELB ligados por um dia consome facilmente alguns dólares do orçamento do Learner Lab. Cada README termina lembrando o comando.

## Próximo módulo

Depois de concluir as 5 demos e os 2 exercícios, prossiga para:

**[02 — Ansible](../02-Ansible/README.md)** — onde, no Mês 2, Helena pede para automatizar a configuração de servidores (um GitLab Runner próprio) com Ansible, deixando o que era manual e não-repetível em algo idempotente e versionado.
