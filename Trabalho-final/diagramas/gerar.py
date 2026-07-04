#!/usr/bin/env python3
"""TEMPLATE de gerador de diagramas .excalidraw para aulas.

Copie este arquivo para <pasta-do-lab>/diagramas/gerar.py, ajuste a paleta
(cor da marca) e escreva uma funcao por diagrama montando nos + conexoes.
Os assets (PNG) devem estar em <pasta-do-lab>/diagramas/assets/ — baixe com
o script baixar-assets.sh desta skill.

Embute assets OFICIAIS como PNG. Layout pensado para UX: espacamento generoso,
sem sobreposicao, setas conectando bordas, rotulos abaixo dos assets.

API da classe Diagrama:
  no(icone, rotulo, cx, cy, destaque=False) -> dict(bbox)   # icone + rotulo
  seta(a, b, rotulo=None)                                   # horizontal
  seta_vertical(a, b, rotulo=None, tracejada=False)         # cima->baixo
  seta_diagonal(a, b, rotulo=None)                          # alturas diferentes
  fan_out(origem, [destinos], rotulo=None)                  # 1 -> N
  titulo(texto, x, y); nota(texto, x, y, w, cor)
  salvar(caminho)

LICOES DE UX (aplicar SEMPRE; a cada reprovacao do revisor, ADICIONE uma nova
aqui e nunca repita o erro em diagrama seguinte):
- L1 Acentuacao correta nos rotulos visiveis (portugues correto).
- L2 Sem redundancia entre titulo e subtitulo.
- L3 Direcao da seta casa com o verbo (sujeito = origem da seta).
- L4/L7 Layout proximo do topo e equilibrado; sem vazio vertical grande.
- L5 Rotulo de aresta explicito ("invoca (evento)" > "evento").
- L6 Deixar explicito o nome da empresa/contexto ficticio (senao parece typo).
- L8 Fluxo secundario (observabilidade/erro) com seta TRACEJADA.
- L9 Rotulo de seta nunca encosta na seta nem em icone (dar respiro).
- L10 Caminho de erro: tracejado + (so ele) cor de alerta.
- L11 Fan-out: setas de UM ponto; rotulo unico no ponto de divisao.
- L12 Mesmo icone em papeis diferentes -> papel em DESTAQUE no rotulo.
- L13 Cor tem semantica: magenta/vermelho = alerta. Rotulo informativo = cinza.
"""
import base64
import json
import sys
import os

DIR = os.path.dirname(os.path.abspath(__file__))
ICONES = os.path.join(DIR, "assets")

# Paleta FIAP + AWS
FIAP_MAGENTA = "#ED0973"
TEXTO = "#1e1e1e"
CINZA = "#495057"
AWS_LARANJA = "#ED7100"

# Geometria base (em px) — folgas largas evitam sobreposicao
ICON = 80          # tamanho do icone
LABEL_H = 50       # altura reservada para o rotulo (ate 2 linhas)
LABEL_GAP = 12     # espaco entre icone e rotulo
COL_PITCH = 260    # distancia horizontal entre centros de nos (bem largo)
ROW_PITCH = 230    # distancia vertical entre linhas


def _seed(n):
    return 1000 + n * 7


