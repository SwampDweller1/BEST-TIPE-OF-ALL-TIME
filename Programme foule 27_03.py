#Initialisation
import pygame
from pygame.locals import *
import sys
import numpy as np
import numpy.random as random
import math
import time
import matplotlib.pyplot as pyplot

nbrpietons =  int(input('Entrez le nombre de piéton(s): '))
nbrinfect= int(input('Entrez le nombre de infecté(s): '))
nr_experiments = 20
data_matrix = np.zeros((nr_experiments*nbrpietons, 4))
j = 0

#------------------------Création des positions initiales----------------------#

positionmatrix = []

for j in range(0,nr_experiments):
    nr_experiment = j + 1
    for i in range(0,nbrpietons):
        i=random.randint(0,3)                                                   #Initialisation du lieu d'apparition
        Vdes =  20
        mass = 80
        radius = 10
        if i==0:
            pieton_x = random.randint(109,236)
            pieton_y = random.randint(48,170)
        if i==1:
            pieton_x = random.randint(88,128)
            pieton_y = random.randint(386,479)
        if i==2:
            pieton_x = random.randint(505,640)
            pieton_y = random.randint(460,540)


        positionmatrix.append([pieton_x, pieton_y, radius, mass, Vdes, nr_experiment,i])

#-----------------------------Fonction de base---------------------------------#

def normalize(v):                                                               #Normalisation d'un vecteur
    norm=np.linalg.norm(v)
    if norm==0:
       return v
    return v/norm

def g(x):
    return np.max(x, 0)

def dist2(pt1,pt2):
    S=np.sqrt((pt1[1]+p2[1])**2+(pt1[2]+pt2[2])**2)
    S=S/2
    return S

def distance_pieton_obstacle(pieton, obstacle):                                 #Calcul de la distance entre un piéton et un obstacle(ligne rouge)
    p0 = np.array([obstacle[0],obstacle[1]])
    p1 = np.array([obstacle[2],obstacle[3]])
    d = p1-p0
    ymp0 = pieton-p0
    t = np.dot(d,ymp0)/np.dot(d,d)
    if t <= 0.0:
        dist = np.sqrt(np.dot(ymp0,ymp0))
        cross = p0 + t*d
    elif t >= 1.0:
        ymp1 = pieton-p1
        dist = np.sqrt(np.dot(ymp1,ymp1))
        cross = p0 + t*d
    else:
        cross = p0 + t*d
        dist = np.linalg.norm(cross-pieton)
    npw = normalize(cross-pieton)
    return dist,npw

#Initialisation

pygame.init()
clock = pygame.time.Clock()
pygame.font.init()
image = pygame.image.load("Shibuya.PNG")                                        # Importation image de fond
police = pygame.font.SysFont('monospace', 15)

# Initialisation du fond

window = pygame.display.set_mode((850, 587))                                    #Création de la fenêtre
pygame.display.update()

#----------------------------Initialisation du piéton--------------------------#

liste_pti=[[547,243],[200,500],[210,196],[331,182],[496,447],[188,193]]         #[ptimajeur1,ptimajeur2,ptimineur...]

