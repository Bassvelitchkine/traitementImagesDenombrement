## L'idée ici est de modifier nous-même les photos avec une interface Tkinter, simplement pour l'adaptive threshold
##Ensuite, on fait le calcul du nombre d'objets. Pour déterminer l'aire moyenne d'un objet, on trouve les composantes connexes dans limage et on regarde quelles sont les trois tailles les plus représentées de ces composantes connexes.
##On prend la moyenne pondérées par le nombre d'occurences de ces trois tailles de composantes.

##Par ailleurs, il arrive que certaines composantes soient le résultat d'un groupement d'objets, donc qu'elles soient plus proche d'un multiple de la surface que d'un autre. Dans ce cas, on prend le multiple le plus proche comme valeur pour le nombre d'objets à compter présents dans la composante.
from tkinter import *
from tkinter import filedialog as fd
import PIL
from PIL import Image, ImageTk
import numpy as np
import cv2
from win32api import GetSystemMetrics
import scipy.ndimage as ndimage
import mahotas as mh

##On se préoccupe de toutes les fonctions qui nous aideront à des fins de calcul

def voisins(image,coordonnees):
    """
    Input: np.array, tuple of ints
    Output: np.array (1D)
    La fonction prend en argument une image ainsi que les coordonnées d'un des pixels de l'image (sous forme de numpy array). Elle retourne les voisins de ce pixel, à savoir les pixels qui lui sont adjacents et qui ont les mêmes valeurs.
    """
    nombreLignes=image.shape[0]-1
    nombreColonnes=image.shape[1]-1
    
    (ligne,colonne)=coordonnees
    valeur=image[ligne,colonne]
    neighbors=[]
    
    if ligne!=0 and image[ligne-1,colonne]==valeur:
        neighbors.append((ligne-1,colonne))
    if ligne!=nombreLignes and image[ligne+1,colonne]==valeur:
        neighbors.append((ligne+1,colonne))
    if colonne!=0 and image[ligne,colonne-1]==valeur:
        neighbors.append((ligne,colonne-1))
    if colonne!=nombreColonnes and image[ligne,colonne+1]==valeur:
        neighbors.append((ligne,colonne+1))
        
    return neighbors

#On créé une fonction de parcours en largeur d'une image. Les sommets sont les pixels, et les voisins d'un sommet sont ses pixels adjacents qui ont la même couleur
def bfs(dico,image, coordonnees):
    """
    Input: dict, np.array, tuple of ints
    Output: np.array (1D)
    La fonction prend en argument le dictionnaire de tous les sommets dont les valeurs sont None une image sous forme de numpy array ainsi que les coordonnées entières du sommet de départ et elle retourne le nombre de sommets parcourus, après un parcours en largeur.
    """
    
    #La liste résultat
    res=1
    #On va implémenter a_voir comme une file ou les premiers éléments qui sortent sont à droite de la liste
    a_voir=[coordonnees]
    
    while a_voir!=[]:
        point=a_voir.pop()
        dico[point]=1
        neighbors=voisins(image,point)
        for voisin in neighbors:
            if dico[voisin]==None:
                res+=1
                dico[voisin]=1
                a_voir=[voisin]+a_voir
    
    return res

#Maintenant on applique l'algorithme des composante connexes, ce qui nous intéresse est en fait la taille en pixel de chaque composante
def connected_components_sizes(image):
    """
    Input: numpy array
    Output: list of ints
    La fonction prend en agument une image sous forme de tabeau numpy et retourne la liste des tailles en pixels des composantes connexes du graphe. L'image est supposée être en noir et blanc et on ne considère que les composantes connexes blanches.
    """
    res=[]
    dico_sommets={}
    liste_sommets=[]
    
    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            if image[i,j]==255: #On ne veut visiter que les sommets blancs
                dico_sommets[(i,j)]=None
                liste_sommets.append((i,j))
            else:
                dico_sommets[(i,j)]=1
    
    for sommet in liste_sommets:
        if dico_sommets[sommet]==None:
            res.append(bfs(dico_sommets,image,sommet))
    
    return res

#On veut une fonction qui à un nombre et un flottant associe le multiple du flottant le plus près du nombre
def nearest_multiple(nombre,aire):
    """
    Input: int, float
    Output: int
    La fonction retourne l'entier td entier*aire est le plus proche possible de nombre.
    """
    multiple=nombre/aire
    res_temp=int(round(multiple,0))
    if res_temp == 0:
        return 1
    else:
        return res_temp

#On veut une fonction qui à la liste des tailles en pixels des composantes connexes associe le nombre total de larves sur l'image
#La principe est le suivant, on a au préalable déterminé l'aire moyenne en pixel**2 d'un objet sur une image, ainsi pour chaque composante connexe, on prend le multiple de l'aire le plus proche du nombre de pixels de la composante
def number_items(liste_tailles, aire):
    """
    Input: list of ints, float
    Output: int
    La fonction prend en argument la liste des tailles des composantes connexes ainsi que l'aire moyenne d'un objet et retourne le nombre d'objets total estimé sur toutes es composantes connexes.
    """
    nombre=0
    for taille in liste_tailles:
        nombre+=nearest_multiple(taille,aire)
    return nombre

