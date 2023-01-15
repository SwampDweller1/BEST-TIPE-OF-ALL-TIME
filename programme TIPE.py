import pygame
import numpy as np
from pygame.locals import *
from random import *
import matplotlib.pyplot as pyplot
from matplotlib.animation import FuncAnimation

##----------------- FONCTIONS PREALABLES --------------------##

def test(a):
    if a>0:
        return -1
    elif a<=0:
        return 1

##-------------------- INITIALISATION -----------------------##
pygame.init()
window = pygame.display.set_mode((850, 587))                                    # Taille de l'image de fond
clock = pygame.time.Clock()                                                     # Création de l'horloge
direction = 1                                                                   # Variable de direction
run = True
##----------------------- CLASSE ----------------------------##
class PTI(pygame.sprite.Sprite):                                                # Création de la classe des points d'interêts
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load('cerclePTI.png')
        self.rect = self.image.get_rect()
        liste=[200,500]                                                         # génération de la postion aléatoirement mais définie pour éviter les pbs
        self.rect.x = choice(liste)
        self.rect.y = choice(liste)
'''
def collide(self):                                                          # Détecter la colision avec un pixel rouge
        return  image_rouge.get_at((self.rect.x, self.rect.y))==(255, 0, 0, 255)
'''

class Player(pygame.sprite.Sprite):                                             # Création de la classe des piétons
    def __init__(self):
        super().__init__()
        self.state=randint(0,1)*10
        if self.state==0:
            self.image = pygame.image.load('cerclePIETON.png')
        if self.state==10:
            self.image = pygame.image.load('cerclePIETONinfecte.png')
        self.rect = self.image.get_rect()
        self.rect.x = randint(250,450)                                          # Position initial
        self.rect.y = randint(100,550)

    def deplacement(self):
        '''
        a=self.rect.x-M[D[i]].rect.x
        b=self.rect.y-M[D[i]].rect.y                    
        '''                           
                                                                                # Gestion des mouvement            
        if np.abs(a)<7 and np.abs(b)<7:                                         #Déplacer le piéton en quarantaine dès qu'il est trop proche du PTI
            (self.rect.x,self.rect.y)=(randint(700,830),randint(20,130))
        elif np.abs(a)<2:                                                           
            self.rect.y += test(b)
        elif np.abs(b)<2: 
            self.rect.x += test(a)
        else:
            self.rect.x += test(a)
            self.rect.y += test(b)
                                                                                # utilisation du modèle des fces centrales
    def draw(self):
        self.draw.player()                                                      # Dessiner le piéton
    def collide(self):                                                          # Détecter la colision avec un pixel rouge
        return  image_rouge.get_at((self.rect.x, self.rect.y))==(255, 0, 0, 255)

##----------------------- FONCTIONS ----------------------------##

image = pygame.image.load("Interieur.png")                                      # Importation image de fond
image_rouge = pygame.image.load("interieurred.png")                                 # Importation image rouge
pixel = np.zeros((587 , 850))                                                   # Taille de l'image
for i in range(359):
    for j in range(512):
        pixel[i,j] = image_rouge.get_at((i,j))                                  # Le pixel détecte la couleur sur laquelle il s'assoit
L=[]
for i in range(7):
    L.append(Player())                                                          # Création d'une liste de piétons (range('Nb de piéton'))
M=[]
for i in range(3):
    M.append(PTI())                                                             # Création d'une liste point d'interêt

D={}                                                                            # Dictionnaire liant les players et listes
for i in range(len(L)):
    liste=[0,1,2]
    j=choice(liste)
    D[i]=j

def ifcollide_start(N):                                                         # Tester la collision à l'instant initial
    i=0
    while i<len(N):
        if N[i].collide()==True:                                                # Si N[i] est sur un pixel rouge : on le supprime de la liste
            N.remove(N[i])
            N.append(Player())                                                  # S'il est sur un pixel rouge : on regénere le piéton jusqu'à ce
                                                                                # qu'il ne soit plus sur du rouge
        else:
            i=i+1                                                               # Si N[i] n'est pas sur un pixel rouge, la boucle while va tourner à l'infini :
                                                                                # il faut rajouter un +1 dans ce cas!
