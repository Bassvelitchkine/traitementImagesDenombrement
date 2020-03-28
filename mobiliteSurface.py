#Attention, l'ordre dans lequel on importe les modules et fonctions a une importance !
from tkinter import *
from tkinter import filedialog as fd
import PIL
from PIL import Image, ImageTk
import numpy as np
import cv2
import scipy.ndimage.filters as filters
import scipy.ndimage as ndimage
import matplotlib.pyplot as plt
from win32api import GetSystemMetrics
import mahotas as mh

#On commence par récupérer la taille de l'écran sur lequel on travaille car l'affichage des photos en dépend (il faudra que chaque photo prenne à peu près un quart de la surface de l'écran)
global screen_width,screen_height
screen_width=GetSystemMetrics(0)
screen_height=GetSystemMetrics(1)


cheminPhotos = "" # ENTREZ ICI LE CHEMIN MENANT AU DOSSIER CONTENANT LES PHOTOS

def photoResize(image):
    """
    Input: image pillow
    Output: image pillow
    La fonction prend en argument une image telle que le module pillow les définit ainsi que la largeur de l'écran sur lequel in travaille et retourne l'image redimensionnée pour pouvoir être correctement affichée dans la fenêtre tkinter.
    """
    global screen_width,screen_height
    largeur=image.width
    hauteur=image.height   
    #Selon l'orientation de l'image, protrait ou paysage, il faut qu'elle puisse tenir dans notre fenêtre tkinter, en utilisant au maximum l'espace disponible.
    facteur=min((screen_height//2-100)/hauteur,(screen_width//2-50)/largeur)
    #On redimensionne alors l'image à l'aide d'une fonction prédéfinie.    
    imageResized=image.resize((int(facteur*largeur),int(facteur*hauteur)))
    
    return imageResized

#On créer également la variable qui contient les instructions de départ pour l'utilisateur.
global instructions
instructions="Cher opérateur, servez-vous des boutons ci-dessous pour ouvrir D'ABORD la première photo à traiter, PUIS la deuxième.\n Dès lors, vous pourrez commencer à ajuster les différents paramètres.\n\n Voici, en bref, ce que font les différents paramètres qui s'affichent :\n\n-Threshold permet de faire disparaitre le bruit de votre image. Lorsque vous lancez le traitement, il ne faut absolument AUCUN bruit sur l'image. Le seul blanc ou gris autorisé doit provenir des objets à dénombrer.\n-Kernel et sigma vous permettront en gros de flouter l'image, les objets à dénombrer apparaitront comme des taches un peu plus lisses.\n-erosion vous permettra d'éroder l'image, c'est-à-dire de légèrement amincir les objets à dénombrer. De cette manière, deux de vos objets se touchaient, ne formant qu'une seule tache, vous pourrez les séparer. \nATTENTION à ne pas faire disparaitre certaines des taches blanches.\n-Radius définit la taille de la zone dans laquelle chercher des maximas. S'il est trop grand, vous aurez moins de croix rouges que d'objets à compter, s'il est trop petit, vous aurez plusieurs croix par objet. \nLe but étant, in fine, d'avoir autant de croix que d'objets à compter, de la manière la plus fidèle possible.\n\n A vous de jouer !"

#On créé une fonction qui deviendra une commande pour la fenêtre Tkinter pour demander à l'utilisateur d'ouvrir la première photo
def open_photo1():
    """
    Input: None
    Output: None
    La fonction fonctionne avec des variables globales. Elle demande à l'utilisateur d'aller ouvrir les photos en question puis stocke la photo en niveau de gris dans une variable globale, celle de la photo 1.
    """
    #Avec Tkinter, nous sommes forcés de définir des variables globales et des fonctions qui agissent sur les variables globales plutôt que des fonctions avec entrées et sorties
    global photo1, p1_depart, p1, fenetre,l1,l2,bouton1,param1,param11,param12,param13,param14,param15,case1, threshold1,kernel_size1,sigma1,erosion_size1,filtering_radius1, croix1, canvas1
    
    #La ligne qui suit permet de demander à l'utilisateur d'ouvrir un fichier jpg    
    filepath = fd.askopenfilename(initialdir = cheminPhotos ,title = "Select file",filetypes = (("jpeg files","*.jpg"),("all files","*.*")))
    #On ouvre l'image en niveaux de gris, en effet, nous avons des images qui sont en noir et blanc, inutile de conserver le RGB qui est plus lourd en mémoire
    p1=Image.open(filepath).convert('L') 
    
    #On transforme l'image de départ en array numpy pour les traitement futurs, p1_depart est une variable globale qui ne sera jamais modifiée contrairement à p1. En effet, tous les filtres doivent être appliqués sur l'image de départ avec sa taille originale et non sur les résultats des itérations qui précèdent. Exemple : si on applique un seuil un peu trop fort à une photo qu'on stocke le résultat et qu'on veut rectifier le tir sur le résultat en rabaissant le seuil, c'est impossible.
    p1_depart=np.array(mh.gaussian_filter(np.asarray(p1),3),dtype=np.uint8)

    photo1=photoResize(p1)
    
    #Les photos exploitables par Tkinter ne sont pas les mêmes que celles qui sont retournées par pillow
    photo1Tk=ImageTk.PhotoImage(photo1)
    
    #Un fois que la première image a été appelée, on peut détruire les instructions ainsi que le bouton qui permettait d'ouvrir la première photo
    l1.destroy()
    bouton1.destroy()
    
    #On positionne la photo sur l'écran tkinter
    canvas1 = Label(l2, width=int(photo1.width)+30, height=int(photo1.height)+10,image=photo1Tk)
    canvas1.pack(side=LEFT)

    #Paramètres de la photo1 : on créé toutes les fenêtres qui contiennent les scrolls qui permettront d'ajuster les paramètres de la photo 1. Les "fenêtres" sont des LabelFrames
    param1=LabelFrame(l2,text='PARAMETRES')
    param1.pack(fill='both',expand='yes',side=RIGHT)
    #On les ajoute un à un
    param11=LabelFrame(param1, text="Threshold")
    
    param11.pack(fill='both',expand='yes',side=LEFT)
    
#    On ajoute les curseurs à l'intérieur des LabelFrame() qu'on vient de créer, on ajoute des boutons de valeurs incrémenter
    threshold1 = StringVar()
    threshold1.set(-3)
    scale11 = Spinbox(param11, textvariable=threshold1, from_=-100, to=100)
    scale11.pack()

    
def open_photo2():
    """
    Input: None
    Output: None
    La fonction fonctionne avec des variables globales. Elle demande à l'utilisateur d'aller ouvrir les photos en question puis stocke la photo en niveau de gris dans une variable globale, celle de la photo 2.
    """
    #Avec Tkinter, nous sommes forcés de définir des variables globales et des fonctions qui agissent sur les variables globales plutôt que des fonctions avec entrées et sorties
    global bouton,photo2, p2, p2_depart, continuer,fenetre,l1,l3,bouton2,param2,param21,param22,param23,param24,param25,case2, threshold2, kernel_size2, sigma2, erosion_size2, filtering_radius2, croix2, canvas2
    
    #La ligne qui suit permet de demander à l'utilisateur d'ouvrir un fichier jpg    
    filepath = fd.askopenfilename(initialdir = cheminPhotos,title = "Select file",filetypes = (("jpeg files","*.jpg"),("all files","*.*")))
    #On ouvre l'image en niveaux de gris, en effet, nous avons des images qui sont en noir et blanc, inutile de conserver le RGB qui est plus lourd en mémoire
    p2=Image.open(filepath).convert('L') 
    
    #On transforme l'image de départ en array numpy pour les traitement futurs, p1_depart est une variable globale qui ne sera jamais modifiée contrairement à p1. En effet, tous les filtres doivent être appliqués sur l'image de départ avec sa taille originale et non sur les résultats des itérations qui précèdent. Exemple : si on applique un seuil un peu trop fort à une photo qu'on stocke le résultat et qu'on veut rectifier le tir sur le résultat en rabaissant le seuil, c'est impossible.
    p2_depart=np.array(mh.gaussian_filter(np.asarray(p2),3),dtype=np.uint8)
    
    #On redimensionne l'image avant d'en faire qqch d'exploitable par Tkinter, comme nous l'avons dit, un quart de l'écran par image à peu près
    photo2=photoResize(p2)    

    #Les photos exploitables par Tkinter ne sont pas les mêmes que celles qui sont retournées par pillow
    photo2Tk=ImageTk.PhotoImage(photo2)
    
    #Un fois que la première image a été appelée, on peut détruire les instructions ainsi que le bouton qui permettait d'ouvrir la deuxième photo
    l1.destroy() 
    bouton2.destroy()
    
    #On positionne la photo sur l'écran tkinter
    canvas2 = Label(l3, width=int(photo2.width)+30, height=int(photo2.height)+10,image=photo2Tk)
    canvas2.pack(side=LEFT)

    #Paramètres de la photo 2 : on créé toutes les fenêtres qui contiennent les scrolls qui permettront d'ajuster les paramètres de la photo 21. Les "fenêtres" sont des LabelFrames
    param2=LabelFrame(l3,text='PARAMETRES')
    param2.pack(fill='both',expand='yes',side=RIGHT)
    
    #On ajoute tous les paramètres un à un
    param21=LabelFrame(param2, text="Threshold")

    param21.pack(fill='both',expand='yes',side=LEFT)
    
    #    On ajoute les curseurs à l'intérieur des LabelFrame() qu'on vient de créer, on ajoute des boutons de valeurs incrémenter
    threshold2 = StringVar()
    threshold2.set(-3)
    scale21 = Spinbox(param21, textvariable=threshold2, from_=-100, to=100)
    scale21.pack()
    
    #Il faut un tout dernier bouton qui permettra ensuite de lancer les calculs
    bouton = Button(fenetre, text="Décollage", command=decollage)
    bouton.pack(side=BOTTOM)
    
    #Une fois que l'utilisateur a chargé la deuxième photo, et seulement après cela, on peut lancer l'ajustement des paramètres et actualiser l'affichage au fur et à mesure des modifications avec la fonction actualiser qui s'appelle elle-même
    fenetre.after(500,actualiser)

#Il faut la fonction qui permet d'appliquer le traitement de nos images à un array numpy
def photo_processing(image_entree,numero_photo):
    """
    Input: array,int
    Output: array
    La fonction prend en argument le tableau en niveaux de gris à traiter ainsi que le numéro de la photo qui correspond. Elle retourne le tableau numpy de l'image après son traitement.
    """
    global liste_centres_1,liste_centres_2,thresh1, kernel1, sig1, erosion1, radius1, X1,thresh2, kernel2, sig2, erosion2, radius2, X2
    
    #On traite séparément les photos 1 et 2 car elles ont des paramètres de traitement différents
    if numero_photo==1:
                
        #Il faut aussi appliquer un seuil pour éliminer tout le bruit. En effet, les petits points blancs qui constituent le bruit pourraient être comptés comme les objets que nous tentons de dénombrer
        #Il ne faut pas appliquer le flou gaussien à chaque fois, ça consomme du temps de calcul, une seule fois au début suffit
        image= cv2.adaptiveThreshold(src=image_entree, maxValue=255, adaptiveMethod=cv2.ADAPTIVE_THRESH_MEAN_C, thresholdType=cv2.THRESH_BINARY, blockSize=7, C=thresh1)
                
    #Si la photo à traiter est la photo 2 
    elif numero_photo==2:                
        #Il faut aussi appliquer un seuil pour éliminer tout le bruit. En effet, les petits points blancs qui constituent le bruit pourraient être comptés comme les objets que nous tentons de dénombrer
        image= cv2.adaptiveThreshold(src=image_entree, maxValue=255, adaptiveMethod=cv2.ADAPTIVE_THRESH_MEAN_C, thresholdType=cv2.THRESH_BINARY, blockSize=7, C=thresh2)
        
    return image

#Juste en dessous se trouve la fonction qui ùet la variable flag à True pour indiquer qu'on arrête l'actualisation de la fenêtre Tkinter et qu'on passe au calcul des résultats
def decollage():
    """
    Input: None
    Output: None
    La fonction change la valeur de la variable globale flag pour la passer de False à True
    """
    global flag
    flag=True
    
#Il faut une fonction qui actualise régulièrement la photo en fonction des valeurs données par l'opérateur, on en a parlé plus tôt.
def actualiser():
    """
    Input: None
    Output: None
    La fonction permet d'actualiser les images avec les paramètres entrés par l'utilisateur
    """
    global p1_couleur, p2_couleur, p2_depart,fenetre,canvas1,canvas2, p1,p2,photo1,photo2,threshold1,kernel_size1,sigma1,erosion_size1,filtering_radius1, croix1, threshold2,kernel_size2,sigma2,erosion_size2,filtering_radius2, croix2,thresh1,thresh2,kernel1,kernel2,sig1,sig2,erosion1,erosion2,radius1,radius2,X1,X2
    
    #On commence par récupérer toutes les valeurs entrées par l'utilisateur (qui sont toutes entre 0 et 100, on le rappelle, par définition des objets Tkinter)
    thresh1=int(threshold1.get())
    thresh2=int(threshold2.get())

    p1=photo_processing(p1_depart,1)
    photo1=PIL.Image.fromarray(p1) #On fait la distinction p1 et P1_couleur car les tableaux n'ont pas les mêmes dimensions dans ce cas (on rajoute une dimension pour le RGB)
    
    p2=photo_processing(p2_depart,2)
    photo2=PIL.Image.fromarray(p2)
    
    
    #On a fait toutes les opérations sur les photos originales pour ne pas perdre d'information mais il faut ensuite les réadapter à la taille de notre fenêtre Tkinter   
    photo1=photoResize(photo1)
    photo2=photoResize(photo2)
    
    #On les retransforme dans un état que tkinter puisse interpréter
    photo1=ImageTk.PhotoImage(photo1)
    photo2=ImageTk.PhotoImage(photo2)
    
    #On actualise les widgets qui contiennent les photos modifiées
    canvas1.configure(image=photo1)
    canvas1.image=photo1
    canvas2.configure(image=photo2)
    canvas2.image=photo2
    
    #Ensuite, soit l'utilisateur veut lancer le calcul, soit il veut continuer d'ajuster les paramètres
    #flag est le paramètre en question qui vaut False si on continue  ajuster, True si on lance les calculs
    
    if not flag:
        fenetre.after(100,actualiser)
    else:
        resultats()
    
#Il faut d'abord une fonction qui ouvre la fenêtre de départ, affiche les instructions et demande à l'utilisateurs de charger les deux images à traiter
def starting_window():
    """
    Input: None
    Output: 
    La fonction affiche la fenêtre Tkinter de départ qui demande à l'utilisateur d'ouvrir les deux photos qu'il veut traiter ainsi que les instructions qu'il doit suivre.
    """
    global flag,photo1,photo2,l1,l2,l3,fenetre,bouton1,bouton2,canvas1,canvas2,thresh1,thresh2,kernel1,kernel2,sig1,sig2,erosion1,erosion2,radius1,radius2
    
    #On initialise toutes la variable flag à False car on débute par de multiples actualisations avant de passer aux calculs
    flag=False
    
    fenetre=Tk() 
    
    #On créé trois LabelFrames pour les instructions, la photo1 et la photo2
    l1 = LabelFrame(fenetre, text='INSTRUCTIONS')
    l1.pack(fill="both", expand="yes")     
    Label(l1, text=instructions).pack()
    
    l2 = LabelFrame(fenetre, text="PREMIERE PHOTO")
    l2.pack(fill="both", expand="yes")     
    bouton1=Button(l2, text="Ouvrir Photo", command=open_photo1)
    bouton1.pack()
    
    l3 = LabelFrame(fenetre, text="DEUXIEME PHOTO")
    l3.pack(fill="both", expand="yes")     
    bouton2=Button(l3, text="Ouvrir Photo", command=open_photo2)
    bouton2.pack()
            
    fenetre.mainloop()
    
def takeSecond(item):
    return item[1]

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
    
#On réécrit la fonction qui permet de trouver les composantes connexes pour qu'elle puisse traiter trois images en même temps et diminuer le temps de calcul
def connected_components_sizes(image1, image2):
    """
    Input: numpy array, numpy array
    Output: [list of ints, list of ints, list of int, 2D numpy array of float]
    La fonction prend en agument deux images sous forme de tabeaux numpy. Elle calcule terme à terme la valeur absolue de la différence entre les deux images. Elle retourne les listes des tailles en pixels des composantes connexes des graphes des trois images ainsi que la troisième image. Les images sont supposées être en noir et blanc et on ne considère que les composantes connexes sont blanches.
    """
    image3 = np.zeros(image1.shape)
    res1,res2,res3=[],[],[]
    dicoSommets1,dicoSommets2,dicoSommets3={},{},{}
    listeSommets1,listeSommets2,listeSommets3=[],[],[]
    
    for i in range(image1.shape[0]):
        for j in range(image1.shape[1]):
            #On considère d'abord la première image
            if image1[i,j]==255: #On ne veut visiter que les sommets blancs
                dicoSommets1[(i,j)]=None
                listeSommets1.append((i,j))
            else:
                dicoSommets1[(i,j)]=1
            #Puis la deuxième
            if image2[i,j]==255: #On ne veut visiter que les sommets blancs
                dicoSommets2[(i,j)]=None
                listeSommets2.append((i,j))
            else:
                dicoSommets2[(i,j)]=1
            #Puis la troisième
            if image1[i,j]!=image2[i,j]:
                image3[i,j]=255
                dicoSommets3[(i,j)]=None
                listeSommets3.append((i,j))
            else:
                dicoSommets3[(i,j)]=1                
            
    for sommet in listeSommets1:
        if dicoSommets1[sommet]==None:
            res1.append(bfs(dicoSommets1,image1,sommet))
    for sommet in listeSommets2:
        if dicoSommets2[sommet]==None:
            res2.append(bfs(dicoSommets2,image2,sommet))
    for sommet in listeSommets3:
        if dicoSommets3[sommet]==None:
            res3.append(bfs(dicoSommets3,image3,sommet))
            
    return [res1,res2,res3,image3]

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

#On veut une fonction qui à la liste des tailles en pixels des composantes connexes associe le nombre total des composantes connexes sur l'image
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

def moyennePonder(liste):
    """
    """
    res=0
    diviseur=0
    for a,b in liste:
        res+=a*b
        diviseur+=b
    return (res/diviseur)
    
def sommeArrangee(liste):
    """
    """
    res=0
    for a,b in liste:
        res+=a*b
    return res

def sommeDeuxiemeVal(liste):
    """
    """
    res=0
    for a,b in liste:
        res+=b
    return res
    
    
#Une fois que les valeurs des 12 paramètres ont été réglées on dispose également de la liste des positions des centres des maximas, et c'est tout ce dont nous avons besoin pour afficher nos résultats 
def resultats():
    """
    Input: None
    Output: None
    La fonction détruit la fenetre précédente pour en créer une nouvelle qui affichera les résultats des calculs.
    """
    global fenetre, p1_depart, p2_depart, p1,p2
    
    #Si on arrive sur le calcul des résultats c'est que nous en avons fini avec la première fenêtre dans laquelle il n'y a pas de place pour afficher les résultats, donc on la détruit
    fenetre.destroy()
    fenetre=Tk()
       
    #Ci-dessous les calculs avec la deuxième fonction de calcul des composantes connexes
    [liste1,liste2,liste3,derniereImage] = connected_components_sizes(p1,p2)
    
    liste12=[(k,liste1.count(k)) for k in set(liste1)]  
    liste12.sort(key=takeSecond,reverse=True)
    taille1=moyennePonder(liste12[:3])
    
    liste22=[(k,liste2.count(k)) for k in set(liste2)]  
    liste22.sort(key=takeSecond,reverse=True)
    taille2=moyennePonder(liste22[:3])
    
    tailleMoyenne = (taille1 + taille2)/2
    liste3=[(k,liste3.count(k)) for k in set(liste3)] # if k>0.3*tailleMoyenne] #On se laisse une petite marge d'erreur

    nombreObjets1=number_items(liste1,taille1)
    nombreObjets2=number_items(liste2,taille2)
    nombreObjetsMoyen=(nombreObjets1+nombreObjets2)//2
        
    nombreMobiles=sommeDeuxiemeVal(liste3)//2 #Il faut diviser par deux car un objet mobile fera apparaitre deux taches de 1, ou alors un grosse tache si les deux taches ne sont pas distinctes
    tauxMortalite=1-(nombreMobiles/nombreObjetsMoyen)
        
#    Et pour finir, on range tout cela dans notre nouvelle fenêtre, on veut former un tableaud de 6 lignes et 2 colonnes
    la1=Label(fenetre,text='Nombre objets photo 1',borderwidth=1).grid(row=0,column=0)
    la2=Label(fenetre,text=str(nombreObjets1),borderwidth=1).grid(row=0,column=1)
    la3=Label(fenetre,text='Nombre objets photo 2',borderwidth=1).grid(row=1,column=0)
    la4=Label(fenetre,text=str(nombreObjets2),borderwidth=1).grid(row=1,column=1)
    la5=Label(fenetre,text="Nombre moyen d'objets",borderwidth=1).grid(row=2,column=0)
    la6=Label(fenetre,text=str(nombreObjetsMoyen),borderwidth=1).grid(row=2,column=1)
    la9=Label(fenetre,text="Ratio moyen d'immobiles",borderwidth=1).grid(row=4,column=0)
    la10=Label(fenetre,text=str(tauxMortalite),borderwidth=1).grid(row=4,column=1)

    
    fenetre.mainloop()
    
    
starting_window()