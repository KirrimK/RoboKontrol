"""Module serial_radio.py - gestion des communications via Serial"""

#fonction de récupération du fichier de configuration

#classe de l'objet SerialRadio (avec des placeholders)
class SerialRadio():
    """
    Objet devant gérer les communications par voie Série
    (pour l'instant rempli avec des méthodes placeholder
    devant être compatibles avec backend.py)

    Attributs:
        - config_file (str): chemin vers le fichier de configuration série
    """
    def __init__(self, config_file):
        self.config_file = config_file
        self.msgs_buffer = []
        self.cmds_buffer = []
        self.record_msgs = False
        self.record_cmds = False

    def start(self):
        """Démarrage de la SerialRadio"""

    def stop(self):
        """Arrêt de la SerialRadio"""

    def send_cmd(self, cmd):
        """Envoie un message sur le canal série,
        après conversion de regex vers message série

        Entrée:
            - cmd (str): le message à envoyer, sous forme texte"""

    def register_start(self, *args):
        """Démarre l'enregistrement des messages et/ou commandes"""
        #TODO: renommer les types d'enrg(dans ivyradio aussi) à un nom plus explicite?
        #revoir les arguments de register_start/stop

    def register_stop(self, save=True, del_buffer=True, *args):
        """Arrête l'enregistrement des messages et/ou commandes"""
        #dans le fichier d'enregistrement,
        # le fichier de config devrait être réécrit à des fins de compat
