"""
Scanner de Documentos — Retângulo Fixo
========================================
O usuário posiciona o documento dentro do retângulo exibido na tela.
Ao pressionar ESPAÇO, a região dentro do retângulo é recortada, processada
e salva como PDF ou imagem PNG.

Requisitos:
    pip install opencv-python numpy Pillow img2pdf - Instalar bibliotecas

Controles:
    [ESPAÇO]  → Capturar o documento dentro do retângulo
    [S]       → Salvar última captura como PDF
    [I]       → Salvar última captura como PNG
    [M]       → Alternar modo de imagem (adaptativo / cinza / colorido)
    [Q/ESC]   → Sair
"""

# ─── Importações ──────────────────────────────────────────────────────────────

import cv2        # Biblioteca principal de visão computacional (captura e desenho)
import numpy as np  # Manipulação de arrays e matrizes de pixels
import img2pdf    # Conversão de imagens para PDF sem perda de qualidade
import os         # Operações de sistema de arquivos (remover arquivos temporários)
import time       # Controle de tempo para contagem regressiva
from pathlib import Path      # Manipulação de caminhos de arquivos de forma moderna
from datetime import datetime # Geração de timestamps para nomear arquivos salvos

# ─── Importação opcional do OCR ───────────────────────────────────────────────

# Tenta importar o EasyOCR. Se não estiver instalado, o programa continua
# funcionando normalmente, apenas sem a funcionalidade de reconhecimento de texto.
try:
    import easyocr
    EASYOCR_DISPONIVEL = True
except ImportError:
    EASYOCR_DISPONIVEL = False

# ─── Configurações globais ────────────────────────────────────────────────────

# Pasta onde todos os arquivos escaneados (PDF, PNG, TXT) serão salvos.
PASTA_SAIDA = Path("documentos_escaneados")
# O método mkdir(exist_ok=True) cria a pasta se ela ainda não existir.
PASTA_SAIDA.mkdir(exist_ok=True)

# Define o tamanho do retângulo guia como proporção do frame da câmera.
# Ajuste esses valores para tornar o retângulo maior (menor margem) ou menor (maior margem).
MARGEM_X = 0.08
MARGEM_Y = 0.12

# Definição das cores usadas na interface visual.
COR_RETANGULO = (0, 242, 214)   # Cor do retângulo guia em estado normal
COR_PRONTO    = (0, 242, 214)   # Cor do retângulo durante a contagem regressiva
COR_CANTO     = (0, 242, 214)   # Cor dos círculos nos 4 cantos do retângulo
COR_TEXTO     = (255, 255, 255) # Cor do texto exibido na interface 
COR_SOMBRA    = (0, 0, 0)       # Cor da sombra por trás do texto

# Tamanho em pixels das marcações de canto do retângulo guia.
TAMANHO_CANTO   = 28

# Espessura das linhas tracejadas das bordas do retângulo.
ESPESSURA_LINHA = 2


# ─── Funções utilitárias ──────────────────────────────────────────────────────

def gerar_nome_arquivo(extensao: str) -> Path:
    """
    Gera um nome de arquivo único baseado na data e hora atual.
    Exemplo de saída: documentos_escaneados/scan_<data>_<hora>.pdf

    Parâmetros:
        extensao: string com a extensão desejada ('pdf', 'png', 'txt')

    Retorna:
        Objeto Path com o caminho completo do arquivo a ser criado.
    """
    # Formata a data/hora atual como string no formato AAAAMMDD_HHMMSS
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return PASTA_SAIDA / f"scan_{ts}.{extensao}"


def salvar_pdf(imagem: np.ndarray, caminho: Path) -> bool:
    """
    Salva uma imagem numpy como arquivo PDF usando a biblioteca img2pdf.

    Processo interno:
        1. Salva a imagem temporariamente como PNG no disco
        2. Converte esse PNG para PDF usando img2pdf
        3. Remove o arquivo PNG temporário

    Parâmetros:
        imagem:  Array numpy com os pixels da imagem a ser salva
        caminho: Caminho completo onde o PDF será criado

    Retorna:
        True se o PDF foi salvo com sucesso, False em caso de erro.
    """
    try:
        # Caminho do arquivo temporário PNG que será convertido para PDF
        temp = str(PASTA_SAIDA / "_temp.png")

        # Salva a imagem numpy como PNG no disco
        cv2.imwrite(temp, imagem)

        # Abre o arquivo PDF para escrita em modo binário e converte o PNG
        with open(caminho, "wb") as f:
            f.write(img2pdf.convert(temp))

        # Remove o arquivo temporário após a conversão
        os.remove(temp)

        print(f"[OK] PDF salvo: {caminho}")
        return True
    except Exception as e:
        print(f"[ERRO] {e}")
        return False


