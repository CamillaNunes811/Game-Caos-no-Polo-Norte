import pygame #Biblioteca utilizada para o desenvolvimento de jogos .
import os #Biblioteca que permite manipulação de caminhos de arquivo neste caso.
import random #Biblioteca que gera números aleatórios, usada aqui para gerar alturas aleatórias para os canos.
import pygame.mixer #Módulo da biblioteca pygame usado para lidar com reprodução de áudio.
import time #Biblioteca utilizada para para pausar a execução do programa.

# Definindo as dimensões da tela
TELA_LARGURA = 500
TELA_ALTURA = 800
DIFICULDADE = 5

# Carregando as imagens e sons necessários
IMAGEM_CANO = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'pipe.png')))
IMAGEM_CHAO = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'base.png')))
IMAGEM_BACKGROUND = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bg.png')))
IMAGEM_GAMEOVER = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'gameover.png')))
IMAGEM_LOGO = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'logo.png')))
IMAGENS_TRENO = [
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird1.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird2.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird3.png'))),
]

pygame.font.init() # Fonte que exibir a pontuação
FONTE_PONTOS = pygame.font.SysFont('arial', 50)
pygame.mixer.init() # Inicializando o mixer para reprodução de áudio
pygame.mixer.music.load('play/musicfundo.mp3')
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.5)

def tocar_musica_game_over(): # Função para tocar música de game over
    pygame.mixer.music.stop()
    pygame.mixer.music.load('play/musicgameover.mp3')
    pygame.mixer.music.play(0)
    pygame.mixer.music.set_volume(0.5)

class Treno:
    IMGS = IMAGENS_TRENO
    ROTACAO_MAXIMA = 25 # define o ângulo máximo de rotação do Treno ao pular
    VELOCIDADE_ROTACAO = 20 # define a vel ocidade de rotação do Treno
    TEMPO_ANIMACAO = 5  # é o tempo de exibição de cada imagem durante a animação

    def __init__(self, x, y):
        self.x = x # x e y representam as coordenadas iniciais do Treno
        self.y = y
        self.angulo = 0 # angulo representa o ângulo de inclinação do Treno
        self.velocidade = 0 # velocidade representa a velocidade vertical do Treno
        self.altura = self.y # altura representa a altura inicial do Treno
        self.tempo = 0 # tempo é usado para calcular o deslocamento vertical do Treno durante o pulo
        self.contagem_imagem = 0 # contagem_imagem rastreia o tempo decorrido para atualizar a animação 
        self.imagem = self.IMGS[0]  #imagem representa a imagem atual do Treno na animação
        self.visivel = True # visivel indica se o Treno deve ser desenhado na tela

    def pular(self): # Método chamado quando o jogador pressiona a tecla de espaço para fazer o Treno pular
        self.velocidade = -10.5
        self.tempo = 0
        self.altura = self.y

    def mover(self):
        self.tempo += 1 # Incrementa o tempo para o cálculo do deslocamento
        deslocamento = 1.5 * (self.tempo**2) + self.velocidade * self.tempo # Calcula o deslocamento vertical do treno usando uma função quadrática
        if deslocamento > 16: # Limita o deslocamento máximo para evitar movimentos excessivos para baixo
            deslocamento = 16
        elif deslocamento < 0: # Se o deslocamento for negativo, ajusta para uma queda mais rápida         
            deslocamento -= 2
        self.y += deslocamento # Atualiza a posição vertical do treno
        if deslocamento < 0 or self.y < (self.altura + 50): # Ajusta o ângulo de rotação do treno com base no deslocamento
            if self.angulo < self.ROTACAO_MAXIMA:
                self.angulo = self.ROTACAO_MAXIMA
        else:
            if self.angulo > -90:
                self.angulo -= self.VELOCIDADE_ROTACAO

    def desenhar(self, tela): # Verifica se o treno está visível 
        if self.visivel:
            self.contagem_imagem += 1 # Incrementa a contagem de imagens para a animação do treno
            if self.contagem_imagem < self.TEMPO_ANIMACAO: # Seleciona a imagem do treno com base na contagem de animação
                self.imagem = self.IMGS[0]
            elif self.contagem_imagem < self.TEMPO_ANIMACAO*2:
                self.imagem = self.IMGS[1]
            elif self.contagem_imagem < self.TEMPO_ANIMACAO*3:
                self.imagem = self.IMGS[2]
            elif self.contagem_imagem < self.TEMPO_ANIMACAO*4:
                self.imagem = self.IMGS[1]
            elif self.contagem_imagem >= self.TEMPO_ANIMACAO*4 + 1:
                self.imagem = self.IMGS[0]
                self.contagem_imagem = 0 # Verifica se o treno está em uma posição de mergulho


            if self.angulo <= -80:
                self.imagem = self.IMGS[1]
                self.contagem_imagem = self.TEMPO_ANIMACAO*2

            imagem_rotacionada = pygame.transform.rotate(self.imagem, self.angulo) # Rotaciona a imagem do treno de acordo com o ângulo
            pos_centro_imagem = self.imagem.get_rect(topleft=(self.x, self.y)).center # Obtém o centro da imagem original para posicionamento adequado após rotação
            retangulo = imagem_rotacionada.get_rect(center=pos_centro_imagem) # Obtém o retângulo da imagem rotacionada 
            tela.blit(imagem_rotacionada, retangulo.topleft) # Desenha a imagem rotacionada na tela 

    def get_mask(self): # Cria e retorna uma máscara de colisão a partir da superfície da imagem do treno
        return pygame.mask.from_surface(self.imagem)

