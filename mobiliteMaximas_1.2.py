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

#On commence par récupérer la taille de l'écran sur lequel on travaille car l'affichage des photos en dépend (il faudra que chaque photo prenne à peu près un quart de la surface de l'écran)
global screen_width
screen_width=GetSystemMetrics(0)

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
    filepath = fd.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("jpeg files","*.jpg"),("all files","*.*")))
    #On ouvre l'image en niveaux de gris, en effet, nous avons des images qui sont en noir et blanc, inutile de conserver le RGB qui est plus lourd en mémoire
    p1=Image.open(filepath).convert('L') 
    
    #On redimensionne l'image avant d'en faire qqch d'exploitable par Tkinter, comme nous l'avons dit, un quart de l'écran par image à peu près
    hauteur=p1.height
    largeur=p1.width
    longueur=max(hauteur,largeur)
    facteur=(screen_width//2-120)/longueur
    photo1=p1.resize((int(facteur*largeur),int(facteur*hauteur)))
    
    #On transforme l'image de départ en array numpy pour les traitement futurs, p1_depart est une variable globale qui ne sera jamais modifiée contrairement à p1. En effet, tous les filtres doivent être appliqués sur l'image de départ avec sa taille originale et non sur les résultats des itérations qui précèdent. Exemple : si on applique un seuil un peu trop fort à une photo qu'on stocke le résultat et qu'on veut rectifier le tir sur le résultat en rabaissant le seuil, c'est impossible.
    p1_depart=np.asarray(p1)
    
    #Les photos exploitables par Tkinter ne sont pas les mêmes que celles qui sont retournées par pillow
    photo1=ImageTk.PhotoImage(photo1)
    
    #Un fois que la première image a été appelée, on peut détruire les instructions ainsi que le bouton qui permettait d'ouvrir la première photo
    l1.destroy()
    bouton1.destroy()
    
    #On positionne la photo sur l'écran tkinter
    canvas1 = Label(l2, width=(screen_width//2-120), height=int(facteur*hauteur),image=photo1)
    canvas1.pack(side=LEFT)

    #Paramètres de la photo1 : on créé toutes les fenêtres qui contiennent les scrolls qui permettront d'ajuster les paramètres de la photo 1. Les "fenêtres" sont des LabelFrames
    param1=LabelFrame(l2,text='PARAMETRES')
    param1.pack(fill='both',expand='yes',side=RIGHT)
    #On les ajoute un à un
    param11=LabelFrame(param1, text="Threshold")
    param12=LabelFrame(param1, text="Kernel Size")
    param13=LabelFrame(param1, text="Sigma")
    param14=LabelFrame(param1, text="Erosion")
    param15=LabelFrame(param1, text="Rayon maximas")
    case1=LabelFrame(param1, text="  ")    
    
    param11.pack(fill='both',expand='yes',side=LEFT)
    param12.pack(fill='both',expand='yes',side=LEFT)
    param13.pack(fill='both',expand='yes',side=LEFT)
    param14.pack(fill='both',expand='yes',side=LEFT)
    param15.pack(fill='both',expand='yes',side=LEFT)
    case1.pack(fill='both',expand='yes',side=LEFT)
    
#    On ajoute les curseurs à l'intérieur des LabelFrame() qu'on vient de créer, on ajoute des boutons de valeurs incrémenter
    threshold1 = StringVar()
    scale11 = Spinbox(param11, textvariable=threshold1, from_=0, to=255)
    scale11.pack()
    
    kernel_size1 = StringVar()
    scale12 = Spinbox(param12, textvariable=kernel_size1, values=(1,3,5,7,9,11,13,15,17,19,21,23,25,27,29,31))
    scale12.pack()
    
    sigma1 = StringVar()
    scale13 = Spinbox(param13, textvariable=sigma1, from_=0, to=100)
    scale13.pack()
    
    erosion_size1 = StringVar()
    scale14 = Spinbox(param14, textvariable=erosion_size1, values=(1,3,5,7,9,11,13,15,17,19,21,23,25,27,29,31))
    scale14.pack()
    
    filtering_radius1 = StringVar()
    scale15 = Spinbox(param15, textvariable=filtering_radius1,from_=1, to=30)
    scale15.pack()
    
    #On créé également un bouton qui permettra de demander à l'utilisateur s'il souhaite qu'on affiche les croix rouges ou non
    croix1=IntVar()
    bouton1 = Checkbutton(case1, text="Croix", variable=croix1, onvalue=1, offvalue=0)
    bouton1.pack()
    
def open_photo2():
    """
    Input: None
    Output: None
    La fonction fonctionne avec des variables globales. Elle demande à l'utilisateur d'aller ouvrir les photos en question puis stocke la photo en niveau de gris dans une variable globale, celle de la photo 2.
    """
    #Avec Tkinter, nous sommes forcés de définir des variables globales et des fonctions qui agissent sur les variables globales plutôt que des fonctions avec entrées et sorties
    global bouton,photo2, p2, p2_depart, continuer,fenetre,l1,l3,bouton2,param2,param21,param22,param23,param24,param25,case2, threshold2, kernel_size2, sigma2, erosion_size2, filtering_radius2, croix2, canvas2
    
    #La ligne qui suit permet de demander à l'utilisateur d'ouvrir un fichier jpg
    filepath = fd.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("jpeg files","*.jpg"),("all files","*.*")))
    #On ouvre l'image en niveaux de gris, en effet, nous avons des images qui sont en noir et blanc, inutile de conserver le RGB qui est plus lourd en mémoire
    p2=Image.open(filepath).convert('L') 
    
    #On redimensionne l'image avant d'en faire qqch d'exploitable par Tkinter, comme nous l'avons dit, un quart de l'écran par image à peu près
    hauteur=p2.height
    largeur=p2.width
    facteur=(screen_width//2-120)/largeur
    photo2=p2.resize((int(facteur*largeur),int(facteur*hauteur)))
    
    #On transforme l'image de départ en array numpy pour les traitement futurs, p1_depart est une variable globale qui ne sera jamais modifiée contrairement à p1. En effet, tous les filtres doivent être appliqués sur l'image de départ avec sa taille originale et non sur les résultats des itérations qui précèdent. Exemple : si on applique un seuil un peu trop fort à une photo qu'on stocke le résultat et qu'on veut rectifier le tir sur le résultat en rabaissant le seuil, c'est impossible.
    p2_depart=np.asarray(p2)
    #Les photos exploitables par Tkinter ne sont pas les mêmes que celles qui sont retournées par pillow
    photo2=ImageTk.PhotoImage(photo2)
    
    #Un fois que la première image a été appelée, on peut détruire les instructions ainsi que le bouton qui permettait d'ouvrir la deuxième photo
    l1.destroy() 
    bouton2.destroy()
    
    #On positionne la photo sur l'écran tkinter
    canvas2 = Label(l3, width=(screen_width//2-120), height=int(facteur*hauteur),image=photo2)
    canvas2.pack(side=LEFT)

    #Paramètres de la photo 2 : on créé toutes les fenêtres qui contiennent les scrolls qui permettront d'ajuster les paramètres de la photo 21. Les "fenêtres" sont des LabelFrames
    param2=LabelFrame(l3,text='PARAMETRES')
    param2.pack(fill='both',expand='yes',side=RIGHT)
    
    #On ajoute tous les paramètres un à un
    param21=LabelFrame(param2, text="Threshold")
    param22=LabelFrame(param2, text="Kernel Size")
    param23=LabelFrame(param2, text="Sigma")
    param24=LabelFrame(param2, text="Erosion")
    param25=LabelFrame(param2, text="Rayon maximas")
    case2=LabelFrame(param2, text="  ")    
    
    param21.pack(fill='both',expand='yes',side=LEFT)
    param22.pack(fill='both',expand='yes',side=LEFT)
    param23.pack(fill='both',expand='yes',side=LEFT)
    param24.pack(fill='both',expand='yes',side=LEFT)
    param25.pack(fill='both',expand='yes',side=LEFT)
    case2.pack(fill='both',expand='yes',side=LEFT)
    
    #    On ajoute les curseurs à l'intérieur des LabelFrame() qu'on vient de créer, on ajoute des boutons de valeurs incrémenter
    threshold2 = StringVar()
    scale21 = Spinbox(param21, textvariable=threshold2, from_=0, to=255)
    scale21.pack()
    
    kernel_size2 = StringVar()
    scale22 = Spinbox(param22, textvariable=kernel_size2, values=(1,3,5,7,9,11,13,15,17,19,21,23,25,27,29,31))
    scale22.pack()
    
    sigma2 = StringVar()
    scale23 = Spinbox(param23, textvariable=sigma2, from_=0, to=100)
    scale23.pack()
    
    erosion_size2 = StringVar()
    scale24 = Spinbox(param24, textvariable=erosion_size2, values=(1,3,5,7,9,11,13,15,17,19,21,23,25,27,29,31))
    scale24.pack()
    
    filtering_radius2 = StringVar()
    scale25 = Spinbox(param25, textvariable=filtering_radius2,from_=1, to=30)
    scale25.pack()    
    
    #On créé également un bouton qui permettra de demander à l'utilisateur s'il souhaite qu'on affiche les croix rouges ou non
    croix2=IntVar()
    croix2.set(0)
    bouton2 = Checkbutton(case2, text="Croix",variable=croix2, onvalue=1, offvalue=0)
    bouton2.pack()
    
    #Il faut un tout dernier bouton qui permettra ensuite de lancer les calculs
    bouton = Button(fenetre, text="Décollage", command=decollage)
    bouton.pack(side=BOTTOM)
    
    #Une fois que l'utilisateur a chargé la deuxième photo, et seulement après cela, on peut lancer l'ajustement des paramètres et actualiser l'affichage au fur et à mesure des modifications avec la fonction actualiser qui s'appelle elle-même
    fenetre.after(500,actualiser)
  
#Il faut la fonction qui à une image traitée sous forme d'array retourne la liste des coordonnées des maximas de luminosité
def positions(image,numero_photo):
    """
    Input: array, int
    Output: list of tuples
    La fonction prend en argument l'image en niveaux de gris sous forme de tableau ainsi que l'entier qui représente le numéro de la photo qu'on traite (1 ou 2). Elle retourne la liste des absisses ainsi que la liste des ordonnées des centres de ces maximas. 
    """
    global radius1,radius2
    
    if numero_photo==1:    
        #Le filtre qu'on applique permet de trouver les maximas REGIONNAUX d'une photo
        maximas = filters.maximum_filter(image, radius1)
    elif numero_photo==2:
        #Le filtre qu'on applique permet de trouver les maximas REGIONNAUX d'une photo
        maximas = filters.maximum_filter(image, radius2)
    
    #On considère alors l'image qui n'est constituée que des maximas qui ont été trouvés
    res= (image==maximas)    
    labeled, num_objects = ndimage.label(res)   
     
    #On détermine les positions des maximas. fond_objects retourne en fait des objets slices qui détermine de manière unique le petit rectangle dans lequel se trouve le maxima en question. A partir de ces informations, on peut trouver le centre du rectangle et donc le centre des objets qu'on dénombre
    slices = ndimage.find_objects(labeled)
    
    #On créé alors une liste qui contient les coordonnées de tous les centres sous forme de tuples
    res=[]
    for dx,dy in slices:
        x_center = int((dx.start + dx.stop - 1)/2)
        y_center = int((dy.start + dy.stop - 1)/2)
        res.append((x_center,y_center))
    
    return res
    
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
        T,image= cv2.threshold(image_entree, thresh1, 0, type=cv2.THRESH_TOZERO)
        
        #On applique un filtre gaussien à l'image, on trouve facilement sur internet ce qu'est un filtre gaussien
        image=cv2.GaussianBlur(image,(kernel1,kernel1),sig1)
        
        #On érode les différents objets, c'est-à-dire qu'on les amincit. De cette façon, les objets qui ne font que se toucher, pourront peut-être se séparer, selon les situations.
        kernel = np.ones((erosion1,erosion1),np.uint8)
        image = cv2.erode(image,kernel,iterations = 1)
        
        #Maintenant, en fonction de la valeur de X1 on superpose des taches rouges sur notre image de départ. X1 est la variable qui enregistre le choix de l'utilisateur pour oui ou non afficher les croix rouges
        #Si on veut afficher les croix sur la première photo
        if X1==1:
            #On récupère la liste des points rouges à placer
            liste_centres_1=positions(image,1)
            
            #Il faut convertir l'image en RGB (elle était en niveau de gris) car nous aurons des croix rouges dessus. On utilise les fonctions toutes faites des modules qui sont beaucoup plus efficaces que les opérations terme à terme
            image=np.asarray(Image.fromarray(image).convert('RGB')).copy()
            
            #Ensuite, à chaque centre on associe une croix rouge qu'il faut mettre dans la photo. Pour faire la croix, on considère les deux droites d'équation y=x et y=-x.
            for (j,i) in liste_centres_1:
                if j<len(image)-11 and j>10 and i>10 and i<len(image[0])-11: #il ne faut pas dépasser les bords de l'image
#                    Le code pour faire un carré plutôt qu'une croix
                    for k in range(-3,3):
                        for l in range(-3,3):
                            image[j+k,i+l]=[255,0,0]

    #Si la photo à traiter est la photo 2 
    elif numero_photo==2:                
        #Il faut aussi appliquer un seuil pour éliminer tout le bruit. En effet, les petits points blancs qui constituent le bruit pourraient être comptés comme les objets que nous tentons de dénombrer
        T,image= cv2.threshold(image_entree, thresh2, 0, type=cv2.THRESH_TOZERO)
        
        #On applique un filtre gaussien à l'image, cf. internet pour comprendre ce que c'est
        image=cv2.GaussianBlur(image,(kernel2,kernel2),sig2)

        #On érode les différents objets, c'est-à-dire qu'on les amincit. De cette façon, les objets qui ne font que se toucher, pourront peut-être se séparer, selon les situations.
        kernel = np.ones((erosion2,erosion2),np.uint8)
        image = cv2.erode(image,kernel,iterations = 1)   
        
        #Maintenant, en fonction de la valeur de X2 on superpose des taches rouges sur notre image de départ
        #Si on veut afficher les croix sur la première photo
        if X2==1:
            #On récupère la liste des points rouges à placer
            liste_centres_2=positions(image,2)
            
            #Il faut convertir l'image en RGB (elle était en niveau de gris) car nous aurons des croix rouges dessus. On utilise les fonctions toutes faites des modules qui sont beaucoup plus efficaces que les opérations terme à terme
            image=np.asarray(Image.fromarray(image).convert('RGB')).copy()        
            
            #Ensuite, à chaque centre on associe une croix rouge qu'il faut mettre dans la photo. Pour faire la croix, on considère les deux droites d'équation y=x et y=-x.
            for (j,i) in liste_centres_2:
                if j<len(image)-11 and j>10 and i>10 and i<len(image[0])-11: #Il ne faut pas dépasser les bords de l'image
#                    Le code pour faire un carré plutôt qu'une croix
                    for k in range(-3,3):
                        for l in range(-3,3):
                            image[j+k,i+l]=[255,0,0]     
        
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
    thresh1=threshold1.get()
    thresh2=threshold2.get()
    kernel1=kernel_size1.get()
    kernel2=kernel_size2.get()
    sig1=sigma1.get()
    sig2=sigma2.get()
    erosion1=erosion_size1.get()
    erosion2=erosion_size2.get()
    radius1=filtering_radius1.get()
    radius2=filtering_radius2.get()
    
    thresh1=int(thresh1)
    kernel1=int(kernel1)
    sig1=int(sig1)
    erosion1=int(erosion1)
    radius1=int(radius1)
    X1=croix1.get()
    X2=croix2.get()
    
    #On considère le cas où on n'a pas encore modifié la photo 2 et celui où on l'a déjà fait
    if (thresh2,kernel2,sigma2,erosion2,radius2)==(0,0,0,0,0):
        #Dans le cas où on ne l'a pas encore fait, on donne les même valeurs aux paramètres de la photo 2 car il y des chances pour que les paramètres appliqués à la photo 1 soient tout à fait adaptés à la photo 2
        thresh2=thresh1
        kernel2=kernel1
        sig2=sig1
        erosion2=erosion1
        radius2=radius1
        threshold2.set(thresh1)
        kernel_size2.set(kernel1)
        sigma2.set(sig1)
        erosion_size2.set(erosion1)
        filtering_radius2.set(radius1)
    else:
        thresh2=int(thresh2)
        kernel2=int(kernel2)
        sig2=int(sig2)
        erosion2=int(erosion2)
        radius2=int(radius2)
        
    
    #On a récupéré toutes les valeurs, désormais, il faut transformer les photos en accord avec la demande de l'utilisateur
    if X1==1:
        #Si l'opérateur veut des croix sur ses photos on obtient une image en couleur
        p1_couleur=photo_processing(p1_depart,1)
        photo1=PIL.Image.fromarray(p1_couleur) #On fait la distinction p1 et P1_couleur car les tableaux n'ont pas les mêmes dimensions dans ce cas (on rajoute une dimension pour le RGB)
    else:
        p1=photo_processing(p1_depart,1)
        photo1=PIL.Image.fromarray(p1) #On fait la distinction p1 et P1_couleur car les tableaux n'ont pas les mêmes dimensions dans ce cas (on rajoute une dimension pour le RGB)
    
    if X2==1:
        p2_couleur=photo_processing(p2_depart,2)
        photo2=PIL.Image.fromarray(p2_couleur) #On fait la distinction p1 et P1_couleur car les tableaux n'ont pas les mêmes dimensions dans ce cas (on rajoute une dimension pour le RGB)
    else:
        p2=photo_processing(p2_depart,2)
        photo2=PIL.Image.fromarray(p2)
    
    
    #On a fait toutes les opérations sur les photos originales pour ne pas perdre d'information mais il faut ensuite les réadapter à la taille de notre fenêtre Tkinter
    hauteur=photo1.height
    largeur=photo1.width
    facteur=(screen_width//2-120)/largeur
    
    photo1=photo1.resize((int(facteur*largeur),int(facteur*hauteur)))    
    photo2=photo2.resize((int(facteur*largeur),int(facteur*hauteur)))
    
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
        fenetre.after(500,actualiser)
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
    
#Une fois que les valeurs des 12 paramètres ont été réglées on dispose également de la liste des positions des centres des maximas, et c'est tout ce dont nous avons besoin pour afficher nos résultats 
def resultats():
    """
    Input: None
    Output: None
    La fonction détruit la fenetre précédente pour en créer une nouvelle qui affichera les résultats des calculs.
    """
    global fenetre, liste_centres_1, liste_centres_2
    
    #Si on arrive sur le calcul des résultats c'est que nous en avons fini avec la première fenêtre dans laquelle il n'y a pas de place pour afficher les résultats, donc on la détruit
    fenetre.destroy()
    fenetre=Tk()
    
    #On calcule le nombre d'immobiles ainsi que le nombre total d'objets sur les deux images
    nombre_immobiles=0
    liste_centres_photo1=[(j,i) for (j,i) in liste_centres_1 if j<len(p1_depart)-11 and j>10 and i>10 and i<len(p1_depart[0])-11]
    liste_centres_photo2=[(j,i) for (j,i) in liste_centres_2 if j<len(p2_depart)-11 and j>10 and i>10 and i<len(p2_depart[0])-11]
    for x1,y1 in liste_centres_photo1:
        indice=0
        x2,y2=liste_centres_photo2[0]
        while (abs(x1-x2)>1 or abs(y1-y2)>1) and indice<len(liste_centres_photo2): #On considèrera qu'un objet n'a pas bougé s'il se trouve dans un rayon de quelques pixels autour de sa position initiale (le fait que les images soient traitées légèrement différemment apporte cette incertitude)
            x2,y2=liste_centres_photo2[indice]
            indice+=1
        if indice<len(liste_centres_photo2):
            nombre_immobiles+=1
    
    nombres_objets=[len(liste_centres_photo1),len(liste_centres_photo2)]
    
    #Ensuite on range tous les résultats dans un dictionnaire
    dico={}
    dico['Nombre objets photo 1']=int(nombres_objets[0])
    dico['Nombre objets photo 2']=int(nombres_objets[1])
    moyenne=sum(nombres_objets)/2
    dico["Nombre moyen d'objets"]=round(moyenne,2)
    dico["Nombre d'objets immobiles"]=nombre_immobiles
    ratio1=nombre_immobiles*(1/nombres_objets[0])
    ratio2=nombre_immobiles*(1/nombres_objets[1])
    ratio_moyen=(ratio1+ratio2)/2
    dico["Ratio moyen d'immobiles"]=round(ratio_moyen,2)
    dico['Ecart-type sur le ratio']=round(np.sqrt((ratio1-ratio_moyen)**2 + (ratio2-ratio_moyen)**2),2)
    

    #Et pour finir, on range tout cela dans notre nouvelle fenêtre, on veut former un tableaud de 6 lignes et 2 colonnes
    la1=Label(fenetre,text='Nombre objets photo 1',borderwidth=1).grid(row=0,column=0)
    la2=Label(fenetre,text=str(dico['Nombre objets photo 1']),borderwidth=1).grid(row=0,column=1)
    la3=Label(fenetre,text='Nombre objets photo 2',borderwidth=1).grid(row=1,column=0)
    la4=Label(fenetre,text=str(dico['Nombre objets photo 2']),borderwidth=1).grid(row=1,column=1)
    la5=Label(fenetre,text="Nombre moyen d'objets",borderwidth=1).grid(row=2,column=0)
    la6=Label(fenetre,text=str(dico["Nombre moyen d'objets"]),borderwidth=1).grid(row=2,column=1)
    la7=Label(fenetre,text="Nombre d'objets immobiles",borderwidth=1).grid(row=3,column=0)
    la8=Label(fenetre,text=str(dico["Nombre d'objets immobiles"]),borderwidth=1).grid(row=3,column=1)
    la9=Label(fenetre,text="Ratio moyen d'immobiles",borderwidth=1).grid(row=4,column=0)
    la10=Label(fenetre,text=str(dico["Ratio moyen d'immobiles"]),borderwidth=1).grid(row=4,column=1)
    la11=Label(fenetre,text="Ecart-type sur le ratio",borderwidth=1).grid(row=5,column=0)
    la12=Label(fenetre,text=str(dico["Ecart-type sur le ratio"]),borderwidth=1).grid(row=5,column=1)
    
    fenetre.mainloop()

starting_window()