def salvar_imagem(imagem: np.ndarray, caminho: Path) -> bool:
    """
    Salva uma imagem numpy diretamente como arquivo PNG.

    Parâmetros:
        imagem:  Array numpy com os pixels da imagem
        caminho: Caminho completo onde o PNG será criado

    Retorna:
        True se a imagem foi salva com sucesso, False em caso de erro.
    """
    try:
        cv2.imwrite(str(caminho), imagem)
        print(f"[OK] Imagem salva: {caminho}")
        return True
    except Exception as e:
        print(f"[ERRO] {e}")
        return False


def aprimorar(imagem: np.ndarray, modo: str = "adaptativo") -> np.ndarray:
    """
    Aplica pós-processamento na imagem capturada para simular o efeito de scanner.

    Modos disponíveis:
        'adaptativo' → Converte para preto e branco com binarização inteligente.
                       O threshold adaptativo analisa regiões locais da imagem,
                       lidando bem com iluminação desigual (ex: sombras no documento).
                       Ideal para documentos com texto.

        'cinza'      → Converte para escala de cinza sem binarização.
                       Preserva os tons intermediários, útil para documentos com fotos.

        'colorido'   → Retorna a imagem original sem qualquer processamento.
                       Útil quando se quer preservar cores (ex: formulários coloridos).

    Parâmetros:
        imagem: Array numpy BGR da imagem recortada do retângulo
        modo:   String indicando o modo de processamento desejado

    Retorna:
        Array numpy com a imagem processada.
    """
    # Modo Adaptativo
    if modo == "adaptativo":
        # Converte BGR para escala de cinza (pré-requisito do threshold)
        cinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)

        # Aplica threshold adaptativo gaussiano:
        # - blockSize=11: analisa blocos de 11x11 pixels para calcular o limiar local
        # - C=2: subtrai 2 do valor médio calculado para refinar o limiar
        return cv2.adaptiveThreshold(
            cinza, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            blockSize=11, C=2
        )
    # Modo Cinza
    elif modo == "cinza":
        # Apenas converte para escala de cinza
        return cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
    # Modo Colorido
    else:
        # Modo colorido: retorna a imagem sem alteração
        return imagem


# ─── Retângulo guia ───────────────────────────────────────────────────────────

def calcular_retangulo(frame: np.ndarray):
    """
    Calcula as coordenadas absolutas (em pixels) do retângulo guia,
    sempre centralizado no frame e proporcional ao seu tamanho.

    O retângulo é recalculado a cada frame para se adaptar caso a
    resolução da câmera mude dinamicamente.

    Parâmetros:
        frame: Array numpy do frame atual da câmera

    Retorna:
        Tupla (x1, y1, x2, y2) com os cantos superior-esquerdo e inferior-direito.
    """
    # Extrai altura e largura do frame
    h, w = frame.shape[:2]  

    # Calcula os cantos aplicando as margens proporcionais
    x1 = int(w * MARGEM_X)          # Borda esquerda
    y1 = int(h * MARGEM_Y)          # Borda superior
    x2 = int(w * (1 - MARGEM_X))    # Borda direita
    y2 = int(h * (1 - MARGEM_Y))    # Borda inferior

    return x1, y1, x2, y2


