# RoboKontrol

Une application Python/Qt servant d'interface pour le contrôle de robots et/ou simulateurs de robots développés par le club ENAC Robotique.

Développée pour le projet programmation python en première année ingénieur à [l'ENAC](https://www.enac.fr) dans le cadre du sujet "[Interface de contrôle d'un robot](https://e-campus.enac.fr/moodle/pluginfile.php/34661/course/section/23938/projet%20python%20-%20Interface%20de%20contr%C3%B4le%20dun%20robot.pdf)".

## Installation:

- Cloner le dépôt dans le dossier de votre choix: `git clone https://github.com/KirrimK/RoboKontrol`
- Installer les librairies python requises: `pip install ivy-python lxml PyQt5`
- Sous Linux, il peut être nécessaire d'installer le paquet QtSvg séparément: `sudo apt-get install python3-pyqt5.qtsvg` (sous Ubuntu)

## Utilisation:

### Lancer l'application
En l'absence de robot, le programme suivant est un simulateur compatible: [https://github.com/Fabien-B/robotSim](https://github.com/Fabien-B/robotSim)

Pour lancer l'application, executer `main.py`.

### Mode d'emploi

#### CONNECTER UN ROBOT

Les robots qui sont dans le canal Ivy de l'interface sont automatiquement affichés sur celle ci.

#### COMMENT GUIDER LE ROBOT
Pour envoyer une commande de position à un robot, vous pouvez selectionner le tab robot correspondant, et cliquer sur la carte.

Pour envoyer une commande de position avec une orientation au robot, vous pouvez soit modifier la ligne de commande dernière position, soit déplacer la souris pendant un clic sur la carte.

Pour envoyer une commande de vitesse au robot, vous pouvez utilisez les touches suivantes :
- Z : Vers l'avant
- S : Vers l'arrière
- Q : Tourner vers la gauche
- D : Tourner vers la droite
- Shift: Avancer/Reculer plus vite

#### ENREGISTREMENT

Pour enregistrer les messages et les commandes envoyées, appuyez sur le bouton record. Le bouton devrait se colorer en rouge, et un label en dessous de la carte vous indiquera le nombre de messages ayant été captés par la radio et qui sont enregistrés.

Pour arrêter l'enregistrement, vous avez deux options :
- Le bouton Stop :
Il arrête l'enregistrement en effaçant les données.
- Le bouton Save :
Il arrête l'enregistrement et sauvegarde les données dans le dossier dont l'adresse est indiquée dans le paramètre [Enregistrement/Playback (Chemin Sauvegarde)] sous la forme d'un fichier de messages et d'un fichier de commandes.

#### LECTURE

Pour le bouton lecture, vous avez besoin d'un fichier respectant la même syntaxe que ceux qu'enregistre l'interface. Selectionnez ce fichier dans le menu qui s'ouvre après l'appui du bouton.

Sélectionner un fichier "messages" vous permettra de revoir
les déplacements effectués par vos robots ainsi
que les états des différents équipements de celui-ci.

Sélectionner un fichier "commandes" vous permettra de rejouer une séquence
de commandes enregistrées précédemment,
qui seront exécutées par les robots actuellement connectés,
si leur nom correspond à ceux des robots mentionnés dans le fichier.

---
<div>L'icone de l'application a été réalisée par <a href="https://creativemarket.com/eucalyp" title="Eucalyp">Eucalyp</a> du site <a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com</a></div>