#Pour finir il faut une fonction qui prend en argument une image et une aire et qui retourne le nombre d'items présents sur l'image
def items(image,aire):
    """
    Inut: numpy array, float
    Output: int
    La fonction prend en argument une image sous forme d'array numpy ainsi que l'aire moyenne des objets sur l'image. Elle retourne le nombre d'objets présents sur l'image.
    """
    return number_items(connected_components_sizes(image),aire)

def takeSecond(tupl):
    """
    Input: tuple
    Output: float
    La fonction prend en argument un couple et retourne le deuxième élément du couple.
    """
    return tupl[1]

def moyennePonder(liste):
    """
    Input: list of tuples 
    Output: float
    La fonction prend en argument une liste de couple et retourne la moyenne des premières valeurs de chaque couple pondérées par les deuxièmes valeurs de chaque couple.
    """
    res=0
    diviseur=0
    for a,b in liste:
        res+=a*b
        diviseur+=b
    res/=diviseur
    
    return res

def sommeArrangee(liste):
    """
    Input: list of tuple
    Output: int
    La fonction prend en argument une liste de couple et retourne la somme des produits des deux éléments que comporte chaque couple.
    """
    res=0
    for a,b in liste:
        res+=a*b
    return res

##On s'occupe maintenant de la partie interface et traitement de l'image
    
#On commence par la fonction qui affiche la fenêtre Tkinter et propose d'ouvrir un fichier image
def opening():
    """
    Input: None
    Outut: None
    La fonction affiche une fenêtre Tkinter qui propose à l'utilisateur d'ouvrir une photo
    """
    global zoneImage, boutonOuverture, zoneParametre, threshold, flag, fenetre
    
    #On ouvre quand même une première fenêtre pour donner les instructions à l'opérateur
    window=Tk()
    instruction="Cher opérateur, commencez par ouvrir votre photo. \n\n Il n'y a ensuite qu'un seul paramère à ajuster, il s'agit de 'threshold'. Peu importe sa signification, il faut trouver une valeur telle que seuls les objets à compter apparaissent en blanc sur l'image.\n\n Il peut rester des petits points blancs qui ne correspondent à aucun objet SI ET SEULEMENT SI ces points sont de taille inférieure à environ 5 pixels.\n\n Une fois les réglages terminés, cliquez sur décollage pour voir vos résultats. Il faut attendre quelques secondes pour le voir s'afficher.\n\n Fermez cette fenêtre et le programme débutera."
    notaBene="\n\nNB: Sur la première ligne du tableau de résultats s'afficheront les tailles en pixels des taches blanches que vous voulez compter les plus présentes. \nSi parmis les trois valeurs, l'une vous semble anormalement basse, c'est que vous n'avez pas assez filtré la photo, il faut recommencer."
    instructions=LabelFrame(window,text="INSTRUCTIONS")
    instructions.pack()
    Label(instructions,text=instruction+notaBene).pack()
    window.mainloop()
    
    #On peut alors passer au reste
    flag=True
    
    fenetre=Tk()
    #Il faut une zone dans laquelle afficher l'image à traiter
    zoneImage= Label(fenetre)
    zoneImage.pack(fill='both',expand='yes')
    #Un bouton pour commander l'ouverture de l'image
    boutonOuverture= Button(zoneImage, text="Ouvrir photo", command=openPhoto)
    boutonOuverture.pack()
    #Une zone dans laquelle seront réalisés les ajustements des différents paramètres
    zoneParametre = LabelFrame(fenetre,text="AJUSTEMENT DU THRESHOLD")
    zoneParametre.pack(fill='both',expand='yes')
    
    #Le seul paramètre à ajuster est la constante dans la fonction cv2.adaptiveThreshold dont on se sert plus bas
    threshold=StringVar()
    threshold.set(-3)
    parametre=Spinbox(zoneParametre, textvariable=threshold, from_=-100, to=100)
    parametre.pack(padx=200)
    
    fenetre.mainloop()
    
def photoResize(image, screen_width, screen_height):
    """
    Input: image pillow, int, int
    Output: image pillow
    La fonction prend en argument une image telle que le module pillow les définit ainsi que la largeur de l'écran sur lequel in travaille et retourne l'image redimensionnée pour pouvoir être correctement affichée dans la fenêtre tkinter.
    """
    largeur=image.width
    hauteur=image.height   
    
    #Selon l'orientation de l'image, protrait ou paysage, il faut qu'elle puisse tenir dans notre fenêtre tkinter, en utilisant au maximum l'espace disponible.
    facteur=min((screen_height-150)/hauteur,(screen_width-300)/largeur)
    #On redimensionne alors l'image à l'aide d'une fonction prédéfinie.
    imageResized=image.resize((int(facteur*largeur),int(facteur*hauteur)))
    
    return imageResized

