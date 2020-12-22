##configuration carte
#Largeur_carte=input("largeur de la carte:")
#Longueur_carte=input("longueur de la carte:")
#nb_bases=input("nombres de bases:")
#couleur_base =input("couleur de base:")
#position_base=input("position de la base")
class Config:
    def __init__(self,config):
        self.config=[]
    def ajoute_bases(self):
        bases=[]
        Largeur_base=input("largeur de la carte:")
        Longueur_base=input("longueur de la carte:")
        couleur_base =input("couleur de base:")
        position_base=input("position de la base")
        nb_bases=input("nombres de bases:")
        for i in range(nb_bases):
            bases.append([Largeur_base,Longueur_base,couleur_base,nb_bases])
    def configuration(self):
        self.config.append([Largeur_carte,Longueur_carte])
        self.config.append(bases)
#todo #gestion des erreurs                
#class DrawMap:
                