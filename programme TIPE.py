import pygame
import numpy as np
from pygame.locals import *
from random import *
import matplotlib.pyplot as plt

##----------------- FONCTIONS PREALABLES --------------------##
def testx(a):
    if a>0:
        return -1
    elif a<=0:
        return 1
def testy(b):
    if b>0:
        return (-2)
    elif b<=0:
        return 2

##-------------------- INITIALISATION -----------------------##
pygame.init()
window = pygame.display.set_mode((850, 587))                                    # Taille de l'image de fond
clock = pygame.time.Clock()                                                     # Création de l'horloge
direction = 1                                                                   # Variable de direction
run = True
##----------------------- CLASSE ----------------------------##
class PTI(pygame.sprite.Sprite):                                                #Création de la classe des points d'interêts
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load('cerclePTI.png')
        self.rect = self.image.get_rect()
        self.rect.x = 500
        self.rect.y = 500

class Player(pygame.sprite.Sprite):                                             #Création de la classe des piétons
    def __init__(self):
        super().__init__()
        state=randint(0,1)
        if state==0:
            self.image = pygame.image.load('cerclePIETON.png')
        else:
            self.image = pygame.image.load('cerclePIETONinfecte.png')
        self.rect = self.image.get_rect()
        self.rect.x = randint(350,450)                                           #Position initial
        self.rect.y = randint(350,450)

    def deplacement(self):
        a=self.rect.x-M[0].rect.x
        b=self.rect.y-M[0].rect.y                                               # Gestion des mouvements
        if abs(a)<3 and abs(b)<3:                                               # Si le point est assez proche il s'arrête
            self.rect.x=self.rect.x
            self.rect.y=self.rect.y
        else:                                                                   # Mvt si le point d'intérêt n'est pas atteint
            vitesse = b/a
            p,q=direction(L,M)
            self.rect.x += testx(p)
            self.rect.y += testx(p)*vitesse
                                                                                # utilisation du modèle des fces centrales
    def draw(self):
        self.draw.player()                                                      # Dessiner le piéton
    def collide(self):                                                          # Détecter la colision avec un pixel rouge
        return  image_rouge.get_at((self.rect.x, self.rect.y))==(255, 0, 0, 255)

##----------------------- FONCTIONS ----------------------------##
image = pygame.image.load("Shibuya.PNG")                                        # Importation image de fond
image_rouge = pygame.image.load("Shibuyared.png")                               # Importation image rouge
pixel = np.zeros((587 , 850))                                                   # Taille de l'image
for i in range(359):
    for j in range(512):
        pixel[i,j] = image_rouge.get_at((i,j))                                  # Le pixel détecte la couleur sur laquelle il s'assoit
L=[]
for i in range(7):
    L.append(Player())                                                          #Création d'une liste de piétons (range('Nb de piéton'))
M=[]
for i in range(1):
    M.append(PTI())                                                             #Création d'une liste point d'interêt

def ifcollide_start(N):                                                         #Tester la collision à l'instant initial
    i=0
    while i<len(N):
        if N[i].collide()==True:                                                #Si N[i] est sur un pixel rouge : on le supprime de la liste
            N.remove(N[i])
            N.append(Player())                                                  #S'il est sur un pixel rouge : on regénere le piéton jusqu'à ce
                                                                                #qu'il ne soit plus sur du rouge
        else:
            i=i+1                                                               #Si N[i] n'est pas sur un pixel rouge, la boucle while va tourner à l'infini :
                                                                                #il faut rajouter un +1 dans ce cas!
ifcollide_start(L)

def ifcollide_running(N):
    i=0
    while i<len(N):
        if N[i].collide()==True:                                                #Si N[i] est sur un pixel rouge lors de la simulation :
            (N[i].rect.x,N[i].rect.y)=V[i]                                      #     on le fait revenir à sa position précédente
            N[i].velocity= randint(-1,1)
        i=i+1

def position_save(N):                                                           #Sauvegarde de la position des piétons dans une liste
    V=[]
    for i in N:
        V.append((i.rect.x,i.rect.y))
    return(V)
position_save(L)

def direction(L,M):                                                             #Comparaison entre la position des piétons et le PTI
    u=M[0]
    for i in range(len(L)):
        a=L[i].rect.x-u.rect.x
        b=L[i].rect.y-u.rect.y
        if np.abs(a)<5 and np.abs(b)<5:                                         #Supprime le piéton dès qu'il est trop proche du PTI
            (L[i].rect.x,L[i].rect.y)=(randint(700,830),randint(20,130))
    return a,b
direction(L,M)

def interactions_pt(L):                                                         # Modélise les interactions de répultions entre piétons
    A=10
    B=-3
    for i in L:
        for j in range(len(L)):
            if L[j]!=i:
                (L[j].rect.x,L[j].rect.y) = (L[j].rect.x+A*np.exp(abs(i.rect.x-L[j].rect.x)/B),L[j].rect.y+A*np.exp(abs(i.rect.y-L[j].rect.y)/B))

smallfont = pygame.font.SysFont('stencil',25)
text = smallfont.render('Quitter' , True , (255,255,255))                       #Créer un bouton quitter


##----------------------- INITIALISATION DES GRAPHES ------------------------##

from datetime import datetime
from matplotlib import pyplot
from matplotlib.animation import FuncAnimation
from random import randrange

x_data, y_data = [], []

figure = pyplot.figure()
line, = pyplot.plot_date(x_data, y_data, '-')

def update(frame):
    x_data.append(datetime.now())
    y_data.append(randrange(0, 100))
    line.set_data(x_data, y_data)
    figure.gca().relim()
    figure.gca().autoscale_view()
    return line,

animation = FuncAnimation(figure, update, interval=200)

pyplot.show()


##----------------------- SIMULATION ------------------------##

k=0
while run:                                                                      # Boucle infinie pour notre simulation
    if k%20==0 or k==0:                                                         # On actualise la liste de position tous les 200 tours
        V=position_save(L)                                                      # pour éviter que le piéton soit trop proche de la position problématique
    window.blit(image,(0,0))                                                    # Importation de l'image de fond
    window.blit(text,(717,533))
    for i in L:                                                                 # Gestion du piéton au cours de la simulation
        if i.rect.x>680:
            window.blit(i.image,i.rect)
        else:
            i.deplacement()
            ifcollide_running(L)
            window.blit(i.image,i.rect)
            interactions_pt(L)
    k=k+1
    for i in M:                                                                 # Gestion des points d'intérêt au cours de la simulation
        window.blit(i.image,i.rect)

    mouse = pygame.mouse.get_pos()                                              #Position de la souris
    pygame.display.flip()                                                       # Mise à jour l'écran

    for event in pygame.event.get():                                            # Fermer la fenêtre
        if event.type == pygame.MOUSEBUTTONDOWN:
            if 700 <= mouse[0] <= 830 and 514 <= mouse[1] <= 580:               #Si on clique sur le bouton quitter
                run=False
                print("---- Fin de la simulation -----")
                pygame.quit()
        if event.type == pygame.QUIT:                                           #Si on clique sur la croix
            run=False
            print("---- Fin de la simulation -----")
            pygame.quit()
