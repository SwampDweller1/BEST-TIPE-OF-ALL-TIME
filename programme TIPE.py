import pygame
import numpy as np
from pygame.locals import *
from random import *
import matplotlib.pyplot as pyplot
from matplotlib.animation import FuncAnimation

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
        self.state=randint(0,1)
        if self.state==0:
            self.image = pygame.image.load('cerclePIETON.png')
        else:
            self.image = pygame.image.load('cerclePIETONinfecte.png')
        self.rect = self.image.get_rect()
        self.rect.x = randint(350,450)                                           #Position initial
        self.rect.y = randint(350,450)

    def deplacement(self):
        a=self.rect.x-M[0].rect.x
        b=self.rect.y-M[0].rect.y                                               # Gestion des mouvement                                             
        vitesse = b/a                   
        if np.abs(a)<7 and np.abs(b)<7:                                         #Déplacer le piéton en quarantaine dès qu'il est trop proche du PTI
            (self.rect.x,self.rect.y)=(randint(700,830),randint(20,130))
        self.rect.x += testx(a)
        self.rect.y += testx(b)*vitesse
                                                                                # utilisation du modèle des fces centrales
    def draw(self):
        self.draw.player()                                                      # Dessiner le piéton
    def collide(self):                                                          # Détecter la colision avec un pixel rouge
        return  image_rouge.get_at((self.rect.x, self.rect.y))==(255, 0, 0, 255)

##----------------------- FONCTIONS ----------------------------##

image = pygame.image.load("Interieur.png")                                        # Importation image de fond
image_rouge = pygame.image.load("Interieurred.png")                               # Importation image rouge
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
        i=i+1

def position_save(N):                                                           #Sauvegarde de la position des piétons dans une liste
    V=[]
    for i in N:
        V.append((i.rect.x,i.rect.y))
    return(V)
position_save(L)

def interactions_pt(L):                                                         # Modélise les interactions de répultions entre piétons
    A=10
    B=-3
    for i in L:
        for j in range(len(L)):
            if L[j]!=i:
                (L[j].rect.x,L[j].rect.y) = (L[j].rect.x+A*np.exp(abs(i.rect.x-L[j].rect.x)/B),L[j].rect.y+A*np.exp(abs(i.rect.y-L[j].rect.y)/B))

smallfont = pygame.font.SysFont('stencil',25)
text = smallfont.render('Quitter' , True , (255,255,255))                       #Créer un bouton quitter


##----------------------- CONTAGION VIRUS ------------------------##

from datetime import datetime
Nombre_infecte=[]                                                               #Liste définie par : le premier terme est le temps et 
d=0                                                                             #deuxième terme est le nombre d'infecté à cet instant
for i in L:                                                         
    if i.state==1:
        d+=1
Nombre_infecte.append([0,d])
temps, infecte = [], []
temps.append(Nombre_infecte[0][0])
infecte.append(Nombre_infecte[0][1])

##----------------------- SIMULATION ------------------------##

k=0
while run:                                                                      # Boucle infinie pour notre simulation
    if k%20==0 or k==0:                                                         # On actualise la liste de position tous les 200 tours
        V=position_save(L)                                                      # pour éviter que le piéton soit trop proche de la position problématique
    window.blit(image,(0,0))                                                    # Importation de l'image de fond
    window.blit(text,(717,533))
    nb_infecte=0                                                                #Initialisation du nombre d'infecté à 0 à chaque tour de boucle
    for i in L:                                                                 # Gestion du piéton au cours de la simulation
        if i.rect.x>680:
            window.blit(i.image,i.rect)
        else:
            i.deplacement()
            ifcollide_running(L)
            window.blit(i.image,i.rect)
            '''interactions_pt(L)'''
                                                         
        if i.state==1:
            nb_infecte+=1
    Nombre_infecte.append([k,nb_infecte])
    print(Nombre_infecte)
    temps.append(Nombre_infecte[-1][0])
    infecte.append(Nombre_infecte[-1][1])

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

pyplot.scatter(temps,infecte)
pyplot.show()

