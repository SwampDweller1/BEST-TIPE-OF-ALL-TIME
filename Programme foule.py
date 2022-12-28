import pygame
import numpy as np
from pygame.locals import *
from random import *

#test

##-------------------------------- INITIALISATION --------------------------------##

pygame.init()
window = pygame.display.set_mode((891, 625))        # Taille de l'image de fond
clock = pygame.time.Clock()                         # Création de l'horloge
direction = 1                                       # Variable de direction
player_rect = Rect(100, 100, 50, 50)
speed_x = 5 #Vitesse initiale
speed_y = 4
run = True

##------------------- CLASSE / FONCTIONS --------------------##

class Player(pygame.sprite.Sprite):

    def __init__(self):
        super().__init__()
        self.image = pygame.image.load('cerclebis.png')
        self.rect = self.image.get_rect()
        self.rect.x = randint(0,880)               #Position initial
        self.rect.y = randint(0,620)
        self.velocity = uniform(-1,1)              #Génère des nombres REELS aléatoire

    def deplacement(self):                         # Gestion des mouvements
        self.rect.x -=  self.velocity + uniform(-0.5,0.5)
        self.rect.y -=  self.velocity + uniform(-0.5,0.5)

    def draw(self):
        self.draw.player()                         # Dessiner le piéton

    def collide(self):                             # Détecter la colision avec un pixel rouge
        return  image_rouge.get_at((self.rect.x, self.rect.y))==(255, 0, 0, 255)

image = pygame.image.load("FOND.png")               # Importation image de fond
image_rouge = pygame.image.load("rue.png")         # Importation image rouge

pixel = np.zeros((625 , 891))

for i in range(359):
    for j in range(512):
        pixel[i,j] = image_rouge.get_at((i,j))

L=[]
for i in range(1):
    L.append(Player())                              #Création d'une liste de piétons

print(len(L))

def ifcollide_start(N):                             #Tester la collision à l'instant initial
    i=0
    while i<len(N):
        if N[i].collide()==True:                    #Si N[i] est sur un pixel rouge : on le supprime de la liste
            N.remove(N[i])
            N.append(Player())                      #S'il est sur un pixel rouge : on regénere le piéton jusqu'à ce qu'il ne soit plus
                                                    #sur du rouge
        else:
            i=i+1                                   #Si N[i] n'est pas sur un pixel rouge, la boucle while va tourner à l'infini :
                                                    #il faut rajouter un +1 dans ce cas!

ifcollide_start(L)

def ifcollide_running(N):
    i=0
    while i<len(N):
        if N[i].collide()==True:                               #Si N[i] est sur un pixel rouge lors de la simulation :
            (N[i].rect.x,N[i].rect.y)=V[i]                     #     on le fait revenir à sa position précédente
            N[i].velocity =  N[i].velocity  ####              #  ici on veut lui faire changer légèrement de vitesse et surtout de direction
        i=i+1                                                # note : jsp comment lui donner une direction vers un point d'intérêt

def position_save(N):
    M=[]
    for i in N:
        M.append((i.rect.x,i.rect.y))
    return(M)

position_save(L)

##----------------------- SIMULATION ------------------------##
k=0
while run:                                           # Boucle infinie pour notre simulation
    clock.tick(60)                                   # Nombres de fps
    window.blit(image,(0,0))                         # Fond
    for i in L:
        i.deplacement()
        ifcollide_running(L)
        window.blit(i.image,i.rect)                  # Image du joueur au joueur

    if k%200==0 or k==0:                             # On actualise la liste de position tous les 200 tours
        V=position_save(L)                           # pour éviter que le piéton soit trop proche de la position problématique
    k=k+1


    for event in pygame.event.get():                 # Fermer la fenêtre
        if event.type == pygame.QUIT:
            run=False
            pygame.quit()
            print("----Fermeture de la simulation -----")

    pygame.display.flip()                            # Mise à jour l'écran