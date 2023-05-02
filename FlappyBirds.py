import pygame
import os
import random
import neat

"""
This is a study project for making machine learning work with AI.
It helps the birds from the game understand the best strategy so they do not crash onto the pipes.
I used machine learning to train the data and make it progress by itself.
"""

# If you want to play and drop the AI option, put False
aiJogando = True
geracao = 0


telaLargura = 500
telaAltura = 800

# pygame.transform to increase the scale of the image
# os.path to identify the folder of the image
imagemCano = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'pipe.png')))
imagemChao = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'base.png')))
imagemBackground = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bg.png')))
imagemPassaros = [pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird1.png'))),
                  pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird2.png'))),
                  pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird3.png')))]

# It creates the font of what is written on the screen
pygame.font.init()
fontePontos = pygame.font.SysFont('arial', 50)


# It creates the classes
class Passaro:
    imgs = imagemPassaros
    # It creates the rotation of the images
    rotacaoMaxima = 25
    velocidadeRotacao = 20
    tempoAnimacao = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angulo = 0
        self.velocidade = 0
        self.altura = self.y
        self.tempo = 0
        self.contagemImagem = 0
        self.imagem = self.imgs[0]

    def pular(self):
        self.velocidade = -10.5
        self.tempo = 0
        self.altura = self.y

    def mover(self):
        # It calculates the displacement
        self.tempo += 1
        deslocamento = 1.5 * (self.tempo ** 2) + self.velocidade * self.tempo

        # it constrains the displacement so the bird doesn't go walking madly
        if deslocamento > 16:
            deslocamento = 16
        elif deslocamento < 0:
            deslocamento -= 2

        self.y += deslocamento

        # the angle of the bird
        # self.y is the maximum height it will go at this angle so the game doesn't look ugly
        if deslocamento < 0 or self.y < (self.altura + 50):
            if self.angulo < self.rotacaoMaxima:
                self.angulo = self.rotacaoMaxima
        else:
            if self.angulo > -90:
                self.angulo -= self.velocidadeRotacao

    def desenhar(self, tela):
        # define which bird image will use for the flapping
        self.contagemImagem += 1

        if self.contagemImagem < self.tempoAnimacao:
            self.imagem = self.imgs[0]
        elif self.contagemImagem < self.tempoAnimacao * 2:
            self.imagem = self.imgs[1]
        elif self.contagemImagem < self.tempoAnimacao * 3:
            self.imagem = self.imgs[2]
        elif self.contagemImagem < self.tempoAnimacao * 4:
            self.imagem = self.imgs[1]
        elif self.contagemImagem >= self.tempoAnimacao * 4 + 1:
            self.imagem = self.imgs[0]
            self.contagemImagem = 0

        # if the bird is falling, it doesn't need to flap its wings
        # remembering that when it goes up, the y axis is negative; when it goes down, the y-axis is positive
        if self.angulo <= -80:
            self.imagem = self.imgs[1]
            self.contagemImagem = self.tempoAnimacao * 2

        # let's draw the image
        imagemRotacionada = pygame.transform.rotate(self.imagem, self.angulo)
        # position the image to the top left, but in the center of a rectangle
        posCentroImagem = self.imagem.get_rect(topleft=(self.x, self.y)).center
        retangulo = imagemRotacionada.get_rect(center=posCentroImagem)
        # any drawing on the screen needs to use this next command
        # put the screen name in the "def draw"
        tela.blit(imagemRotacionada, retangulo.topleft)

    # create a mask so that the game reads the pixels and not the rectangle the image is inside
    def get_mask(self):
        return pygame.mask.from_surface(self.imagem)


class Cano:
    distancia = 200
    velocidade = 5

    def __init__(self, x):
        self.x = x
        self.altura = 0
        self.posTopo = 0
        self.posBase = 0
        self.canoTopo = pygame.transform.flip(imagemCano, False, True)
        self.canoBase = imagemCano
        self.passou = False
        self.definir_altura()

    def definir_altura(self):
        # create a range limit so that the pipes are not in an impossible position
        # if the screen is 800 high (indicated at the beginning of the code), we put an interval of 50 and 450
        self.altura = random.randrange(50, 450)
        # defining the size of the pipe
        self.posTopo = self.altura - self.canoTopo.get_height()
        self.posBase = self.altura + self.distancia

    # how to move the pipe
    def mover(self):
        self.x -= self.velocidade  # it is negative because on the left x-axis it is negative.

    def desenhar(self, tela):
        tela.blit(self.canoTopo, (self.x, self.posTopo))
        tela.blit(self.canoBase, (self.x, self.posBase))

    # the game needs to recognize the collision if there is one
    def colidir(self, passaro):
        passaro_mask = passaro.get_mask()
        topo_mask = pygame.mask.from_surface(self.canoTopo)
        base_mask = pygame.mask.from_surface(self.canoBase)

        # calculating the distance to the bird (which needs to be integer) and the position of the pipes
        distanciaTopo = (self.x - passaro.x, self.posTopo - round(passaro.y))
        distanciaBase = (self.x - passaro.x, self.posBase - round(passaro.y))


        # collision point
        topoPonto = passaro_mask.overlap(topo_mask, distanciaTopo)
        basePonto = passaro_mask.overlap(base_mask, distanciaBase)

        # if it touches, there is a collision; if not, there is no collision
        if basePonto or topoPonto:
            return True
        else:
            return False


class Chao:
    velocidade = 5
    largura = imagemChao.get_width()  # it says that the width of the floor is the starting point plus the width of the screen.
    imagem = imagemChao

    # using this def to create the floor and the second floor (which will be hidden until the 1st floor finishes running on screen
    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.largura

    def mover(self):
        self.x1 -= self.velocidade
        self.x2 -= self.velocidade

        # making floor 1 go back to the beginning after it has already walked the entire width of the screen
        # this cycles between floors 1 and 2
        if self.x1 + self.largura < 0:  # finished with the screen
            self.x1 = self.x2 + self.largura  # it comes back to the start
        if self.x2 + self.largura < 0:
            self.x2 = self.x1 + self.largura

    def desenhar(self, tela):
        tela.blit(self.imagem, (self.x1, self.y))
        tela.blit(self.imagem, (self.x2, self.y))


def desenhar_tela(tela, passaros, canos, chao, pontos):
    tela.blit(imagemBackground, (0, 0))
    for passaro in passaros:
        passaro.desenhar(tela)  # use this loop because there will be 1+ bird for the AI to train
    for cano in canos:
        cano.desenhar(tela)

    # creating the text of the score on the screen. The 1 is for rendering and the 255 is the white color
    texto = fontePontos.render(f"Pontuação: {pontos}", 1, (255, 255, 255))
    # the text will be on the far right 10 meters from the limit
    tela.blit(texto, (telaLargura - 10 - texto.get_width(), 10))

    if aiJogando:
        texto = fontePontos.render(f"Geração: {geracao}", 1, (255, 255, 255))
        tela.blit(texto, (10, 10))

    chao.desenhar(tela)
    # now, it will finish drawing the entire screen
    pygame.display.update()


# Create the game itself

# the function received these two parameters due to NEAT
# the genome and the config are described in the config file
def main(genomas, config):
    global geracao
    geracao += 1

    if aiJogando:
        redes = []
        listaGenomas = []
        passaros = []
        # this _ in the for is because you need to get some information, but you don't need it.
        for _, genoma in genomas:
            # this neat.nn is part of the NEAT document
            rede = neat.nn.FeedForwardNetwork.create(genoma, config)
            redes.append(rede)
            genoma.fitness = 0  # bird's score by the distance it travels
            listaGenomas.append(genoma)
            passaros.append(Passaro(230, 350)) # creating a new bird inside the for
    else:
        passaros = [Passaro(230, 350)]

    chao = Chao(730)  # to the ground, just need the y position
    canos = [Cano(700)]  # just need the x position as the y position will be random (already designated up there)
    tela = pygame.display.set_mode((telaLargura, telaAltura))
    pontos = 0
    # create the time animation (how often)
    relogio = pygame.time.Clock()

    rodando = True
    while rodando:
        relogio.tick(30)  # how many frames per second

        # how to interact with the game
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
                pygame.quit()
                quit()
            if not aiJogando:
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_SPACE:
                        for passaro in passaros:
                            passaro.pular()

        # here is to make the AI understand that the bird needs to go through the other pipe
        indiceCano = 0
        if len(passaros) > 0:
            if len(canos) > 1 and passaros[0].x > (canos[0].x + canos[0].canoTopo.get_width()):
                indiceCano = 1
        else:
            rodando = False
            break

        # takes the bird (bird) and its position (i)
        for i, passaro in enumerate(passaros):
            passaro.mover()
            # slightly increase the fitness of the bird
            listaGenomas[i].fitness += 0.1 # it will increase fitness through bird pose
            output = redes[i].activate((passaro.y,
                                       abs(passaro.y - canos[indiceCano].altura),
                                       abs(passaro.y - canos[indiceCano].posBase)))  # activating the neural network
            # rule created by NEAT: if output is > 0.5 it skips
            if output[0] > 0.5:
                passaro.pular()
        chao.mover()

        adicionarCano = False
        removerCanos = []
        for cano in canos:
            for i, passaro in enumerate(passaros):
                if cano.colidir(passaro):
                    passaros.pop(i)
                    if aiJogando:
                        listaGenomas[i].fitness -= 1  # taking a point from the AI if it crashes
                        listaGenomas.pop(i)  # removing the bird that crashed
                        redes.pop(i)
                # In this loop, I say that if a bird from that position collides, it's out.
                # now, if the bird has passed the pipe, it needs to add a new pipe
                # check if the bird's x passed the pipe's x, if so, it will be greater than the pipe's x
                # like this, add a new pipe
                if not cano.passou and passaro.x > cano.x:
                    cano.passou = True
                    adicionarCano = True
            # removing the pipe, which has passed, from the screen
            # for that, its width (x + width) needs to be > 0
            cano.mover()
            if cano.x + cano.canoTopo.get_width() < 0:
                removerCanos.append(cano)

        if adicionarCano:
            pontos += 1
            canos.append(Cano(600))  # if the bird passes the pipe, add another pipe (pos 600) and the player gains 1 pt
            # adding points if the AI bird goes through the pipe
            for genoma in listaGenomas:
                genoma.fitness += 5

        for cano in removerCanos:
            canos.remove(cano)

        # how the bird dies. If he exceeds the height limit, he will die.
        for i, passaro in enumerate(passaros):
            if (passaro.y + passaro.imagem.get_height()) > chao.y or passaro.y < 0:
                passaros.pop(i)
        # if the bird is over the limit or under the limit, it is taken out in that position (pop)
                if aiJogando:
                    listaGenomas.pop(i)
                    redes.pop(i)

        desenhar_tela(tela, passaros, canos, chao, pontos)

def rodar(caminhoConfig):
    # The parameters are the titles of the commands in the "config.txt" and the file path.
    config = neat.config.Config(neat.DefaultGenome,
                                neat.DefaultReproduction,
                                neat.DefaultSpeciesSet,
                                neat.DefaultStagnation,
                                caminhoConfig)
    populacao = neat.Population(config)
    # Generate the game statistics and generate the data
    populacao.add_reporter(neat.StdOutReporter(True))
    populacao.add_reporter(neat.StatisticsReporter())

    if aiJogando:
        populacao.run(main, 50)  # created 50 generations of birds (can be as much as you want)
    else:
        main(None, None)  # If not AI, the parameters are empty. Anyone can play.


# to start the game
if __name__ == '__main__':
    caminho = os.path.dirname(__file__)  #  here I secured NEAT file address
    caminhoConfig = os.path.join(caminho, 'config.txt')  # I put the NEAT file to guarantee the AI
    rodar(caminhoConfig)
