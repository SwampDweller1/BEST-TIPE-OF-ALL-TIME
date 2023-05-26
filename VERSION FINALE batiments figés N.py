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
proba_init=float(input('Entrez la probabilité de contamination: '))
prox_spat= int(input('Entrez la proximité spatiale (distance sociale): (usuel:10) '))
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
        radius = prox_spat
        if i==0:
            pieton_x = random.randint(19,236)
            pieton_y = random.randint(18,170)
        if i==1:
            pieton_x = random.randint(18,128)
            pieton_y = random.randint(386,740)
        if i==2:
            pieton_x = random.randint(505,740)
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

def restore(pieton):
    if pieton.pti == 0:
        pieton.pos[0]=random.randint(870,900)
        pieton.pos[1]=random.randint(70,130)
        pieton.pti = 4

    elif pieton.pti == 1:
        pieton.pos[0]=random.randint(870,900)
        pieton.pos[1]=random.randint(270,330)
        pieton.pti = 5

    elif pieton.pti == 3:
        pieton.pos[0]=random.randint(870,900)
        pieton.pos[1]=random.randint(460,520)
        pieton.pti = 6

#Initialisation

pygame.init()
clock = pygame.time.Clock()
pygame.font.init()
image = pygame.image.load("Shibuyabisbis.PNG")                                  # Importation image de fond
police = pygame.font.SysFont('monospace', 15)

# Initialisation du fond

window = pygame.display.set_mode((1021, 588))                                    #Création de la fenêtre
pygame.display.update()

#----------------------------Initialisation du piéton--------------------------#

liste_pti=[[547,243],[200,500],[564,500],[140,100],[939,101],[939,290],[939,490]]                             #[ptimajeur1,ptimajeur2,ptimineur...]

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

        self.pti=random.randint(0,4)
        self.pti_int=self.pti
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

        self.temps_passe = 0                                                    #temps passé dans un bâtiment

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
        dist = math.sqrt((self.pos[0]-liste_pti[self.pti_int][0])**2 + (self.pos[1]-liste_pti[self.pti_int][1])**2)
        self.dest = np.array([liste_pti[self.pti_int][0],liste_pti[self.pti_int][1]])


#-------------------------------Simulation-------------------------------------#

def main():

    topologiex=[]
    topologiey=[]
    obstacle = [[4,216,174,230],[174,230,150,331],[150,331,5,318],[269,441,420,477],
    [201,584,269,441],[420,477,388,582],[553,391,684,405],[568,294,553,391],
    [684,305,568,294],[505,156,542,1],[412,139,505,156],[442,4,412,139],[232,232,234,379],
    [234,379,408,402],[408,402,305,240],[305,240,232,232],[376,207,492,231],[492,231,500,256],
    [500,256,486,373],[486,373,376,207],[852,4,1017,4],[1017,4,1017,195],[1017,195,1017,390],
    [1017,390,1017,584],[1017,390,852,584],[852,584,852,390],[852,390,852,195],[852,195,852,4],
    [854,200,1017,200],[854,400,1017,400],[854,170,1017,170],[854,370,1017,370]]       #format : [x1,y1,x2,y2]

    checkpoint={(0,1): (190,230), (0,2): (190,230),(1,1):(213,231),(1,2): (190,230),(2,1) : (178,337),
    (2,2): (178,337),(3,1) : (249,407),(3,2): (446,457),(4,1): (493,397),(4,2): (359,194),(5,1):(446,457),
    (5,2):(446,457),(6,1):(530,405),(6,2) : (530,405),(7,1):(554,273),(7,2):(530,405),(8,1):(554,273),
    (8,2): (554,273), (9,1):(521,176),(9,2):(521,176),(10,1) : (393,150),(10,2): (521,176),(11,1):(393,150),
    (11,2) : (393,150), (12,1):(220,215),(12,2): (208,377),(13,1):(208,377),(13,2) : (491,449),(14,1) : (491,449),
    (14,2) : (310,210), (15,1):(310, 210), (15,2) : (220,215), (16,1): (357,196),(16,2): (507,218), (17,1):(507,218),
    (17,2):(513,255),(18,1): (513,255),(18,2):(492,394),(19,1) : (492,394), (19,2):(357,196),            (20,1):(933,19),(20,2):(933,19),
    (21,1) : (995,96),(21,2) : (995,96),(22,1) : (995,300),(22,2) : (995,300),(23,1) : (995,490),(23,2) : (995,490),
    (24,1) : (930,564),(24,2) : (930,564),(25,1) : (873,495),(25,2) : (873,495),(26,1) : (873,290),(26,2) : (873,290),
    (27,1) : (873,100),(27,2) : (873,100),(28,1) : (931,222),(28,2) : (931,222),(29,1) : (931,407),(29,2) : (931,407),
    (30,1) : (931,160),(30,2) : (931,160),(31,1) : (931,360),(31,2) : (931,360)}

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

    def maj_pti(pieton):
        if abs(pieton.pos[0]-liste_pti[pieton.pti][0]) < 30 and abs(pieton.pos[1]-liste_pti[pieton.pti][1]) <30 and pieton.pti != 4 and pieton.pti != 5 and pieton.pti != 6:
            r = random.randint(0,1000)
            if r<=20:                                                            #0.2% de chance de changer de pti à chaque itération
                pieton.pti_int=random.randint(0,4)
            if r>=980:
                restore(pieton)

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

    prob_infect=proba_init
    prob_recov=0

    def contact(L):
        nbrcontact = 0
        M = []
        if elapsed_time > 30:
            for i in L:
                if i.state < 100:
                    for j in L:
                        if (j != i and abs(j.pos[0] - i.pos[0]) < 50 and abs(j.pos[1] - i.pos[1]) < 50 and j.state == 100 and j.pos[0]<852):
                            nbrcontact += 1
                            M.append(i)
                        elif (j != i and abs(j.pos[0] - i.pos[0]) < 2*50 and abs(j.pos[1] - i.pos[1]) < 2*50 and j.state == 100 and j.pos[0]>852):
                            nbrcontact += 2
                            M.append(i)
        return [nbrcontact, M]

    #Paramètres

    wait=0
    wait2=0
    contact2=0
    contact_liste=[]