def desenhar_retangulo_guia(frame: np.ndarray, x1: int, y1: int,
                             x2: int, y2: int, pronto: bool = False):
    """
    Desenha o retângulo guia estilizado sobre o frame da câmera.
    O retângulo é composto por bordas tracejadas e marcações nos 4 cantos.

    Efeitos visuais aplicados:
        - Overlay escuro fora do retângulo: destaca a área de captura
        - Bordas tracejadas: indicam os limites do documento
        - Marcações de canto em L: reforçam visualmente os 4 cantos
        - Círculos nos vértices: pontos de referência precisos

    Parâmetros:
        frame:  Array numpy do frame que será modificado visualmente
        x1, y1: Coordenadas do canto superior-esquerdo do retângulo
        x2, y2: Coordenadas do canto inferior-direito do retângulo
        pronto: Se True, usa a cor COR_PRONTO (verde) indicando captura iminente
    """
    # Seleciona a cor baseada no estado da contagem regressiva
    cor = COR_PRONTO if pronto else COR_RETANGULO
    t = TAMANHO_CANTO    # Comprimento das marcações em L nos cantos
    e = ESPESSURA_LINHA  # Espessura das linhas

    # ── Overlay escurecido fora da área do retângulo ─────────────
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (frame.shape[1], frame.shape[0]), (0, 0, 0), -1)
    cv2.rectangle(overlay, (x1, y1), (x2, y2), (0, 0, 0), -1)  # "limpa" a área interna

    # O peso 0.45 no overlay escuro cria a sombra semitransparente
    cv2.addWeighted(overlay, 0.45, frame, 0.55, 0, frame)

    # ── Bordas tracejadas ─────────────────────────────────────────
    _desenhar_borda_tracejada(frame, x1, y1, x2, y2, cor, e)

    # ── Marcações de canto em formato "L" ────────────────────────
    cantos = [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]

    # Direções das linhas para cada canto
    direcoes = [
        (+t, 0, 0, +t),   # Topo-esquerda: linha vai para direita (+x) e para baixo (+y)
        (-t, 0, 0, +t),   # Topo-direita:  linha vai para esquerda (-x) e para baixo (+y)
        (-t, 0, 0, -t),   # Base-direita:  linha vai para esquerda (-x) e para cima (-y)
        (+t, 0, 0, -t),   # Base-esquerda: linha vai para direita (+x) e para cima (-y)
    ]

    # Cantos são ligeiramente mais grossos que as bordas
    grossura_canto = e + 2  

    for (cx, cy), (dx, _, _, dy) in zip(cantos, direcoes):
        # Linha horizontal do L (vai na direção dx)
        cv2.line(frame, (cx, cy), (cx + dx, cy), cor, grossura_canto, cv2.LINE_AA)
        # Linha vertical do L (vai na direção dy)
        cv2.line(frame, (cx, cy), (cx, cy + dy), cor, grossura_canto, cv2.LINE_AA)
        # Círculo no vértice do canto
        cv2.circle(frame, (cx, cy), 4, COR_CANTO, -1, cv2.LINE_AA)

    return frame


def _desenhar_borda_tracejada(frame, x1, y1, x2, y2, cor, espessura,
                               tamanho_traco=18, espaco=10):
    """
    Desenha as 4 bordas do retângulo como linhas tracejadas (pontilhadas).
    Cada borda é subdividida em segmentos alternados de traço e espaço vazio.

    Parâmetros:
        frame:         Frame onde as bordas serão desenhadas
        x1,y1,x2,y2:  Coordenadas do retângulo
        cor:           Cor BGR dos traços
        espessura:     Espessura dos traços em pixels
        tamanho_traco: Comprimento de cada traço em pixels
        espaco:        Espaço vazio entre os traços em pixels
    """
    def tracos_na_linha(p1, p2):
        """
        Desenha traços ao longo de uma linha entre dois pontos.
        Calcula a direção unitária e avança posição a posição desenhando
        segmentos com intervalos de espaço entre eles.
        """
        # Distância total entre os dois pontos (em pixels)
        dist = int(np.linalg.norm(np.array(p2) - np.array(p1)))

        # Vetor de direção normalizado (comprimento 1 pixel)
        direcao = (np.array(p2) - np.array(p1)) / max(dist, 1)

        # Posição atual ao longo da linha
        pos = 0  
        while pos < dist:
            # Ponto inicial do traço atual
            inicio = tuple((np.array(p1) + direcao * pos).astype(int))
            # Ponto final do traço atual (não ultrapassa o fim da linha)
            fim = tuple((np.array(p1) + direcao * min(pos + tamanho_traco, dist)).astype(int))
            cv2.line(frame, inicio, fim, cor, espessura, cv2.LINE_AA)
            # Avança para o próximo traço (traço + espaço)
            pos += tamanho_traco + espaco

    # Desenha os traços nas 4 bordas em sentido horário
    tracos_na_linha((x1, y1), (x2, y1))  # Borda superior (esq → dir)
    tracos_na_linha((x2, y1), (x2, y2))  # Borda direita  (cima → baixo)
    tracos_na_linha((x2, y2), (x1, y2))  # Borda inferior (dir → esq)
    tracos_na_linha((x1, y2), (x1, y1))  # Borda esquerda (baixo → cima)