class Cano: # Classe para representar os canos
    DISTANCIA = 300 # Distância padrão entre os canos
    VELOCIDADE = 5 # Velocidade de movimento dos canos

    def __init__(self, x, dificuldade):
        self.x = x
        self.altura = 0
        self.pos_topo = 0 # Posição do topo do cano
        self.pos_base = 0 # Posição da base do cano
        self.CANO_TOPO = pygame.transform.flip(IMAGEM_CANO, False, True) # Imagem do cano invertida para o topo
        self.CANO_BASE = IMAGEM_CANO # Imagem do cano para a base
        self.passou = False # Indica se o treno já passou por este cano
        self.definir_altura(dificuldade) # Inicializa a altura do cano com base na dificuldade

    def definir_altura(self, dificuldade):
        self.altura = random.randrange(50, 450) + (dificuldade * 10)  # Gera uma altura aleatória entre 50 e 450, ajustada pela dificuldade
        self.pos_topo = self.altura - self.CANO_TOPO.get_height() # Calcula a posição do topo do cano com base na altura e na altura do topo da imagem do cano
        self.pos_base = self.altura + self.DISTANCIA # Calcula a posição da base do cano com base na altura e na distância padrão entre os canos

    def mover(self):
        self.x -= self.VELOCIDADE # Atualiza a posição horizontal do cano subtraindo sua velocidade

    def desenhar(self, tela):
        tela.blit(self.CANO_TOPO, (self.x, self.pos_topo)) # Desenha a imagem do topo do cano na posição (x, pos_topo) na tela
        tela.blit(self.CANO_BASE, (self.x, self.pos_base)) # Desenha a imagem da base do cano na posição (x, pos_base) na tela


    def colidir(self, treno):
        treno_mask = treno.get_mask() # Obtém a máscara de pixels do treno
        topo_mask = pygame.mask.from_surface(self.CANO_TOPO) # Obtém as máscaras de pixels do topo e da base do cano
        base_mask = pygame.mask.from_surface(self.CANO_BASE)
        distancia_topo = (self.x - treno.x, self.pos_topo - round(treno.y)) # Calcula as distâncias entre os pixels do treno e do topo/base do cano
        distancia_base = (self.x - treno.x, self.pos_base - round(treno.y))
        topo_ponto = treno_mask.overlap(topo_mask, distancia_topo) # Verifica se há sobreposição de pixels entre as máscaras do treno e do topo/base do cano
        base_ponto = treno_mask.overlap(base_mask, distancia_base)
        if base_ponto or topo_ponto:  # Se houver sobreposição de pixels entre o treno e o topo/base do cano, retorna True (houve colisão)
            return True
        else: # Se não houver sobreposição, retorna False (não houve colisão)  
            return False