class Pieton(object):
    def __init__(self,nbrinfect):
        self.image = pygame.image.load('cerclePIETON.png')
        self.masse = 80                                                         #Masse du piéton
        self.rayon = 10                                                         #Taille du piéton

        self.x = 1                                                              #Position en x du piéton
        self.y = 1                                                              #Position en y du piéton
        self.pos = np.array([self.x, self.y])

        self.vitesseX = 0                                                       #Vitesse du piéton en x
        self.vitesseY = 0                                                       #Vitesse du piéton en y
        self.vit_a = np.array([self.vitesseX, self.vitesseY])                   #Vitesse actuel

        self.pti=random.randint(0,2)
        self.spawn=0

        self.dest = np.array([50,50])
        self.direction = normalize(self.dest - self.pos)

        self.dvit = 12
        self.vit_d = self.dvit*self.direction                                   #Vitesse désirée

        self.acclTime = 0.5
        self.drivenAcc = (self.vit_d - self.vit_a)/self.acclTime


        self.bodyFactor = 120000
        self.F = 200                                                            #Force du piéton
        self.delta = 0.08*50

        self.time = 0.0

        if nbrinfect != 0:                                                      #Initialisation de l'état du piéton
            self.state=100
        if nbrinfect==0:
            self.state=0

        if self.state==100:
            self.image = pygame.image.load('cerclePIETONinfecte.png')
        else:
            self.image = pygame.image.load('cerclePIETON.png')

    def velocite(self):
        deltaV = self.vit_d - self.vit_a
        if np.allclose(deltaV, np.zeros(2)):
            deltaV = np.zeros(2)
        return deltaV*self.masse/self.acclTime


    def f_inter(self, pieton_2):                                                #Interactions avec les piétons
        r_ij = self.rayon + pieton_2.rayon
        d_ij = np.linalg.norm(self.pos - pieton_2.pos)
        e_ij = (self.pos - pieton_2.pos)/d_ij
        valeur = self.F*np.exp((r_ij-d_ij)/(self.delta))*e_ij
        + self.bodyFactor*g(r_ij-d_ij)*e_ij
        return valeur

    def f_obstacle(self, mur):                                                  #Interaction avec les obstacles
        r_i = self.rayon
        d_iw,e_iw = distance_pieton_obstacle(self.pos,mur)
        valeur = -10*self.F*np.exp((r_i-d_iw)/self.delta)*e_iw
        + self.bodyFactor*g(r_i-d_iw)*e_iw
        return valeur

    def maj_dest(self):
        dist = math.sqrt((self.pos[0]-liste_pti[self.pti][0])**2 + (self.pos[1]-liste_pti[self.pti][1])**2)
        self.dest = np.array([liste_pti[self.pti][0],liste_pti[self.pti][1]])


#-------------------------------Simulation-------------------------------------#

def main():

    obstacle = [[232,232,229,363], [229,363,440,424],[440,424,305,240],[305,240,232,232]
                ,[4,216,174,230],[174,230,150,331],[150,331,5,318],[5,318,4,216]
                ,[442,4,412,139],[412,139,505,156],[505,156,542,1],[542,1,442,4]
                ,[376,207,492,231],[492,231,500,256],[500,256,486,373],[486,373,376,207]
                ,[269,441,420,477],[420,477,388,582],[388,582,201,584],[201,584,269,441]
                ,[553,391,684,405],[684,405,684,305],[684,305,568,294],[568,294,553,391]
                ,[0,0,690,0],[690,0,690,585],[690,585,0,585],[0,585,0,0]]       #format : [x1,y1,x2,y2]

    pietons = []

    def positions(pieton,nbrinfect):                                            #Initialisation de la liste des piétons
        M=nbrinfect
        L=[]
        for i in range(nbrpietons):
            pieton = Pieton(M)
            if M !=0:                                                           #Ajustement du nombre d'infecté initial
                M-=1                                                            #On enlève 1 au nombre d'infecté a encore faire spawn
            pieton.spawn = positionmatrix[j*nbrpietons+i][6]
            pieton.x = positionmatrix[j*nbrpietons+i][0]
            pieton.y = positionmatrix[j*nbrpietons+i][1]
            pieton.pos = np.array([pieton.x, pieton.y])
            pieton.rayon = positionmatrix[j*nbrpietons+i][2]
            pieton.masse = positionmatrix[j*nbrpietons+i][3]
            pieton.dvit = positionmatrix[j*nbrpietons+i][4]
            pietons.append(pieton)
            while (pieton.x,pieton.y) in L:
                pieton.x+=2
                pieton.y+=2
            L.append((pieton.x,pieton.y))

    def maj_pti(i):
        if abs(i.pos[0]-liste_pti[i.pti][0]) < 10 and abs(i.pos[1]-liste_pti[i.pti][1]) < 10:
            r = random.randint(0,100)
            if r==0:                                                            #1% de chance de changer de pti à chaque itération
                i.pti=random.randint(0,2)

    positions(pietons,nbrinfect)

    count = 0
    start_time = time.time()
    run = True

