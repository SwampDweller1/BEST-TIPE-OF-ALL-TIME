import pygame
import numpy as np
from pygame.locals import *
from random import *
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
window = pygame.display.set_mode((891, 625))                                    # Taille de l'image de fond
clock = pygame.time.Clock()                                                     # Création de l'horloge
direction = 1                                                                   # Variable de direction
run = True
##----------------------- CLASSE ----------------------------##
class PTI(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load('cerclePTI.png')
        self.rect = self.image.get_rect()
        self.rect.x = 500
        self.rect.y = 500
class Player(pygame.sprite.Sprite):

    def __init__(self):
        super().__init__()
        self.image = pygame.image.load('cerclebis2.png')
        self.rect = self.image.get_rect()
        self.rect.x = randint(20,400)                                          #Position initial
        self.rect.y = randint(20,400)

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
image = pygame.image.load("Fondtest.png")                                       # Importation image de fond
image_rouge = pygame.image.load("Fondtest.png")                                 # Importation image rouge
pixel = np.zeros((625 , 891))
for i in range(359):
    for j in range(512):
        pixel[i,j] = image_rouge.get_at((i,j))                                  # Le pixel détecte la couleur sur laquelle il s'assoit
L=[]
for i in range(10):
    L.append(Player())                                                          #Création d'une liste de piétons
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
    return a,b

direction(L,M)
def interactions_pt(L):                                                         #modifier intéraction pour mettre le modèles des FC
    for i in L:
        for j in range(len(L)):
            if abs(i.rect.x-L[j].rect.x)<5 and abs(i.rect.y-L[j].rect.y)<5 and i!=L[j]:
                L[j].rect.x,L[j].rect.y = V[j]

def repulsion_pt(L):                                                            #ici on peut modéliser le mouvement des piétons entre eux et ajouter plus tard une chance de contamination
    for i in L:
        for j in range(len(L)):
            if i!=L[j]:
                if i.rect.x != L[j].rect.x and i.rect.y != L[j].rect.y:
                    L[j].rect.x= L[j].rect.x + int(10/(abs(L[j].rect.x-i.rect.x) + abs(L[j].rect.y-i.rect.y)))
                    L[j].rect.y= L[j].rect.y + int(10/(abs(L[j].rect.x-i.rect.x) + abs(L[j].rect.y-i.rect.y)))


"""            if i.rect.x != L[j].rect.x and i.rect.y != L[j].rect.y:"""


##----------------------- SIMULATION ------------------------##
k=0
while run:                                                                      # Boucle infinie pour notre simulation
    if k%20==0 or k==0:                                                         # On actualise la liste de position tous les 200 tours
        V=position_save(L)                                                      # pour éviter que le piéton soit trop proche de la position problématique
    window.blit(image,(0,0))                                                    # Importation de l'image de fond
    for i in L:                                                                 # Gestion du piéton au cours de la simulation
        i.deplacement()
        ifcollide_running(L)
        window.blit(i.image,i.rect)
        interactions_pt(L)
        repulsion_pt(L)
    k=k+1
    for i in M:                                                                 # Gestion des points d'intérêt au cours de la simulation
        window.blit(i.image,i.rect)

    for event in pygame.event.get():                                            # Fermer la fenêtre
        if event.type == pygame.QUIT:
            run=False
            print("----Fin de la simulation -----")
            pygame.quit()

    pygame.display.flip()                                                       # Mise à jour l'écran