class Chao: # Classe para representar o chão
    VELOCIDADE = 5
    LARGURA = IMAGEM_CHAO.get_width()
    IMAGEM = IMAGEM_CHAO

    def __init__(self, y):
        self.y = y # Inicializa a posição vertical do chão
        self.x1 = 0 # Inicializa as posições horizontais do chão para criar o efeito de movimento
        self.x2 = self.LARGURA

    def mover(self):
        self.x1 -= self.VELOCIDADE # Move as posições horizontais do chão de acordo com a velocidade
        self.x2 -= self.VELOCIDADE
        if self.x1 + self.LARGURA < 0: # Verifica se a primeira imagem do chão saiu completamente da tela e a reposiciona
            self.x1 = self.x2 + self.LARGURA
        if self.x2 + self.LARGURA < 0: # Verifica se a segunda imagem do chão saiu completamente da tela e a reposiciona
            self.x2 = self.x1 + self.LARGURA

    def desenhar(self, tela): # Desenha as duas imagens do chão em movimento  
        tela.blit(self.IMAGEM, (self.x1, self.y))
        tela.blit(self.IMAGEM, (self.x2, self.y))

def desenhar_tela(tela, trenos, canos, chao, pontos, game_over, nivel, tela_titulo): # Função para desenhar a tela do jogo
    tela.blit(IMAGEM_BACKGROUND, (0, 0)) # Desenha o fundo da tela
    if tela_titulo:
        tela.blit(IMAGEM_LOGO, ((TELA_LARGURA - IMAGEM_LOGO.get_width()) // 2, (TELA_ALTURA - IMAGEM_LOGO.get_height()) // 2)) # Desenha o logotipo no centro da tela
        pygame.display.update() #Atualiza a tela para exibir o logotipo
        pygame.mixer.init() # Inicializa o mixer de áudio do pygame
        time.sleep(1)  # Aguarda por 1 segundo para exibir o logotipo
    for treno in trenos:  # Loop para desenhar cada treno na tela, caso esteja visível  
        if treno.visivel:
            treno.desenhar(tela)
    for cano in canos: # Loop para desenhar cada cano na tela
        cano.desenhar(tela)
    if game_over: # Verifica se o jogo está no estado de "game over"
        tela.blit(IMAGEM_GAMEOVER, ((TELA_LARGURA - IMAGEM_GAMEOVER.get_width()) // 2, (TELA_ALTURA - IMAGEM_GAMEOVER.get_height()) // 2)) # Se estiver no estado de "game over", exibe a imagem de game over no centro da tela
    else:
        texto_pontos = FONTE_PONTOS.render(f"Pontuação: {pontos}", 1, (255, 255, 255)) # Se não estiver no estado de "game over", exibe a pontuação e o nível na tela
        tela.blit(texto_pontos, (TELA_LARGURA - 10 - texto_pontos.get_width(), 10))
        texto_nivel = FONTE_PONTOS.render(f"Nível: {nivel}", 1, (255, 255, 255))
        tela.blit(texto_nivel, (10, 10))
        chao.desenhar(tela) # Desenha o chão na tela
    pygame.display.update() # Atualiza a tela para refletir as mudanças

def reiniciar_jogo(): # Função para reiniciar o jogo
    treno = Treno(230, 350) # Cria um objeto da classe treno com posição inicial (230, 350)
    chao = Chao(730) # Cria um objeto da classe Chao com posição inicial 730
    cano = Cano(700, DIFICULDADE) # Cria um objeto da classe Cano com posição inicial 700 e dificuldade DIFICULDADE
    return [treno], chao, [cano], 0, False # Retorna uma lista contendo o treno, chao, uma lista com o cano, pontuação inicial (0) e False indicando que o jogo não está no estado de "game over"

def main():
    global DIFICULDADE # Declaração de uma variável global DIFICULDADE
    pygame.mixer.music.play(-1)  # Inicia a reprodução contínua da música de fundo
    trenos, chao, canos, pontos, game_over = reiniciar_jogo() # Chama a função reiniciar_jogo para obter os elementos iniciais do jogo
    tela = pygame.display.set_mode((TELA_LARGURA, TELA_ALTURA)) # Cria a tela do jogo com as dimensões especificadas 
    nivel = 1
    relogio = pygame.time.Clock() # Cria um objeto Clock para controlar a taxa de quadros por segundo (FPS)
    tela_titulo = True

    rodando = True
    while rodando:
        relogio.tick(30) # Limita o loop para rodar a uma taxa de 30 quadros por segundo
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT: # Verifica se o evento é do tipo QUIT (fechar a janela)
                rodando = False # Define a variável 'rodando' como False para encerrar o loop 
                pygame.quit() # Encerra o pygame
                quit()
            elif evento.type == pygame.KEYDOWN: # Verifica se a tecla pressionada é a tecla de espaço
                if game_over and evento.key == pygame.K_SPACE: # Se o jogo terminou e a tecla de espaço foi pressionada, interrompe a música atual
                    pygame.mixer.music.stop()
                    pygame.mixer.music.load('play/musicfundo.mp3') # Carrega a música de fundo novamente  
                    pygame.mixer.music.play(-1) # Inicia a reprodução da música de fundo em um loop infinito
                    trenos, chao, canos, pontos, game_over = reiniciar_jogo() # Reinicia o jogo obtendo novas instâncias de treno, chao, canos e zerando os pontos e a flag de game_over
                    nivel = 1
                    tela_titulo = True
                elif not game_over and evento.key == pygame.K_SPACE: # Verifica se o jogo não terminou e a tecla de espaço foi pressionada
                    for treno in trenos:
                        treno.pular() # Chama o método pular() do treno, fazendo-o pular # Define a variável tela_titulo como False, indicando que o título do jogo não deve ser exibido
                    tela_titulo = False

        if not game_over: # Verifica se o jogo não terminou

            for treno in trenos:
                treno.mover()
            chao.mover()
        adicionar_cano = False # Variável que indica se deve ser adicionado um novo cano
        remover_canos = [] # Lista para armazenar canos que devem ser removidos
        for cano in canos:
            for i, treno in enumerate(trenos):
                if cano.colidir(treno): # Verifica se há colisão entre o cano e o treno
                    game_over = True # Define o estado do jogo como game over
                    treno.visivel = False # Torna o treno invisível
                    tocar_musica_game_over() # Toca a música de game over
                if not cano.passou and treno.x > cano.x: # Verifica se o treno ultrapassou o cano
                    cano.passou = True # Marca que o treno passou pelo cano
                    adicionar_cano = True # Indica que um novo cano deve ser adicionado
            cano.mover()
            if cano.x + cano.CANO_TOPO.get_width() < 0: # Verifica se o cano saiu da tela
                remover_canos.append(cano) # Adiciona o cano à lista de remoção

        if adicionar_cano: # Verifica se um novo cano deve ser adicionado
            pontos += 1 # Incrementa a pontuação
            if pontos % 5 == 0: # Verifica se a pontuação é um múltiplo de 5
                nivel += 1
            canos.append(Cano(600, DIFICULDADE))

        for i, treno in enumerate(trenos): # Loop sobre os treno na lista
            if (treno.y + treno.imagem.get_height()) > chao.y or treno.y < 0:
                game_over = True # Define a variável game_over como True
                treno.visivel = False # Torna o treno invisível
                tocar_musica_game_over() # Chama a função para tocar a música de game over

        desenhar_tela(tela, trenos, canos, chao, pontos, game_over, nivel, tela_titulo) # Chama a função desenhar_tela para renderizar a tela do jogo com os parâmetros necessários

if __name__ == '__main__': # Verifica se o script está sendo executado como o programa principal
    main() # Chama a função main() para iniciar o loop principal do jogo e executar a lógica do jogo