def carrega_icone_datauri(nome):
    # Usamos PNG (rasterizado dos SVGs oficiais): imagens PNG embutidas sao
    # renderizadas de forma confiavel pelo canvas headless; SVG-em-SVG nao e.
    with open(os.path.join(ICONES, f"{nome}.png"), "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    return f"data:image/png;base64,{b64}"


class Diagrama:
    def __init__(self):
        self.elements = []
        self.files = {}
        self._n = 0

    def _id(self, prefix):
        self._n += 1
        return f"{prefix}{self._n}"

    def no(self, icone, rotulo, cx, cy, destaque=False):
        """Cria um no = icone centralizado em (cx,cy) + rotulo abaixo.
        Retorna o id do elemento-icone e seu bbox para ligar setas."""
        x = cx - ICON / 2
        y = cy - ICON / 2
        file_id = self._id("file")
        self.files[file_id] = {
            "mimeType": "image/png",
            "id": file_id,
            "dataURL": carrega_icone_datauri(icone),
            "created": 1,
        }
        img_id = self._id("img")
        self.elements.append({
            "id": img_id, "type": "image", "x": x, "y": y,
            "width": ICON, "height": ICON, "angle": 0,
            "strokeColor": "transparent", "backgroundColor": "transparent",
            "fillStyle": "solid", "strokeWidth": 1, "strokeStyle": "solid",
            "roughness": 0, "opacity": 100, "groupIds": [], "frameId": None,
            "roundness": None, "seed": _seed(self._n), "version": 1,
            "versionNonce": _seed(self._n), "isDeleted": False,
            "boundElements": [], "updated": 1, "link": None, "locked": False,
            "status": "saved", "fileId": file_id, "scale": [1, 1],
        })
        # rotulo abaixo do icone, largura = COL_PITCH (centralizado), 2 linhas ok
        lbl_w = COL_PITCH - 30
        lbl_x = cx - lbl_w / 2
        lbl_y = y + ICON + LABEL_GAP
        self.elements.append({
            "id": self._id("txt"), "type": "text", "x": lbl_x, "y": lbl_y,
            "width": lbl_w, "height": LABEL_H, "angle": 0,
            "strokeColor": FIAP_MAGENTA if destaque else TEXTO,
            "backgroundColor": "transparent", "fillStyle": "solid",
            "strokeWidth": 1, "strokeStyle": "solid", "roughness": 1,
            "opacity": 100, "groupIds": [], "frameId": None, "roundness": None,
            "seed": _seed(self._n), "version": 1, "versionNonce": _seed(self._n),
            "isDeleted": False, "boundElements": [], "updated": 1, "link": None,
            "locked": False, "fontSize": 16,
            "fontFamily": 2,  # 2 = fonte normal (Helvetica), legivel
            "text": rotulo, "textAlign": "center", "verticalAlign": "top",
            "containerId": None, "originalText": rotulo, "lineHeight": 1.25,
            "baseline": 14,
        })
        return {"x": x, "y": y, "w": ICON, "h": ICON, "cx": cx, "cy": cy}

    def seta(self, a, b, rotulo=None):
        """Liga o no a -> b por uma seta da borda direita de a a borda esq de b."""
        x1 = a["x"] + a["w"]
        y1 = a["cy"]
        x2 = b["x"]
        y2 = b["cy"]
        self.elements.append({
            "id": self._id("arr"), "type": "arrow", "x": x1, "y": y1,
            "width": x2 - x1, "height": y2 - y1, "angle": 0,
            "strokeColor": CINZA, "backgroundColor": "transparent",
            "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
            "roughness": 1, "opacity": 100, "groupIds": [], "frameId": None,
            "roundness": {"type": 2}, "seed": _seed(self._n), "version": 1,
            "versionNonce": _seed(self._n), "isDeleted": False,
            "boundElements": [], "updated": 1, "link": None, "locked": False,
            "points": [[0, 0], [x2 - x1, y2 - y1]],
            "lastCommittedPoint": None, "startBinding": None, "endBinding": None,
            "startArrowhead": None, "endArrowhead": "arrow",
        })
        if rotulo:
            # rotulo da seta ACIMA do meio do caminho, sem encostar nos nos
            mx = (x1 + x2) / 2
            my = (y1 + y2) / 2
            w = COL_PITCH - ICON - 20
            self.elements.append({
                "id": self._id("etxt"), "type": "text", "x": mx - w / 2,
                "y": my - 34, "width": w, "height": 22, "angle": 0,
                "strokeColor": CINZA, "backgroundColor": "transparent",
                "fillStyle": "solid", "strokeWidth": 1, "strokeStyle": "solid",
                "roughness": 1, "opacity": 100, "groupIds": [], "frameId": None,
                "roundness": None, "seed": _seed(self._n), "version": 1,
                "versionNonce": _seed(self._n), "isDeleted": False,
                "boundElements": [], "updated": 1, "link": None, "locked": False,
                "fontSize": 13, "fontFamily": 2, "text": rotulo,
                "textAlign": "center", "verticalAlign": "middle",
                "containerId": None, "originalText": rotulo, "lineHeight": 1.25,
                "baseline": 11,
            })

    def seta_vertical(self, a, b, rotulo=None, tracejada=False):
        """Liga a (em cima) -> b (embaixo) por seta vertical, borda a borda.
        tracejada=True marca fluxo secundario (ex: observabilidade)."""
        x1 = a["cx"]
        y1 = a["y"] + a["h"]
        x2 = b["cx"]
        y2 = b["y"]
        self.elements.append({
            "id": self._id("arr"), "type": "arrow", "x": x1, "y": y1,
            "width": x2 - x1, "height": y2 - y1, "angle": 0,
            "strokeColor": CINZA, "backgroundColor": "transparent",
            "fillStyle": "solid", "strokeWidth": 2,
            "strokeStyle": "dashed" if tracejada else "solid",
            "roughness": 1, "opacity": 100, "groupIds": [], "frameId": None,
            "roundness": {"type": 2}, "seed": _seed(self._n), "version": 1,
            "versionNonce": _seed(self._n), "isDeleted": False,
            "boundElements": [], "updated": 1, "link": None, "locked": False,
            "points": [[0, 0], [x2 - x1, y2 - y1]],
            "lastCommittedPoint": None, "startBinding": None, "endBinding": None,
            "startArrowhead": None, "endArrowhead": "arrow",
        })
        if rotulo:
            my = (y1 + y2) / 2
            self.elements.append({
                "id": self._id("vtxt"), "type": "text", "x": x1 + 14,
                "y": my - 11, "width": 160, "height": 22, "angle": 0,
                "strokeColor": CINZA, "backgroundColor": "transparent",
                "fillStyle": "solid", "strokeWidth": 1, "strokeStyle": "solid",
                "roughness": 1, "opacity": 100, "groupIds": [], "frameId": None,
                "roundness": None, "seed": _seed(self._n), "version": 1,
                "versionNonce": _seed(self._n), "isDeleted": False,
                "boundElements": [], "updated": 1, "link": None, "locked": False,
                "fontSize": 13, "fontFamily": 2, "text": rotulo,
                "textAlign": "left", "verticalAlign": "middle",
                "containerId": None, "originalText": rotulo, "lineHeight": 1.25,
                "baseline": 11,
            })

    def seta_diagonal(self, a, b, rotulo=None):
        """Seta da borda direita de a ate a borda esquerda de b, mesmo em
        alturas diferentes (ex: 1 stream -> 2 consumidores acima/abaixo)."""
        x1 = a["x"] + a["w"]
        y1 = a["cy"]
        x2 = b["x"]
        y2 = b["cy"]
        self.elements.append({
            "id": self._id("arr"), "type": "arrow", "x": x1, "y": y1,
            "width": x2 - x1, "height": y2 - y1, "angle": 0,
            "strokeColor": CINZA, "backgroundColor": "transparent",
            "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
            "roughness": 1, "opacity": 100, "groupIds": [], "frameId": None,
            "roundness": {"type": 2}, "seed": _seed(self._n), "version": 1,
            "versionNonce": _seed(self._n), "isDeleted": False,
            "boundElements": [], "updated": 1, "link": None, "locked": False,
            "points": [[0, 0], [x2 - x1, y2 - y1]],
            "lastCommittedPoint": None, "startBinding": None, "endBinding": None,
            "startArrowhead": None, "endArrowhead": "arrow",
        })
        if rotulo:
            # rotulo a ~35% do caminho (perto da origem), deslocado para nao
            # encostar no no de destino nem na outra diagonal
            mx = x1 + (x2 - x1) * 0.35
            my = y1 + (y2 - y1) * 0.35
            self.elements.append({
                "id": self._id("dtxt"), "type": "text", "x": mx - 70,
                "y": my - 26, "width": 140, "height": 22, "angle": 0,
                "strokeColor": CINZA, "backgroundColor": "transparent",
                "fillStyle": "solid", "strokeWidth": 1, "strokeStyle": "solid",
                "roughness": 1, "opacity": 100, "groupIds": [], "frameId": None,
                "roundness": None, "seed": _seed(self._n), "version": 1,
                "versionNonce": _seed(self._n), "isDeleted": False,
                "boundElements": [], "updated": 1, "link": None, "locked": False,
                "fontSize": 13, "fontFamily": 2, "text": rotulo,
                "textAlign": "center", "verticalAlign": "middle",
                "containerId": None, "originalText": rotulo, "lineHeight": 1.25,
                "baseline": 11,
            })

    def fan_out(self, origem, destinos, rotulo=None):
        """1 origem -> N destinos (L11). Todas as setas partem do MESMO ponto
        (borda direita da origem); rotulo unico colocado nesse ponto."""
        px = origem["x"] + origem["w"]
        py = origem["cy"]
        for b in destinos:
            x2 = b["x"]
            y2 = b["cy"]
            self.elements.append({
                "id": self._id("arr"), "type": "arrow", "x": px, "y": py,
                "width": x2 - px, "height": y2 - py, "angle": 0,
                "strokeColor": CINZA, "backgroundColor": "transparent",
                "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
                "roughness": 1, "opacity": 100, "groupIds": [], "frameId": None,
                "roundness": {"type": 2}, "seed": _seed(self._n), "version": 1,
                "versionNonce": _seed(self._n), "isDeleted": False,
                "boundElements": [], "updated": 1, "link": None, "locked": False,
                "points": [[0, 0], [x2 - px, y2 - py]],
                "lastCommittedPoint": None, "startBinding": None,
                "endBinding": None, "startArrowhead": None,
                "endArrowhead": "arrow",
            })
        if rotulo:
            # L13: rotulo informativo = cinza (magenta seria lido como alerta).
            # L9: respiro maior do ponto de divisao para nao colar na seta.
            self.elements.append({
                "id": self._id("fotxt"), "type": "text", "x": px + 22,
                "y": py - 42, "width": 200, "height": 22, "angle": 0,
                "strokeColor": CINZA, "backgroundColor": "transparent",
                "fillStyle": "solid", "strokeWidth": 1, "strokeStyle": "solid",
                "roughness": 1, "opacity": 100, "groupIds": [], "frameId": None,
                "roundness": None, "seed": _seed(self._n), "version": 1,
                "versionNonce": _seed(self._n), "isDeleted": False,
                "boundElements": [], "updated": 1, "link": None, "locked": False,
                "fontSize": 13, "fontFamily": 2, "text": rotulo,
                "textAlign": "left", "verticalAlign": "middle",
                "containerId": None, "originalText": rotulo, "lineHeight": 1.25,
                "baseline": 11,
            })

    def caixa(self, x, y, w, h, titulo=None, cor=CINZA, bg="transparent",
              tracejada=False, titulo_cor=None):
        """Retangulo container (agrupador). Titulo opcional no topo interno."""
        self.elements.append({
            "id": self._id("rect"), "type": "rectangle", "x": x, "y": y,
            "width": w, "height": h, "angle": 0, "strokeColor": cor,
            "backgroundColor": bg, "fillStyle": "solid", "strokeWidth": 2,
            "strokeStyle": "dashed" if tracejada else "solid", "roughness": 1,
            "opacity": 100, "groupIds": [], "frameId": None,
            "roundness": {"type": 3}, "seed": _seed(self._n), "version": 1,
            "versionNonce": _seed(self._n), "isDeleted": False,
            "boundElements": [], "updated": 1, "link": None, "locked": False,
        })
        if titulo:
            self.elements.append({
                "id": self._id("btit"), "type": "text", "x": x + 16,
                "y": y + 12, "width": w - 32, "height": 22, "angle": 0,
                "strokeColor": titulo_cor or cor,
                "backgroundColor": "transparent", "fillStyle": "solid",
                "strokeWidth": 1, "strokeStyle": "solid", "roughness": 1,
                "opacity": 100, "groupIds": [], "frameId": None,
                "roundness": None, "seed": _seed(self._n), "version": 1,
                "versionNonce": _seed(self._n), "isDeleted": False,
                "boundElements": [], "updated": 1, "link": None,
                "locked": False, "fontSize": 15, "fontFamily": 2,
                "text": titulo, "textAlign": "left", "verticalAlign": "top",
                "containerId": None, "originalText": titulo, "lineHeight": 1.25,
                "baseline": 12,
            })
        return {"x": x, "y": y, "w": w, "h": h, "cx": x + w / 2,
                "cy": y + h / 2}

    def stage(self, cx, cy, numero, nome, sub, cor=AWS_LARANJA):
        """Mini-caixa de um stage do pipeline (numero + nome + subtitulo)."""
        w, h = 178, 100
        x, y = cx - w / 2, cy - h / 2
        self.elements.append({
            "id": self._id("srect"), "type": "rectangle", "x": x, "y": y,
            "width": w, "height": h, "angle": 0, "strokeColor": cor,
            "backgroundColor": "#fff4ec", "fillStyle": "solid",
            "strokeWidth": 2, "strokeStyle": "solid", "roughness": 1,
            "opacity": 100, "groupIds": [], "frameId": None,
            "roundness": {"type": 3}, "seed": _seed(self._n), "version": 1,
            "versionNonce": _seed(self._n), "isDeleted": False,
            "boundElements": [], "updated": 1, "link": None, "locked": False,
        })
        self.elements.append({
            "id": self._id("stit"), "type": "text", "x": x, "y": y + 16,
            "width": w, "height": 26, "angle": 0, "strokeColor": TEXTO,
            "backgroundColor": "transparent", "fillStyle": "solid",
            "strokeWidth": 1, "strokeStyle": "solid", "roughness": 1,
            "opacity": 100, "groupIds": [], "frameId": None, "roundness": None,
            "seed": _seed(self._n), "version": 1, "versionNonce": _seed(self._n),
            "isDeleted": False, "boundElements": [], "updated": 1, "link": None,
            "locked": False, "fontSize": 18, "fontFamily": 2,
            "text": f"{numero}. {nome}", "textAlign": "center",
            "verticalAlign": "top", "containerId": None,
            "originalText": f"{numero}. {nome}", "lineHeight": 1.25,
            "baseline": 15,
        })
        self.elements.append({
            "id": self._id("ssub"), "type": "text", "x": x + 8, "y": y + 48,
            "width": w - 16, "height": 44, "angle": 0, "strokeColor": CINZA,
            "backgroundColor": "transparent", "fillStyle": "solid",
            "strokeWidth": 1, "strokeStyle": "solid", "roughness": 1,
            "opacity": 100, "groupIds": [], "frameId": None, "roundness": None,
            "seed": _seed(self._n), "version": 1, "versionNonce": _seed(self._n),
            "isDeleted": False, "boundElements": [], "updated": 1, "link": None,
            "locked": False, "fontSize": 12, "fontFamily": 2, "text": sub,
            "textAlign": "center", "verticalAlign": "top", "containerId": None,
            "originalText": sub, "lineHeight": 1.2, "baseline": 10,
        })
        return {"x": x, "y": y, "w": w, "h": h, "cx": cx, "cy": cy}

    def titulo(self, texto, x, y, w=900):
        self.elements.append({
            "id": self._id("title"), "type": "text", "x": x, "y": y,
            "width": w, "height": 30, "angle": 0, "strokeColor": FIAP_MAGENTA,
            "backgroundColor": "transparent", "fillStyle": "solid",
            "strokeWidth": 1, "strokeStyle": "solid", "roughness": 1,
            "opacity": 100, "groupIds": [], "frameId": None, "roundness": None,
            "seed": _seed(self._n), "version": 1, "versionNonce": _seed(self._n),
            "isDeleted": False, "boundElements": [], "updated": 1, "link": None,
            "locked": False, "fontSize": 22, "fontFamily": 2, "text": texto,
            "textAlign": "left", "verticalAlign": "top", "containerId": None,
            "originalText": texto, "lineHeight": 1.25, "baseline": 19,
        })

    def nota(self, texto, x, y, w=900, cor=CINZA):
        self.elements.append({
            "id": self._id("nota"), "type": "text", "x": x, "y": y,
            "width": w, "height": 22, "angle": 0, "strokeColor": cor,
            "backgroundColor": "transparent", "fillStyle": "solid",
            "strokeWidth": 1, "strokeStyle": "solid", "roughness": 1,
            "opacity": 100, "groupIds": [], "frameId": None, "roundness": None,
            "seed": _seed(self._n), "version": 1, "versionNonce": _seed(self._n),
            "isDeleted": False, "boundElements": [], "updated": 1, "link": None,
            "locked": False, "fontSize": 14, "fontFamily": 2, "text": texto,
            "textAlign": "left", "verticalAlign": "top", "containerId": None,
            "originalText": texto, "lineHeight": 1.25, "baseline": 12,
        })

    def salvar(self, caminho):
        doc = {
            "type": "excalidraw", "version": 2, "source": "fiap-gerador",
            "elements": self.elements,
            "appState": {"gridSize": None, "viewBackgroundColor": "#ffffff"},
            "files": self.files,
        }
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False, indent=2)
        print(f"gerado: {caminho} ({len(self.elements)} elementos)")




