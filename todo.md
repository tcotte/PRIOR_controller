*Cf mail Alban at April 14th 2023*

### Tasks

0. Move in the XY stage
1. Read X and Y postiions in real time


    real_time_positions_demo function


2. Return the XYScale to home position (0, 0)


    return2home_demo function

4. Define origins of X and Y positions 
    

    set_new_home_demo

5. Handle the scale

if (step_size == 1 and resolution == 1) -> 1 codded step equals 1 µm


6. Handle S_Curve

s_curve property does not work : the command is not recognized by the controller or the XY scale.     
(See E111 XY scale datasheet : https://www.prior.com/wp-content/uploads/2017/07/ES111%20Datasheet.pdf)      
*The unique S curve acceleration algorithm allows fast, smooth positioning without vibration, reducing disruption to 
sample*






##############    
team :   

mardi matin : création de l'application qui permet de détecter automatiquement le light_controller : 0.5
mardi aprem : rtt
mercredi : rtt
jeudi : reunion avec IDEA pour presenter le modèle IA : 0.2
        preparation de la reunion : 0.1
        point avec Alban + discussion autour de la gestion XY du microscope : 0.1
        discussion avec prestataire pour fixer le tarif annotations IDEA précipité : 0.2
        preparation du dataset pour prestataire : 0.4
        developpement de l'application qui permet de détecter le light_controller

vendredi : développement de l'ui pour la gestion xy du microscope




#########
TODO

- Z est monté à l'envers
- Pouvoir setter une position de home pour XY et Z (dans command general)
- S'interfacer avec la caméra
- Systeme de grille
- Gestion du focus avec l'axe Z


##############
- recherche sur le focus en Z
- recherche sur le stitching
- améliorer et commenter la grid
=======



#############
- Recouvrement en x et y ( positif = écart, négatif = recouvrement) le tout en %

#############
- Evaluer sharpness et motorisation en Z
- Evaluer la possibilité de passer le logiciel vers Proscan II



#########
- Enlever les doublons dans la grille quand on change de colonne
- Enlever les rations dans la grid pour éviter d'avoir de mauvaises valuers en résultat
- 20% en x = 304. En fait une window fait ~250µm (850/4=212.5µm)
- regarder à partir de combien de step on peut faire l'algo fp12


#########
- faire la diagonale
- plotter les differentes courbes de sober avec differnetes values de y (10 points)

LA DIAGONALE :  z [100, 600]
                y [0, -17800]
                x [0, 5624]
10 points.


###################
0. Revoir la grille
1. Faire des acquisitions avec des overlaps différents
2. Explorer PyimageJ -> recreer l'image stitchée en python avec la lib
3. Faire le test image par image / tout d'un coup -> comparaison


###################
1. colorier les cellules qui ont été passées en vert
2. Ajouter la la progession dans un module ind
3. Heure du start run 
4. depuis cb de temps on a démarré
5. Transformer le QFrame en vue



400 -> 640
100 -> 640*100/400 = 640/4 = 460