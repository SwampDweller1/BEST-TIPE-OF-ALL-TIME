#Importation
import numpy as np
import math
import numpy.random as random

#-----------------------------Fonction de base---------------------------------#

def normalize(v):                                                               #Normalisation d'un vecteur
    norm=np.linalg.norm(v)
    if norm==0:
       return v
    return v/norm

def g(x):
    return np.max(x, 0)

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

#-------------------------Fonctions supplémentaires----------------------------#

random.seed(123)

nbrpietons = 15
nr_experiments = 20

room_height = 600
room_width = 600
room_left = 100
room_top = 100

# Door 1
door_ytop = 385
door_ybottom = 415

# Door 2
door_ytop = 385
door_ybottom = 415

walls = [[232,232,229,363], [229,363,440,424],[440,424,232,232]]
positionmatrix = []

for j in range(0,nr_experiments):
    nr_experiment = j + 1
    agents_found = 0
    for i in range(0,nbrpietons):
        i=random.randint(0,1)                                               #Initialisation du lieu de spawn
        countwall = 0
        desiredS =  20
        mass = 80
        radius = 12/80 * mass
        if i==0:
            object_x = np.random.uniform(479,652)
            object_y = np.random.uniform(424,545)
        if i==1:
            object_x = np.random.uniform(98,177)
            object_y = np.random.uniform(353,496)

        positionmatrix.append([object_x, object_y, radius, mass, desiredS, nr_experiment])