# ─── Interface HUD (Heads-Up Display) ────────────────────────────────────────

def texto_com_sombra(frame, texto, pos, escala=0.55, cor=COR_TEXTO, espessura=1):
    """
    Escreve texto sobre o frame com uma sombra preta deslocada atrás,
    garantindo legibilidade independentemente da cor do fundo da câmera.

    Técnica: renderiza o texto duas vezes — primeiro a sombra (deslocada 1px
    para baixo e direita, mais grossa), depois o texto colorido por cima.

    Parâmetros:
        frame:     Frame onde o texto será desenhado
        texto:     String a ser exibida
        pos:       Tupla (x, y) com a posição do canto inferior-esquerdo do texto
        escala:    Tamanho da fonte (multiplicador)
        cor:       Cor BGR do texto principal
        espessura: Espessura do texto em pixels
    """
    x, y = pos

    # Renderiza a sombra: deslocada 1px, mais grossa, cor preta
    cv2.putText(frame, texto, (x+1, y+1),
                cv2.FONT_HERSHEY_SIMPLEX, escala, COR_SOMBRA, espessura + 1, cv2.LINE_AA)

    # Renderiza o texto principal por cima da sombra
    cv2.putText(frame, texto, (x, y),
                cv2.FONT_HERSHEY_SIMPLEX, escala, cor, espessura, cv2.LINE_AA)


def desenhar_hud(frame: np.ndarray, status: dict):
    """
    Desenha o painel de informações (HUD) na parte inferior do frame.

    O HUD exibe:
        - Painel semitransparente escuro como fundo
        - Instrução principal ao usuário
        - Última ação realizada (salvar, capturar, etc.)
        - Atalhos de teclado disponíveis
        - Badge colorido com o modo de imagem ativo
        - Miniatura da última captura realizada

    Parâmetros:
        frame:  Frame da câmera que será modificado com os elementos do HUD
        status: Dicionário com informações do estado atual do scanner:
                  'instrucao'      → texto da instrução principal
                  'cor_instrucao'  → cor da instrução (padrão branco)
                  'ultima_acao'    → texto da última ação executada
                  'ultima_captura' → array numpy da última imagem capturada
                  'modo_imagem'    → string do modo ativo ('adaptativo', 'cinza', 'colorido')
    """
    h, w = frame.shape[:2]

    # ── Painel de fundo semitransparente ─────────────────────────
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, h - 90), (w, h), (15, 15, 15), -1)
    cv2.addWeighted(overlay, 0.75, frame, 0.25, 0, frame)  # 75% escuro, 25% frame
    cv2.line(frame, (0, h - 90), (w, h - 90), (60, 60, 60), 1)  # linha divisória

    # ── Instrução principal ───────────────────────────────────────
    instrucao = status.get("instrucao", "Posicione o documento dentro do retangulo")
    texto_com_sombra(frame, instrucao, (20, h - 65), escala=0.52,
                     cor=status.get("cor_instrucao", COR_TEXTO))

    # ── Última ação realizada ─────────────────────────────────────
    # Exibe feedback ao usuário sobre a operação mais recente (ex: "PDF salvo")
    ultima_acao = status.get("ultima_acao", "")
    if ultima_acao:
        texto_com_sombra(frame, ultima_acao, (20, h - 42), escala=0.44,
                         cor=(160, 160, 160))  # Cinza claro para diferenciar da instrução

    # ── Linha de atalhos de teclado ───────────────────────────────
    controles = "[ESPACO] Capturar   [S] PDF   [I] PNG   [M] Modo   [Q] Sair"
    texto_com_sombra(frame, controles, (20, h - 16), escala=0.37,
                     cor=(100, 100, 100))  # Cinza escuro (menos destaque)

    # ── Badge do modo de imagem ───────────────────────────────────
    # Pequeno retângulo colorido no canto direito indicando o modo ativo
    modo = status.get("modo_imagem", "adaptativo")
    cores_modo = {
        "adaptativo": (50, 160, 255),   # Azul → modo principal (P&B limpo)
        "cinza":      (150, 150, 150),  # Cinza → tons de cinza
        "colorido":   (50, 200, 100),   # Verde → colorido original
    }
    cor_modo = cores_modo.get(modo, (100, 100, 100))
    bw = 110  # Largura do badge
    cv2.rectangle(frame, (w - bw - 10, h - 82), (w - 10, h - 58), cor_modo, -1)
    cv2.putText(frame, f"MODO: {modo.upper()}", (w - bw - 5, h - 63),
                cv2.FONT_HERSHEY_SIMPLEX, 0.33, (255, 255, 255), 1, cv2.LINE_AA)

    # ── Miniatura da última captura ───────────────────────────────
    ultima_img = status.get("ultima_captura")
    if ultima_img is not None:
        try:
            mini_h = 80  # Altura fixa da miniatura em pixels
            # Calcula largura proporcional para não distorcer a imagem
            mini_w = int(mini_h * ultima_img.shape[1] / ultima_img.shape[0])
            mini = cv2.resize(ultima_img, (mini_w, mini_h))

            # Garante que a miniatura é colorida (3 canais) para caber no frame BGR
            if len(mini.shape) == 2:
                mini = cv2.cvtColor(mini, cv2.COLOR_GRAY2BGR)

            # Posiciona a miniatura acima do painel do HUD
            xm = w - mini_w - 10   
            ym = h - 175            
            frame[ym:ym+mini_h, xm:xm+mini_w] = mini

            # Borda ao redor da miniatura
            cv2.rectangle(frame, (xm-1, ym-1), (xm+mini_w+1, ym+mini_h+1),
                          (80, 80, 80), 1)

            # Rótulo acima da miniatura
            texto_com_sombra(frame, "ultima captura", (xm, ym - 6),
                             escala=0.32, cor=(120, 120, 120))
        except Exception:
            pass  # Ignora erros silenciosamente para não travar o loop principal