# ---------------------------------------------------------------------------
# EXEMPLO — apague e escreva os seus diagramas (uma funcao por diagrama).
# Pre-requisito: diagramas/assets/{apigateway,lambda,s3}.png  (baixar-assets.sh)
# ---------------------------------------------------------------------------

VPC_ROXO = "#7D2AE8"      # categoria Networking (VPC)
PIPE_AZUL = "#3B5BDB"     # borda do bloco de pipeline (informativo, nao alerta)


def arquitetura_final():
    d = Diagrama()
    d.titulo("Vortex Mobility - Trabalho Final: um git push provisiona a infra na AWS",
             60, 30, w=1500)
    d.nota("Empresa fictícia Vortex Mobility. O push na branch master valida, revisa a segurança (Checkov) "
           "e provisiona a infraestrutura sozinho - sem credencial da AWS guardada no GitLab.",
           60, 66, w=1600)

    # --- Origem: engenheiro -> repositorio GitLab ---
    eng = d.no("user", "Platform\nEngineer", 120, 300)
    git = d.no("gitlab", "Repositório GitLab\nprojeto Vortex (master)", 380, 300)
    d.seta(eng, git, "git push")

    # --- Bloco do Pipeline (roda no runner) ---
    box_pipe = d.caixa(560, 175, 640, 250,
                       titulo="Pipeline GitLab CI/CD",
                       cor=PIPE_AZUL, bg="#eef2ff", titulo_cor=PIPE_AZUL)
    s_val = d.stage(660, 300, "1", "validar", "terraform\nfmt + validate")
    s_rev = d.stage(870, 300, "2", "revisar", "plan + Checkov\n(gate de segurança)")
    s_apl = d.stage(1090, 300, "3", "aplicar", "terraform\napply")
    d.seta(s_val, s_rev)
    d.seta(s_rev, s_apl)
    # gitlab dispara o pipeline (entra na borda esquerda do bloco)
    d.seta(git, {"x": 560, "y": 175, "w": 0, "h": 250, "cx": 560, "cy": 300},
           "dispara")

    # --- Runner (EC2) + LabRole, abaixo do pipeline ---
    runner = d.no("ec2", "GitLab Runner\nEC2 (Módulo 02)", 700, 560)
    role = d.no("iam", "LabRole\n(IAM instance profile)", 980, 560)
    d.seta_vertical(box_pipe, runner, "roda no runner", tracejada=True)
    d.seta(runner, role, "autentica na AWS")

    # --- Terraform (dentro do stage aplicar) ---
    tf = d.no("terraform", "Terraform\nexecuta o apply", 1360, 300)
    d.seta(s_apl, tf, "executa")

    # --- Estado remoto no S3 (fluxo secundario, tracejado) ---
    s3 = d.no("s3", "Amazon S3\nestado remoto\nbase-config-<RM>", 1360, 560)
    d.seta_vertical(tf, s3, "lê/grava state", tracejada=True)

    # --- VPC fiap-lab com ALB -> N x EC2 ---
    box_vpc = d.caixa(1520, 150, 470, 520,
                      titulo="VPC fiap-lab - subnets públicas",
                      cor=VPC_ROXO, bg="#f7f0ff", titulo_cor=VPC_ROXO)
    d.nota("workspaces: dev = 1 nó  |  prod = 3 nós", 1540, 182, w=440,
           cor=VPC_ROXO)
    alb = d.no("elb", "Application\nLoad Balancer", 1620, 340)
    d.seta(tf, box_vpc, "provisiona")

    # Security Group envolvendo os nos nginx.
    # Nos subidos e caixa estendida ate y=660 (dentro da VPC, cujo fundo e 670)
    # para que os 3 rotulos fiquem inteiros dentro da caixa, com folga do
    # tracejado ao rotulo do 3o no (L9: tracejado nao cruza texto).
    d.caixa(1788, 214, 194, 446, titulo="Security Group",
            cor=CINZA, bg="transparent", tracejada=True)
    n1 = d.no("ec2", "EC2 nginx\n(nó 1)", 1885, 300)
    n2 = d.no("ec2", "EC2 nginx\n(nó 2)", 1885, 420)
    n3 = d.no("ec2", "EC2 nginx\n(nó 3)", 1885, 540)
    d.fan_out(alb, [n1, n2, n3], "Target Group")

    # --- Resultado: aplicacao no ar pelo DNS do ALB ---
    res = d.caixa(1360, 710, 520, 62, cor=TEXTO, bg="#f1f3f5")
    d.nota("Aplicação Vortex no ar - acessível pelo DNS do ALB",
           1382, 730, w=490, cor=TEXTO)
    # L3: quem serve o trafego e o ALB -> ancora a seta na base do ALB
    # (logo abaixo do rotulo do ALB, em x=1620) e desce reto ate a caixa de
    # resultado, sem cruzar o rotulo do proprio ALB nem os nos nginx.
    alb_base = {"x": 1580, "y": 442, "w": 80, "h": 0, "cx": 1620, "cy": 442}
    d.seta_vertical(alb_base, res, "serve tráfego")

    d.salvar(os.path.join(DIR, "arquitetura-final.excalidraw"))


if __name__ == "__main__":
    arquitetura_final()