def openPhoto():
    """
    Input: None
    Output: None
    La fonction permet de demander à l'utilisateur d'afficher une image à retoucher et de l'afficher dans la fenetre Tkinter
    """
    global screen_width, screen_height, arrayImageOriginal, zoneImage
    
    #La ligne de code permet de demander à l'utilisateur d'aller chercher lui-même la photo à traiter avec l'explorateur windows
    filepath = fd.askopenfilename(initialdir = cheminPhotos,title = "Selectionner photo",filetypes = (("jpeg files","*.jpg"),("all files","*.*")))
    #Pour les redimensionnement futurs, il faut qu'on ait accès aux dimensions du moniteur sur lequel tourne le programme
    screen_width=GetSystemMetrics(0)
    screen_height=GetSystemMetrics(1)
    
    #On ouvre l'image originale en niveaux de gris
    originalImage=Image.open(filepath).convert('L')
    #On convertit en array numpy échantillonné sur 8 bits et on applique le flou gaussien une bonne fois pour toutes
    arrayImageOriginal=np.array(mh.gaussian_filter(np.array(originalImage),3),dtype=np.uint8)
    #On redimensionne puis on convertit en un format exploitable par tkinter
    resizedImage=photoResize(originalImage,screen_width, screen_height)
    tkinterImage=ImageTk.PhotoImage(resizedImage)
    
    #On peut alors détruire le bouton qui a servi à l'ouverture du fichier image
    boutonOuverture.destroy()
    
    zoneImage.configure(image=tkinterImage)
    zoneImage.image=tkinterImage
    
    #On ajoute le nouveau bouton qui permettra de lancer les calculs sur l'image traitée
    boutonDecollage=Button(zoneParametre,text="Décollage !", command=stop)
    boutonDecollage.pack(padx=200)
    
    #Il faut ensuite lancer l'actualisation
    actualise()

def stop():
    """
    Input: None
    Outut: None
    La fonction met flag à False et indique qu'il faut cesser l'actualisation de l'affichage
    """
    global flag
    flag=False
    
def actualise():
    """
    Input: None
    Output: None
    On définit la fonction qui permet d'actualiser 'affichage de l'image à mesure qu'on modifie la valeur du seuil.
    """
    global arrayImageOriginal, threshold, screen_width, flag, fenetre, screen_width, arrayImage
    
    #On commence par récupérer la valeur d'intérêt
    thresh=int(threshold.get())
    #On modifie l'image
    arrayImage=cv2.adaptiveThreshold(src=arrayImageOriginal, maxValue=255, adaptiveMethod=cv2.ADAPTIVE_THRESH_MEAN_C, thresholdType=cv2.THRESH_BINARY, blockSize=7, C=thresh)
    
    #On la convertit à nouveau
    resizedImage=photoResize(PIL.Image.fromarray(arrayImage),screen_width, screen_height)
    tkinterImage=ImageTk.PhotoImage(resizedImage)
    
    #On affiche l'image        
    zoneImage.configure(image=tkinterImage)
    zoneImage.image=tkinterImage
    
    #On fait les appels aux bonnes fonctions en fonction de la valeur de flag (soit on continue d'actualiser, soit on passe au calcul)
    if flag:
        fenetre.after(100, actualise)
    else:
        fenetre.after(100,processing)
    

def processing():
    """
    Input: None
    Output: None
    Etant donnée une valeur pour le threshold, on a une image modifiée en conséquence et prête pour les traitemtents ultérieurs. On affiche les résultats dans une nouvelle fenêtre
    """
    
    global arrayImage,fenetre
    
    #une fois que le traitement de l'image est fini, on peut détruire la fenêtre
    fenetre.destroy()
    
    #on créé une nouvelle fenêtre pour indiquer à l'utilisateur que son image est en cours de traitement
    #On détermine les tailles de toutes les composantes connexes blanches de l'image traitée
    listeTailles=connected_components_sizes(arrayImage)
    #On compte le nombre de composantes connexes de chaque taille présente dans l'image
    compte = [(k,listeTailles.count(k)) for k in set(listeTailles)]
    
    #On trie en fonction de la valeur du deuxième argument du tuple, dans l'ordre décroissant
    compte.sort(key=takeSecond,reverse=True)
    
    #On détermine successivement: la surface moyenne d'une larve, la surface totale des composantes connexes blanches et la deuxième divisée par la première
    prevalent=compte[:3]
    surfaceMoyenne=round(moyennePonder(prevalent),2)
    resultat = items(arrayImage, surfaceMoyenne)
    
    #On créé la fenêtre qui ajoute les résultats
    root=Tk()
    case1=Label(root, text="Tailles de composantes prééminentes").grid(row=0,column=0)
    prevalent=[str(x[0]) for x in prevalent]
    case2=Label(root,text="/".join(prevalent)).grid(row=0,column=1)
    case3=Label(root, text="Surface moyenne").grid(row=1,column=0)
    case4=Label(root, text=str(surfaceMoyenne)).grid(row=1,column=1)
    case5=Label(root, text="Nombre d'objets").grid(row=2,column=0)
    case6=Label(root,text=resultat).grid(row=2,column=1)
    root.mainloop()

  
cheminPhotos = "" # RENSEIGNER ICI LE CHEMIN DU DOSSIER CONTENANT LES PHOTOS A TRAITER
opening()