def desenhar_contagem(frame: np.ndarray, contagem: int):
    """
    Exibe um número de contagem regressiva grande e centralizado no frame.
    Usado para dar tempo ao usuário de posicionar o documento antes da captura.

    O número é renderizado com sombra preta espessa para garantir visibilidade
    sobre qualquer fundo da câmera.

    Parâmetros:
        frame:    Frame onde o número será desenhado
        contagem: Número inteiro a ser exibido (ex: 3, 2, 1)
    """
    h, w = frame.shape[:2]
    texto = str(contagem)
    escala = 5.0
    espessura = 8 

    # Calcula o tamanho do texto para centralizar perfeitamente
    (tw, th), _ = cv2.getTextSize(texto, cv2.FONT_HERSHEY_SIMPLEX, escala, espessura)
    cx = (w - tw) // 2   # Centro horizontal
    cy = (h + th) // 2   # Centro vertical

    # Renderiza sombra preta espessa
    cv2.putText(frame, texto, (cx+3, cy+3),
                cv2.FONT_HERSHEY_SIMPLEX, escala, (0, 0, 0), espessura + 4, cv2.LINE_AA)

    # Renderiza o número colorido por cima da sombra
    cv2.putText(frame, texto, (cx, cy),
                cv2.FONT_HERSHEY_SIMPLEX, escala, COR_PRONTO, espessura, cv2.LINE_AA)


# ─── Classe principal do scanner ──────────────────────────────────────────────

