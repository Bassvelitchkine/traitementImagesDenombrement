# Traitement d'image pour le dénombrement et l'analyse de la mobilité de petits objets

## Motivations

J'ai réalisé ce projet lorsque j'ai travaillé comme stagiaire dans une startup. L'entreprise était régulièrement amenée à dénombrer de tout petits objets. Par ailleurs, ces petits objets étaient parfois déplacés par inadvertance, si bien qu'il était nécessaire de savoir combien d'entre eux avaient bougé. Ces deux tâches à elles seules étaient chronophages, rébarbatives et soumises aux imprécisions de mesure (grand nombre d'objets de très petite taille).

C'est ainsi que m'est venue l'idée d'automatiser ces deux tâches avec l'aide de Python et des librairies développées pour le traitement d'image. Je me suis approché aussi près que possible de mon but malgré de grandes imperfections (voir `conclusion`).

## Cahier des charges

- Il fallait que mes programmes respectent quelques conditions pour être intéressants :
  - Plus rapide que les tâches manuelles
  - Plus précis
  - Simple d'utilisation (emploi d'une interface)

## Pipeline

### Traitement des images

Les photos étaient prises en noir et blanc car les objets à dénombrer étaient blancs et photographiés sur un fond noir. Il a fallu au maximum les faire se distinguer de leur environnement. Pour cela, il a fallu appliquer des seuils, des flous multiples, etc.

### Analyse des images : différents paradigmes

#### Pour le dénombrement

- J'ai envisagé plusieurs solutions au départ :
  - Trouver les maxima locaux et les dénombrer (les pixels ont des valeurs comprises entre 0 pour le noir et 255 pour le blanc, plus la valeur est élevée, plus on est susceptible d'être sur un pixel correspondant à un objet à dénombrer)
  - Evaluer la surface totale de blanc (en pixel) sur l'image pour la diviser par la taille standard d'un objet à dénombrer.

La deuxième méthode, la plus classique, s'est finalement avérée être la plus efficace avec les moyens dont je disposais. En revanche, j'y ai ajouté ma touche personnelle. Comme la taille standard d'un objet à dénombrer était susceptible de varier d'une photo à l'autre, il fallait pouvoir la recalculer à chaque fois. Pour y parvenir, il a fallu extraire toutes les composantes connexes de la photographie (paquets de pixels blancs) et évaluer la taille moyenne d'une centaine de ces composantes connexes.

#### Pour connaitre la proportion d'objets déplacés

Ce sont les deux mêmes options qui ont été envisagées. Cette fois-ci c'est la première qui a semblé être la plus efficace. Il s'agit de trouver les maxima locaux et de les identifier avec les position des centres des objets à analyser. En comparant deux photos prises à deux instants différents (avant et après déplacement), et en comparant les positions des maxima sur les deux photos, j'ai espéré trouver la proportion d'objets déplacés.

### Interface graphique

J'ai du envelopper mes algorithmes dans l'interface graphique Tkinter pour que les opérateurs puissent ajuster facilement les paramètres appliqués sur les photos (par exemple le rayon du flou gaussien).

## Prerequisites

Les trois principaux modules dont je me suis servi sont opencv, mahotas et Tkinter à installer avec l'invite de commande d'Anaconda pour ceux qui utilisent la distribution Anaconda.

## Démarrage

Clônez le répo et exécutez le script de votre choix. Les fichiers comportant le mot _mobilite_ permettent, avec deux photos de connaitre la proportion d'objets déplacés. Les fichiers comportant le mot _denombrement_ permettent de dénombrer les objets.

Suivez les instructions des interfaces graphiques, c'est aussi simple que ça !

## Conclusion

Si le dénombrement des petits objets est assez performant, le calcul de la proportion d'objets ayant bougé est beaucoup plus bancale.

## Authors

- **Bastien Velitchkine** - [Bassvelitchkine](https://github.com/Bassvelitchkine)
