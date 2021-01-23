# RoboKontrol

Une application Python/Qt servant d'interface pour le contrôle de robots et/ou simulateurs de robots développés par le club ENAC Robotique.

Développée pour le projet programmation python en première année ingénieur à [l'ENAC](https://www.enac.fr) dans le cadre du sujet "[Interface de contrôle d'un robot](https://e-campus.enac.fr/moodle/pluginfile.php/34661/course/section/23938/projet%20python%20-%20Interface%20de%20contr%C3%B4le%20dun%20robot.pdf)".

Auteurs: Rémy Brévart, Victor De Crevoisier, Hippolyte Foulongne, Jacques Serien
(N'hésitez pas à nous rapporter les bugs trouvés sur GitHub.)

## Installation:

- Cloner le dépôt dans le dossier de votre choix: `git clone https://github.com/KirrimK/RoboKontrol`
- Installer les librairies python requises: `pip install ivy-python lxml PyQt5`
- Sous Linux, il peut être nécessaire d'installer le paquet QtSvg séparément: `sudo apt-get install python3-pyqt5.qtsvg` (sous Ubuntu)
- Sur les installations python >= 3.9, il est possible que la librairie Ivy fasse toujours appel à une fonction dépréciée de python 3.8 qui n'existe plus. Si ce problème vous arrive, référez-vous à ce lien: [https://gitlab.com/ivybus/ivy-python/-/issues/1](https://gitlab.com/ivybus/ivy-python/-/issues/1)

## Utilisation:

### Lancer l'application
En l'absence de robot, le programme suivant est un simulateur compatible: [https://github.com/Fabien-B/robotSim](https://github.com/Fabien-B/robotSim)

Pour lancer l'application, executer `main.py` dans le dossier `src`.

### Mode d'emploi

#### CONNECTER UN ROBOT

Les robots qui sont dans le canal Ivy de l'interface sont automatiquement affichés sur celle ci.

Merci d'éviter de connecter des robots dont le nom se termine en "_ghost".
Il est préférable de réserver ce genre de nom aux robots crées automatiquement lors d'une lecture de fichiers.

#### COMMENT GUIDER LE ROBOT

Pour sélectionner un robot, cliquer sur l'onglet portant son nom dans l'inspecteur, ou faites un clic droit sur sa représentation sur la carte.
Une fois le robot sélectionné, vous pouvez lui envoyer une commande de position en cliquant (gauche) sur la carte, ou en entrant des coordonnées
dans le champ prévu à cet effet.

Si vous souhaites envoyer une commande de position avec un cap au robot depuis la carte, cliquez sur la destination, et maintenez le clic tout en glissant afin de dessiner le cap voulu sur la carte.

Vous pouvez contrôler le robot sélectionné avec votre clavier en utilisant les touches suivantes :
- Z : Avancer
- S : Reculer
- Q : Tourner vers la gauche
- D : Tourner vers la droite
- Shift: Avancer/Reculer plus vite

#### ENREGISTREMENT

Pour enregistrer les messages et les commandes envoyées, appuyez sur le bouton record. Le bouton deviendra rouge, et un indicateur en dessous de la carte vous indiquera le nombre de messages ayant été enregistrés.

Pour arrêter l'enregistrement, vous avez deux options :
- Le bouton Stop :
Il arrête l'enregistrement en effaçant les données.
- Le bouton Save :
Il arrête l'enregistrement et sauvegarde les données dans le dossier dont l'adresse est indiquée dans le paramètre [Enregistrement/Playback (Chemin Sauvegarde)] sous la forme d'un fichier de messages et d'un fichier de commandes.

#### LECTURE

Vous pouvez rejouer des évènements ou des séquences de commandes enregistrées dans les fichiers enregistrés par l'application.
Selectionnez un fichier à l'aide de l'explorateur de fichier qui s'ouvre en cliquant sur Play (|>).

Cliquer sur Pause (||) mettra en pause la lecture du fichier actuellement chargé. Cliquez sur Play (|>) pour reprendre la lecture.

Cliquer sur Stop arrêtera la lecture du fichier. Cliquer sur Play (|>) par la suite vous permettra de choisir un nouveau fichier à lire.

Les fichiers sont distingués par leur nom:
- Sélectionner un fichier "messages" vous permettra de revoir
les déplacements effectués par vos robots ainsi
que les états des différents équipements de celui-ci au cours du temps.
Les vrais robots/simulateurs connectés à l'application ne seront pas affectés par la relecture.

- Sélectionner un fichier "commandes" vous permettra de rejouer une séquence
de commandes enregistrées précédemment,
qui seront exécutées par les robots actuellement connectés,
si leur nom correspond à ceux des robots mentionnés dans le fichier et si leur configuration d'équipement correspond.

---
<div>L'icone de l'application a été réalisée par <a href="https://creativemarket.com/eucalyp" title="Eucalyp">Eucalyp</a> du site <a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com</a></div>