class ScannerRetangulo:
    """
    Classe principal que gerencia todo o ciclo de vida do scanner:
    inicialização da câmera, loop de captura, processamento da imagem
    e salvamento dos arquivos.
    """

    def __init__(self, camera_id: int = 0, ocr: bool = False,
                 contagem_regressiva: int = 0, foco_manual: int = 50):
        """
        Inicializa o scanner com as configurações desejadas.

        Parâmetros:
            camera_id:           Índice da câmera a ser usada (0 = câmera padrão)
            ocr:                 Se True e easyocr estiver instalado, extrai texto da captura
            contagem_regressiva: Segundos de espera entre pressionar ESPAÇO e capturar
                                 (0 = captura imediata, sem contagem)
            foco_manual:         Valor de foco para a câmera (0–255); útil para webcams
                                 que permitem controle de foco via software
        """
        self.camera_id = camera_id
        self.ocr_ativo = ocr and EASYOCR_DISPONIVEL  # Só ativa se biblioteca disponível
        self.contagem_regressiva = contagem_regressiva
        self.foco_manual = foco_manual
        self.leitor_ocr = None        # Instância do EasyOCR (carregada sob demanda)
        self.ultima_captura = None    # Última imagem capturada (array numpy)
        self.ultima_acao = ""         # Texto descritivo da última ação para o HUD
        self.modo_imagem = "adaptativo"  # Modo de processamento inicial
        self.cap = None               # Objeto VideoCapture do OpenCV

        # Carrega o modelo OCR se a opção estiver ativa
        if self.ocr_ativo:
            print("[INFO] Carregando OCR...")
            try:
                # Inicializa leitor para português e inglês sem GPU
                self.leitor_ocr = easyocr.Reader(['pt', 'en'], gpu=False)
                print("[OK] OCR pronto.")
            except Exception as e:
                print(f"[AVISO] OCR falhou: {e}")
                self.ocr_ativo = False

    def _iniciar_camera(self) -> bool:
        """
        Inicializa a câmera tentando múltiplos índices automaticamente.

        Tenta primeiro o índice configurado (camera_id), depois 0, 1 e 2.
        Após abrir a câmera, configura a resolução para 1280x720 e descarta
        os primeiros 10 frames instáveis (comum em webcams ao inicializar).

        Retorna:
            True se alguma câmera foi aberta com sucesso, False caso contrário.
        """
        for idx in [self.camera_id, 0, 1, 2]:
            cap = cv2.VideoCapture(idx)
            if cap.isOpened():
                self.cap = cap

                # Configura resolução preferida (câmera pode ignorar se não suportar)
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

                # Tenta definir foco manual (funciona em webcams compatíveis)
                self.cap.set(cv2.CAP_PROP_AUTOFOCUS, self.foco_manual)

                # Descarta os primeiros frames para estabilizar a exposição da câmera
                for _ in range(10):
                    self.cap.read()

                print(f"[OK] Camera iniciada (indice {idx})")
                return True
            cap.release()

        print("[ERRO] Nenhuma camera encontrada.")
        return False

    def _ler_frame(self):
        """
        Lê um único frame da câmera com verificação de validade.

        Retorna:
            Tupla (bool, frame):
                - (True, array_numpy) se o frame foi lido com sucesso
                - (False, None) se a câmera não está disponível ou o frame é inválido
        """
        if not self.cap or not self.cap.isOpened():
            return False, None

        ret, frame = self.cap.read()

        # ret=False significa erro na leitura; frame=None indica frame corrompido
        if not ret or frame is None:
            return False, None

        return True, frame

    def _capturar_regiao(self, frame: np.ndarray):
        """
        Recorta exatamente a região delimitada pelo retângulo guia no frame
        e aplica o processamento de imagem conforme o modo selecionado.

        O recorte usa slicing numpy [y1:y2, x1:x2], que é eficiente e não
        copia memória desnecessária (por isso o .copy() é necessário para
        garantir que o array seja independente do frame original).

        Parâmetros:
            frame: Frame completo da câmera

        Retorna:
            Array numpy com a imagem processada da região recortada,
            ou None se o recorte falhar.
        """
        x1, y1, x2, y2 = calcular_retangulo(frame)

        # Recorta apenas a área interna do retângulo guia
        recorte = frame[y1:y2, x1:x2].copy()

        # Verifica se o recorte tem pixels válidos
        if recorte.size == 0:
            print("[ERRO] Recorte vazio.")
            return None

        # Aplica o pós-processamento escolhido pelo usuário
        return aprimorar(recorte, modo=self.modo_imagem)

    def _executar_ocr(self, imagem: np.ndarray) -> str:
        """
        Executa o reconhecimento de texto (OCR) na imagem capturada.

        O EasyOCR retorna uma lista de tuplas (bbox, texto, confiança).
        Apenas resultados com confiança acima de 30% são incluídos
        para filtrar leituras incorretas.

        Parâmetros:
            imagem: Array numpy da imagem processada a ser analisada

        Retorna:
            String com o texto reconhecido, separado por quebras de linha.
            Retorna string vazia se OCR inativo ou em caso de erro.
        """
        if not self.ocr_ativo or self.leitor_ocr is None:
            return ""
        try:
            resultados = self.leitor_ocr.readtext(imagem)
            # Filtra e junta apenas os textos com confiança suficiente
            return "\n".join([t for (_, t, c) in resultados if c > 0.3])
        except Exception as e:
            print(f"[ERRO] OCR: {e}")
            return ""

    def _realizar_captura(self, frame: np.ndarray):
        """
        Orquestra o processo completo de captura:
            1. Recorta e processa a região do retângulo
            2. Armazena como a última captura disponível
            3. Executa OCR e salva o texto em .txt (se OCR ativo)
            4. Atualiza o texto de status para o HUD

        Parâmetros:
            frame: Frame atual da câmera no momento da captura

        Retorna:
            True se a captura foi bem-sucedida, False caso contrário.
        """
        captura = self._capturar_regiao(frame)

        if captura is not None:
            self.ultima_captura = captura
            self.ultima_acao = "Capturado com sucesso!"

            # Se OCR ativo, extrai texto e salva como arquivo .txt
            if self.ocr_ativo:
                texto = self._executar_ocr(captura)
                if texto:
                    p = gerar_nome_arquivo("txt")
                    p.write_text(texto, encoding="utf-8")
                    self.ultima_acao = "Capturado + OCR salvo!"

            return True
        else:
            self.ultima_acao = "Falha na captura."
            return False

    def executar(self):
        """
        Loop principal do scanner — método central que mantém tudo funcionando.

        Fluxo do loop:
            1. Lê frame da câmera
            2. Calcula posição do retângulo guia
            3. Gerencia contagem regressiva (se ativa)
            4. Desenha retângulo guia e efeito flash pós-captura
            5. Desenha o HUD com informações de status
            6. Exibe o frame na janela
            7. Processa teclas pressionadas pelo usuário
            8. Repete a partir do passo 1

        O loop é encerrado quando o usuário pressiona Q, ESC ou fecha a janela.
        O bloco finally garante que a câmera seja sempre liberada corretamente.
        """
        # Encerra se nenhuma câmera for encontrada
        if not self._iniciar_camera():
            return  

        print("\n" + "=" * 52)
        print("  Scanner - Retangulo Fixo")
        print("=" * 52)
        print("  Posicione o documento dentro do retangulo")
        print("  [ESPACO]  Capturar")
        print("  [S]       Salvar PDF")
        print("  [I]       Salvar PNG")
        print("  [M]       Alternar modo de imagem")
        print("  [Q/ESC]   Sair")
        print("=" * 52 + "\n")

        em_contagem = False    # Indica se a contagem regressiva está ativa
        inicio_contagem = 0.0  # Timestamp de quando a contagem foi iniciada
        flash_timer = 0        # Contador de frames do efeito flash branco pós-captura

        try:
            while True:
                # ── Leitura do frame ─────────────────────────────
                ret, frame = self._ler_frame()
                if not ret:
                    time.sleep(0.05)  # Pequena pausa para não sobrecarregar a CPU
                    continue

                # Cópia do frame para desenhar os elementos visuais sem modificar o original
                display = frame.copy()
                x1, y1, x2, y2 = calcular_retangulo(frame)

                # ── Gerenciamento da contagem regressiva ─────────
                if em_contagem:
                    elapsed = time.time() - inicio_contagem          # Tempo decorrido
                    restante = self.contagem_regressiva - int(elapsed)  # Segundos restantes

                    if restante > 0:
                        # Ainda há tempo: mostra retângulo verde e o número
                        desenhar_retangulo_guia(display, x1, y1, x2, y2, pronto=True)
                        desenhar_contagem(display, restante)
                    else:
                        # Contagem chegou a zero: realiza a captura automaticamente
                        em_contagem = False
                        if self._realizar_captura(frame):
                            flash_timer = 14  # Inicia efeito flash de 14 frames
                        continue  # Pula para o próximo frame imediatamente

                else:
                    # Estado normal: exibe retângulo guia padrão (amarelo)
                    desenhar_retangulo_guia(display, x1, y1, x2, y2, pronto=False)

                # ── Efeito flash branco pós-captura ──────────────
                # Mescla um frame branco com o display diminuindo gradualmente
                # a intensidade ao longo de 14 frames (dá sensação de "foto tirada")
                if flash_timer > 0:
                    alpha = flash_timer / 14  # Opacidade decrescente (1.0 → 0.0)
                    branco = np.ones_like(display) * 255
                    cv2.addWeighted(branco, alpha * 0.6,
                                    display, 1 - alpha * 0.6, 0, display)
                    flash_timer -= 1

                # ── Desenha o HUD com as informações de status ───
                status = {
                    "instrucao": "Posicione o documento dentro do retangulo",
                    "ultima_acao": self.ultima_acao,
                    "ultima_captura": self.ultima_captura,
                    "modo_imagem": self.modo_imagem,
                }
                desenhar_hud(display, status)

                # Exibe o frame processado na janela
                cv2.imshow("Scanner de Documentos", display)

                # ── Leitura de teclas (aguarda 1ms por frame) ────
                # waitKey(1) é necessário para o OpenCV processar eventos da janela
                tecla = cv2.waitKey(1) & 0xFF

                # [ESPAÇO] → Iniciar captura (com ou sem contagem regressiva)
                if tecla == ord(' '):
                    if self.contagem_regressiva > 0:
                        # Inicia a contagem — a captura ocorrerá automaticamente ao fim
                        em_contagem = True
                        inicio_contagem = time.time()
                        self.ultima_acao = "Preparando..."
                    else:
                        # Captura imediata sem contagem
                        if self._realizar_captura(frame):
                            flash_timer = 14

                # [S] → Salvar última captura como PDF
                elif tecla == ord('s') or tecla == ord('S'):
                    if self.ultima_captura is not None:
                        p = gerar_nome_arquivo("pdf")
                        ok = salvar_pdf(self.ultima_captura, p)
                        self.ultima_acao = f"PDF: {p.name}" if ok else "Erro ao salvar."
                    else:
                        self.ultima_acao = "Nada capturado. Pressione ESPACO primeiro."

                # [I] → Salvar última captura como PNG
                elif tecla == ord('i') or tecla == ord('I'):
                    if self.ultima_captura is not None:
                        p = gerar_nome_arquivo("png")
                        ok = salvar_imagem(self.ultima_captura, p)
                        self.ultima_acao = f"PNG: {p.name}" if ok else "Erro ao salvar."
                    else:
                        self.ultima_acao = "Nada capturado. Pressione ESPACO primeiro."

                # [M] → Alternar entre os modos de processamento de imagem
                elif tecla == ord('m') or tecla == ord('M'):
                    modos = ["adaptativo", "cinza", "colorido"]
                    idx = modos.index(self.modo_imagem)
                    # Avança para o próximo modo ciclicamente
                    self.modo_imagem = modos[(idx + 1) % len(modos)]
                    self.ultima_acao = f"Modo: {self.modo_imagem}"

                # [Q] ou [ESC] → Encerrar o programa
                elif tecla == ord('q') or tecla == ord('Q') or tecla == 27:
                    print("[INFO] Encerrando.")
                    break

        except KeyboardInterrupt:
            # Captura Ctrl+C no terminal de forma elegante
            print("\n[INFO] Interrompido.")
        finally:
            # Garante liberação dos recursos independentemente de como o programa encerrou
            if self.cap:
                self.cap.release()       # Libera a câmera
            cv2.destroyAllWindows()      # Fecha todas as janelas do OpenCV
            print(f"[INFO] Arquivos em: {PASTA_SAIDA.resolve()}")


