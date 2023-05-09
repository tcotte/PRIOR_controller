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