#------------------------------Simulation--------------------------------------#
    while run:

        nb_contamine=0
        window.blit(image,(0,0))                                                #Mise à jour de l'image

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

        if elapsed_time>1:                                                      #On attend de lancer le programme pour éviter les bugs d'initialisation

            if int(elapsed_time)%1==0 and wait>5 and elapsed_time>30:                               #Mise à jour du nombre de contact toutes les 2sec
                C=contact(pietons)
                contact2+=C[0]
                contact_liste.append(C[1])
                wait=0

            if int(elapsed_time)%3==0 and wait2>5 and elapsed_time>30:                             #Toutes les 3sec
                nouveauinfecte=int(prob_infect*contact2)                        #Calcul du nombre de nouveaux infectés
                for k in range(len(contact_liste)):
                    for i in contact_liste[k]:
                        if i.state<100 and nouveauinfecte!=0:
                            i.state=200                                         #state=200 -> contaminé ; state=100 -> infecte ; state<100 -> sain
                            i.image = pygame.image.load('cerclePIETONcontamine.png')
                            topologiex.append(i.pos[0])
                            topologiey.append(i.pos[1])
                            nouveauinfecte-=1
                contact2=0
                wait2=0
                contact_liste=[]

            for pieton in pietons:

                if pieton.state==200 and elapsed_time>30:                                               # On recalcule à chaque itérations le nombre d'infectés
                    nb_contamine+=1

                temps_dans_le_batiment=random.randint(50,60)                    #à changer à ta guise

                if pieton.pos[0]>853 and pieton.temps_passe == 0:
                    pieton.temps_passe = elapsed_time

                if (elapsed_time-pieton.temps_passe)>temps_dans_le_batiment and pieton.pos[1]<200 and pieton.pos[0]>853 :
                    pieton.temps_passe = 0
                    pieton.pti_int = random.randint(0,4)
                    pieton.pti = random.randint(0,4)
                    pieton.pos[0]=random.randint(518,578)
                    pieton.pos[1]=random.randint(185,245)

                if (elapsed_time-pieton.temps_passe)>temps_dans_le_batiment and pieton.pos[1]>200 and pieton.pos[1]<370 and pieton.pos[0]>853:
                    pieton.temps_passe = 0
                    pieton.pti_int = random.randint(0,4)
                    pieton.pti = random.randint(0,4)
                    pieton.pos[0]=random.randint(157,217)
                    pieton.pos[1]=random.randint(450,510)

                if (elapsed_time-pieton.temps_passe)>temps_dans_le_batiment and pieton.pos[1]>370 and pieton.pos[0]>853:
                    pieton.temps_passe = 0
                    pieton.pti_int = random.randint(0,4)
                    pieton.pti = random.randint(0,4)
                    pieton.pos[0]=random.randint(535,595)
                    pieton.pos[1]=random.randint(470,530)

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

                min_mur=20                                                      #Distance réglementaire à un mur

                for obstacle1 in obstacle:
                    obstacle_interaction += pieton.f_obstacle(obstacle1)
                    a0 = int(distance_pieton_obstacle(pieton.pos, obstacle1)[0])
                    if min_mur > a0:
                        min_mur=a0                                              #Si le piéton est trop proche du mur
                        mur_proche=obstacle1                                    #On ajoute le mur à la liste des murs trop proches

                sForce = aVelocity_force + pieton_interaction + obstacle_interaction
                dv_dt = sForce/pieton.masse
                pieton.vit_a = pieton.vit_a + dv_dt*dt
                pieton.pos = pieton.pos + pieton.vit_a*dt
                if min_mur<20:
                    pos_list_mur=obstacle.index(mur_proche)
                    if np.abs((mur_proche[0]-pieton.pos[0])**2+(mur_proche[1]-pieton.pos[1])**2) <= np.abs((mur_proche[2]-pieton.pos[0])**2+(mur_proche[3]-pieton.pos[1])**2) and abs(pieton.vit_a[0])<=3 and abs(pieton.vit_a[1])<=3: #choix du sommet le plus proche avec la dist eucli
                        checkpoint_pos=checkpoint[(pos_list_mur,1)]
                    elif abs(pieton.vit_a[0])<=3 and abs(pieton.vit_a[1])<=3:                                                       #Choix du checkpoint optimal pour contourner l'obstacle
                        checkpoint_pos=checkpoint[(pos_list_mur,2)]
                    else :
                        checkpoint_pos=liste_pti[pieton.pti_int]
                    if checkpoint_pos not in liste_pti:
                        liste_pti.append(checkpoint_pos)

                    pieton.pti_int=liste_pti.index(checkpoint_pos)

                if np.sqrt(np.abs((liste_pti[pieton.pti_int][0]-pieton.pos[0])**2+(liste_pti[pieton.pti_int][1]-pieton.pos[1])**2)) <= 10:
                    pieton.pti_int=pieton.pti

        for pieton in pietons:
            window.blit(pieton.image,pieton.pos)                                #Affichage du piéton
            pieton.time += clock.get_time()/1000                                #Définition de son référentiel

        #Texte à afficher

        tempstexte = police.render("Temps écoulé: ", 1, (255, 255, 255))
        tempstexte2 = police.render(str(int(elapsed_time)) +"  minute(s)", 1, (255, 255, 255))
        window.blit(tempstexte,(695,170))
        window.blit(tempstexte2,(720,190))
        probatexte= police.render("Taux d'infection: ", 1, (255, 255, 255))
        tau_infec=round(Nombre_infecte[-1][1]/(len(pietons))*100,2)
        probachiffrei= police.render(str(tau_infec)+"%", 1, (255, 255, 255))
        window.blit(probatexte,(695,230))
        window.blit(probachiffrei,(725,250))

        #Graphique

        Nombre_infecte.append([elapsed_time,nb_contamine])
        temps.append(Nombre_infecte[-1][0])
        infecte.append(Nombre_infecte[-1][1])

        pygame.display.flip()                                                   #Mise à jour de l'écran

    # Affichage du graphique

    pygame.quit()
    pyplot.title("Nombre de contaminés au cours du temps")
    pyplot.plot(temps,infecte,label="Contaminés")
    img = pyplot.imread("Shibuyabisbis.PNG")
    fig, ax = pyplot.subplots()
    ax.imshow(img)
    ax.scatter(topologiex,topologiey,s=10,color='orange',edgecolors="black")
    pyplot.xlim(left=15)
    pyplot.legend()
    pyplot.show()
main()