# ─── Ponto de entrada ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    """
    Ponto de entrada do programa quando executado diretamente pelo terminal.
    Usa argparse para aceitar parâmetros opcionais via linha de comando.

    Exemplos de uso:
        python scanner_documentos.py                      → câmera padrão, captura imediata
        python scanner_documentos.py --camera 1           → usa câmera de índice 1
        python scanner_documentos.py --contagem 3         → conta 3 segundos antes de capturar
        python scanner_documentos.py --ocr                → ativa reconhecimento de texto
        python scanner_documentos.py --contagem 3 --ocr   → contagem + OCR simultâneos
    """
    import argparse

    parser = argparse.ArgumentParser(description="Scanner com retangulo fixo.")

    # Argumento para escolher qual câmera usar (útil quando há múltiplas webcams)
    parser.add_argument("--camera", "-c", type=int, default=0,
                        help="Indice da camera (padrao: 0)")

    # Argumento para ativar contagem regressiva antes da captura
    parser.add_argument("--contagem", type=int, default=0,
                        help="Contagem regressiva em segundos antes de capturar (padrao: 0)")

    # Argumento para controle de foco da webcam via software
    parser.add_argument("--foco", type=int, default=50,
                        help="Foco manual da camera (0-255, padrao: 50)")

    # Flag para ativar OCR (não requer valor, apenas presença do argumento)
    parser.add_argument("--ocr", action="store_true",
                        help="Ativar OCR (requer easyocr instalado)")

    args = parser.parse_args()

    # Instancia e executa o scanner com os parâmetros fornecidos
    scanner = ScannerRetangulo(
        camera_id=args.camera,
        ocr=args.ocr,
        contagem_regressiva=args.contagem,
        foco_manual=args.foco,
    )
    scanner.executar()