ifcollide_start(L)
'''
def ifcollide_start_PTI(M):                                                     #Tester la collision à l'instant initial du PTI
    i=0
    while i<len(M):
        if M[i].collide()==True:                                                #Si M[i] est sur un pixel rouge : on le supprime de la liste
            M.remove(M[i])
            M.append(Player())                                                  #S'il est sur un pixel rouge : on regénere le PTI jusqu'à ce
                                                                                #qu'il ne soit plus sur du rouge
        else:
            i=i+1                                                               #Si M[i] n'est pas sur un pixel rouge, la boucle while va tourner à l'infini :
                                                                                #il faut rajouter un +1 dans ce cas!
                                                                                                                                                                
ifcollide_start_PTI(M)
'''
def ifcollide_running(N):
    i=0
    while i<len(N):
        if N[i].collide()==True:                                                # Si N[i] est sur un pixel rouge lors de la simulation :
            (N[i].rect.x,N[i].rect.y)=V[i]                                      # on le fait revenir à sa position précédente
            
            a=N[i].rect.x
            b=N[i].rect.y
            m=M[0].rect.x
            if abs(b-m) <= abs(b-m)-5 and N[i].collide()==False:                # je change légèrement la valeur de la position précédente pour qu'il évite de rester coincé sur les
                N[i].rect.y += -5                                               # coins de table + je m'assure que la position d'arrivée n'est pas une position problématique
            elif abs(b-m) <= abs(b-m)+5 and N[i].collide()==False:
                N[i].rect.y += 5       

            elif abs(a-m) <= abs(a-m)-5 and N[i].collide()==False:
                N[i].rect.x += -5   
            elif abs(a-m) <= abs(a-m)+5 and N[i].collide()==False:
                N[i].rect.x += 5
            else:                                                               # sinon je contourne l'obstacle en partant en direction opposée au PTI 
                '''
                if N[i].rect.x >= N[i].rect.y:
                    '''       
                N[i].rect.x += -10*test(a-m)
                ''' 
                else:
                    N[i].rect.y += -20*test(b-m)'''                             # contournement par le haut buggé pour l'instant
                                                                   
        i=i+1

def position_save(N):                                                           # Sauvegarde de la position des piétons dans une liste
    V=[]
    for i in N:
        V.append((i.rect.x,i.rect.y))
    return(V)
position_save(L)

def interactions_pt(L):                                                         # Modélise les interactions de répultions entre piétons
    A=8
    B=-20
    for i in L:
        for j in range(len(L)):
            if L[j]!=i:
                (L[j].rect.x,L[j].rect.y) = (L[j].rect.x+A*np.exp(abs(i.rect.x-L[j].rect.x)/B),L[j].rect.y+A*np.exp(abs(i.rect.y-L[j].rect.y)/B))

smallfont = pygame.font.SysFont('stencil',25)
text = smallfont.render('Quitter' , True , (255,255,255))                       # Créer un bouton quitter


##----------------------- CONTAGION VIRUS ------------------------##

from datetime import datetime
Nombre_infecte=[]                                                               # Liste définie par : le premier terme est le temps et 
d=0                                                                             # deuxième terme est le nombre d'infecté à cet instant
for i in L:                                                         
    if i.state==10:
        d+=1
Nombre_infecte.append([0,d])                                                 
temps, infecte = [], []
temps.append(Nombre_infecte[0][0])                                              # Initialisation des listes à l'instant initial
infecte.append(Nombre_infecte[0][1])

def contagion(i):                                                               # Fonction de contagion
    for j in L:
        if j!=i and j.rect.x-i.rect.x<10 and j.rect.y-i.rect.y<10 and j.state==10 and i.state!=10:
            i.state+=1
        if i.state==10:
            i.image = pygame.image.load('cerclePIETONinfecte.png')

##----------------------- SIMULATION ------------------------##

k=0
while run:                                                                      # Boucle infinie pour notre simulation
    if k%20==0 or k==0:                                                         # On actualise la liste de position tous les 200 tours
        V=position_save(L)                                                      # pour éviter que le piéton soit trop proche de la position problématique
    window.blit(image,(0,0))                                                    # Importation de l'image de fond
    window.blit(text,(717,533))
    nb_infecte=0                                                                # Initialisation du nombre d'infecté à 0 à chaque tour de boucle
    for i in range(len(L)):                                                                 # Gestion du piéton au cours de la simulation
        if L[i].rect.x>680:
            window.blit(L[i].image,L[i].rect)
        else:
            j=D[i]
            a=L[i].rect.x-M[j].rect.x
            b=L[i].rect.y-M[j].rect.y
            L[i].deplacement()
            ifcollide_running(L)
            window.blit(L[i].image,L[i].rect)
            "interactions_pt(L)"
            contagion(L[i])
                                                         
        if L[i].state==10:
            nb_infecte+=1
    Nombre_infecte.append([k,nb_infecte])
    temps.append(Nombre_infecte[-1][0])
    infecte.append(Nombre_infecte[-1][1])

    k=k+1
    for i in M:                                                                 # Gestion des points d'intérêt au cours de la simulation
        window.blit(i.image,i.rect)

    mouse = pygame.mouse.get_pos()                                              # Position de la souris
    pygame.display.flip()                                                       # Mise à jour l'écran

    for event in pygame.event.get():                                            # Fermer la fenêtre
        if event.type == pygame.MOUSEBUTTONDOWN:
            if 700 <= mouse[0] <= 830 and 514 <= mouse[1] <= 580:               # Si on clique sur le bouton quitter
                run=False
                print("---- Fin de la simulation -----")
                pygame.quit()
        if event.type == pygame.QUIT:                                           # Si on clique sur la croix
            run=False
            print("---- Fin de la simulation -----")
            pygame.quit()

pyplot.title("Nombre d'infectés au cours du temps")
pyplot.plot(temps,infecte,label="Infectés")
pyplot.legend()
pyplot.show()