#------------------------------Contagion---------------------------------------#

    Nombre_infecte=[]                                                           # Liste définie par : le premier terme est le temps et
    d=0                                                                         # deuxième terme est le nombre de contamine à cet instant
    Nombre_infecte.append([0,d])                                                #Il y a aucun contamine à l'instant 0
    temps, infecte = [], []
    temps.append(Nombre_infecte[0][0])                                          # Initialisation des listes à l'instant initial
    infecte.append(Nombre_infecte[0][1])

    prob_infect=0.05
    prob_recov=0

    def contact(L):                                                             # Fonction de contagion
        nbrcontact=0
        M=[]
        for i in L:
            for j in L:
                if (j!=i and abs(j.pos[0]-i.pos[0])<50 and abs(j.pos[1]-i.pos[1])<50 and j.state==100 and i.state<100):   #Appartient à la boule de rayon 50
                    if elapsed_time>3:
                        nbrcontact+=1
                    M.append(i)
        return [nbrcontact,M]

    wait=0
    wait2=0
    contact2=0
    contact_liste=[]

#------------------------------Simulation--------------------------------------#

    while run:

        nb_contamine=0
        window.blit(image,(0,0))                                                #Mise à jour de l'image

        if count < nbrpietons - 2:
            current_time = time.time()
            elapsed_time = current_time - start_time

        dt = clock.tick(70)/1000
        wait+=1
        wait2+=1

        for event in pygame.event.get():                                        #Avoir les coordonées du point de la souris
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                (x, y) = pygame.mouse.get_pos()
                print(x, y)

        for mur in obstacle:
            start_posw = np.array([mur[0],mur[1]])
            end_posw = np.array([mur[2],mur[3]])
            start_posx = start_posw
            end_posx = end_posw
            pygame.draw.line(window, (255,0,0), start_posx, end_posx, 3)

        if elapsed_time>1:

            if int(elapsed_time)%1==0 and wait>5:                               #Mise à jour du nombre de contact toutes les 2sec
                C=contact(pietons)
                contact2+=C[0]
                contact_liste.append(C[1])
                wait=0

            if int(elapsed_time)%3==0 and wait2>10:                             #Toutes les 3sec
                nouveauinfecte=int(prob_infect*contact2)                        #Calcul du nombre de nouveaux infectés
                for k in range(len(contact_liste)):
                    for i in contact_liste[k]:
                        if i.state<100 and nouveauinfecte!=0:
                            i.state=200                                         #state=200 -> contaminé ; state=100 -> infecte ; state<100 -> sain
                            i.image = pygame.image.load('cerclePIETONcontamine.png')
                            nouveauinfecte-=1
                contact2=0
                wait2=0
                contact_liste=[]


            for pieton in pietons:

                if pieton.state==200:                                               # On recalcule à chaque itérations le nombre d'infectés
                    nb_contamine+=1

                maj_pti(pieton)
                pieton.maj_dest()
                pieton.direction = normalize(pieton.dest - pieton.pos)
                pieton.vit_d = pieton.dvit*pieton.direction
                aVelocity_force = pieton.velocite()
                pieton_interaction = 0.0
                obstacle_interaction = 0.0

                for pieton_2 in pietons:
                    if pieton == pieton_2: continue
                    pieton_interaction += pieton.f_inter(pieton_2)

                min=20
                mur_proche=[]
                for obstacle1 in obstacle:
                    obstacle_interaction += pieton.f_obstacle(obstacle1)

                    a = distance_pieton_obstacle(pieton.pos, obstacle1)
                    a0=int(a[0])
                    if min > a0:
                        min=a0
                        mur_proche=obstacle1

                sForce = aVelocity_force + pieton_interaction + obstacle_interaction
                dv_dt = sForce/pieton.masse
                pieton.vit_a = pieton.vit_a + dv_dt*dt
                pieton.pos = pieton.pos + pieton.vit_a*dt

                if min<20 and (pieton.pti == 0 or pieton.pti == 1) and int(pieton.vit_a[0])<1 and int(pieton.vit_a[1])<1:                                                       #30 = rayon piéton +20
                    if np.sqrt(np.abs((mur_proche[0]-pieton.pos[0])**2+(mur_proche[1]-pieton.pos[1])**2)) >= np.sqrt(np.abs((mur_proche[2]-pieton.pos[0])**2+(mur_proche[3]-pieton.pos[1])**2)): #choix du sommet le plus proche avec la dist eucli
                        sommet_plus_proche=[mur_proche[2],mur_proche[3]]
                    else:
                        sommet_plus_proche=[mur_proche[0],mur_proche[1]]



                    if (sommet_plus_proche[0]-pieton.pos[0])<0 and abs(sommet_plus_proche[1]-pieton.pos[1])<20:             #redéfinission des pti
                        sommet_plus_proche[0] -= 30

                    elif (sommet_plus_proche[0]-pieton.pos[0])>0 and abs(sommet_plus_proche[1]-pieton.pos[1])<20:
                        sommet_plus_proche[0] += 30

                    elif abs(sommet_plus_proche[0]-pieton.pos[0])<20 and (sommet_plus_proche[1]-pieton.pos[1])<0:
                        sommet_plus_proche[1] -= 30

                    elif abs(sommet_plus_proche[0]-pieton.pos[0])<20 and (sommet_plus_proche[1]-pieton.pos[1])>0:
                        sommet_plus_proche[1] += 30


                    elif (sommet_plus_proche[0]-pieton.pos[0])>0 and (sommet_plus_proche[1]-pieton.pos[1])<0:
                        sommet_plus_proche[0] += 30
                        sommet_plus_proche[1] += 30

                    elif (sommet_plus_proche[0]-pieton.pos[0])<0 and (sommet_plus_proche[1]-pieton.pos[1])<0:
                        sommet_plus_proche[0] += 30
                        sommet_plus_proche[1] -= 30

                    elif (sommet_plus_proche[0]-pieton.pos[0])>0 and (sommet_plus_proche[1]-pieton.pos[1])>0:
                        sommet_plus_proche[0] -= 30
                        sommet_plus_proche[1] += 30

                    else :
                        sommet_plus_proche[0] += 30
                        sommet_plus_proche[1] += 30

                    if sommet_plus_proche not in liste_pti:
                        liste_pti.append(sommet_plus_proche)
                        pieton.save_pti = pieton.pti
                        pieton.pti = len(liste_pti)-1



        for pieton in pietons:
            window.blit(pieton.image,pieton.pos)                                #Affichage du piéton
            pieton.time += clock.get_time()/1000                                #Définition de son référentiel

        #Texte à afficher

        tempstexte = police.render("Temps écoulé: ", 1, (255, 255, 255))
        tempstexte2 = police.render(str(int(elapsed_time)) +"  minute(s)", 1, (255, 255, 255))
        window.blit(tempstexte,(695,170))
        window.blit(tempstexte2,(720,190))
        probatexte= police.render("Taux d'infection: ", 1, (255, 255, 255))
        probatexte2= police.render("Taux de guérison: ", 1, (255, 255, 255))
        window.blit(probatexte,(695,230))
        window.blit(probatexte2,(695,260))


        #Graphique

        Nombre_infecte.append([elapsed_time,nb_contamine])
        temps.append(Nombre_infecte[-1][0])
        infecte.append(Nombre_infecte[-1][1])

        pygame.display.flip()                                                   #Mise à jour de l'écran

    # Affichage du graphique

    pygame.quit()
    pyplot.title("Nombre d'infectés au cours du temps")
    pyplot.plot(temps,infecte,label="Infectés")
    pyplot.xlim(left=1.2)
    pyplot.legend()
    pyplot.show()
main()
