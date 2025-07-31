import numpy as np
from .components import *

class Node:
    """Représente un nœud dans le circuit"""
    def __init__(self, name=None, ground=False):
        self.name = name if name else f"Node_{id(self)}"
        self.components = []  # Composants connectés à ce nœud
        self.voltage = 0      # Potentiel du nœud
        self.current = 0
        self.isG = ground
        self.priority = 0     # Priorité du nœud (plus élevée pour ground)
        
        # Si c'est un nœud de référence, sa priorité est maximale
        if ground:
            self.priority = 1000
    
    def connect(self, component):
        """Connecte un composant à ce nœud"""
        if component not in self.components:
            self.components.append(component)
            
            # Si ce nœud est connecté à une source, augmenter sa priorité
            if isinstance(component, VoltageSource):
                self.priority += 100
            
    def is_connected(self):
        """Vérifie si le nœud est connecté à au moins un composant"""
        return len(self.components) > 0
    
    def __str__(self):
        status = "GND" if self.isG else f"V={self.voltage}V"
        return f"{self.name}: {status}, {len(self.components)} élément(s) lié(s)"
    

class Circuit:
"""Représente la breadboard du circuit"""
    def __init__(self):
        self.components = []
        self.nodes = []
        self.freq = 0
        self._solved = False


    def add_component(self,component):
        if isinstance(component,list):
            for comp in component:
                self.components.append(comp)
        else:
            self.components.append(component)
    
    def add_node(self, name=None, ground=False):
        """Ajoute un nœud au circuit"""
        node = Node(name, ground)
        self.nodes.append(node)
        
        # Si c'est un nœud de masse, le placer en premier dans la liste
        if ground:
            self.nodes.remove(node)
            self.nodes.insert(0, node)
        
        return node

    def add_ground_node(self, name="GND"):
        """Ajoute un nœud de masse au circuit"""
        # Vérifier si un nœud de masse existe déjà
        for node in self.nodes:
            if node.isG:
                return node
        
        return self.add_node(name, True)
    
    def set_frequency(self, f):
        self.freq = f

    def comp_order(self):
        components = self.components
        for comp in components:
            if comp._firstorder:
                components.remove(comp)
                components.insert(0,comp)
        self.components = components
    

    def solve(self):
        """Résout le circuit en utilisant la méthode des noeuds avec détection automatique de référence"""
        # Rechercher les sources de tension AC
        ac_sources = [comp for comp in self.components if isinstance(comp, VoltageSource) and comp.freq > 0]
        
        # Déterminer la fréquence d'analyse
        if len(ac_sources) > 0:
            if len(set(src.freq for src in ac_sources)) > 1:
                print("Attention: Plusieurs sources AC avec des fréquences différentes détectées.")
                print("L'analyse supposera une fréquence de la première source AC.")
            
            # Utiliser la fréquence de la première source AC
            self.freq = ac_sources[0].freq
        else:
            # Circuit DC par défaut
            self.freq = 0
        
        if len(self.nodes) < 2:
            print("Erreur: Au moins deux nœuds sont nécessaires pour l'analyse.")
            return False
        
        # Organiser les composants par priorité
        self.comp_order()
        
        # Vérifier que tous les composants sont connectés
        for component in self.components:
            if None in component.nodes or len(component.nodes) < 2:
                print(f"Erreur: Le composant {component.name} n'est pas correctement connecté.")
                return False
        
        # Trouver le nœud de référence (GND)
        reference_node = None
        for node in self.nodes:
            if node.isG:
                reference_node = node
                break
        
        # Si aucun nœud de masse n'est désigné, prendre le nœud avec la priorité la plus élevée
        if reference_node is None:
            nodes_sorted = sorted(self.nodes, key=lambda n: n.priority, reverse=True)
            reference_node = nodes_sorted[0]
            print(f"Aucun nœud de masse défini, utilisation de {reference_node.name} comme référence.")
        
        reference_node.voltage = 0  # Définir la tension de référence à 0
        
        # Identifier les autres nœuds dans l'ordre de priorité
        other_nodes = [n for n in self.nodes if n != reference_node]
        other_nodes.sort(key=lambda n: n.priority, reverse=True)
        
        # Construire la matrice d'admittance (Y) et le vecteur de courants (I)
        n = len(other_nodes)
        if n == 0:
            print("Erreur: Aucun nœud à analyser après avoir défini la référence.")
            return False
            
        Y = np.zeros((n, n), dtype=complex)  # Matrice d'admittance
        I = np.zeros(n, dtype=complex)       # Vecteur de courants
        
        # Pour chaque composant, ajouter sa contribution à la matrice Y
        for component in self.components:
            node1, node2 = component.nodes
            
            # Calculer l'admittance Y = 1/Z à la fréquence actuelle
            try:
                Z = component.get_imp_cplx(self.freq)
                if abs(Z) < 1e-12:
                    Y_comp = 1e12  # Limite pour éviter division par zéro
                else:
                    Y_comp = 1 / Z
            except Exception as e:
                print(f"Erreur lors du calcul de l'impédance pour {component.name}: {e}")
                return False
            
            # Construction de la matrice selon les indices des nœuds
            if node1 != reference_node and node2 != reference_node:
                i = other_nodes.index(node1)
                j = other_nodes.index(node2)
                Y[i, i] += Y_comp
                Y[j, j] += Y_comp
                Y[i, j] -= Y_comp
                Y[j, i] -= Y_comp
            elif node1 == reference_node and node2 != reference_node:
                j = other_nodes.index(node2)
                Y[j, j] += Y_comp
            elif node2 == reference_node and node1 != reference_node:
                i = other_nodes.index(node1)
                Y[i, i] += Y_comp
        
        # Pour chaque source de tension, modifier matrice Y et vecteur I
        for component in self.components:
            if isinstance(component, VoltageSource):
                node1, node2 = component.nodes
                V_source = component.source_voltage
                
                # Obtenir l'admittance de la source
                try:
                    Z_source = component.get_imp_cplx(self.freq)
                    Y_source = 1 / Z_source if abs(Z_source) > 1e-12 else 1e12
                except Exception as e:
                    print(f"Erreur lors du calcul de l'impédance de la source {component.name}: {e}")
                    return False
                
                # Application correcte des sources au vecteur I
                if node1 != reference_node and node2 == reference_node:
                    i = other_nodes.index(node1)
                    I[i] += V_source * Y_source
                elif node2 != reference_node and node1 == reference_node:
                    j = other_nodes.index(node2)
                    I[j] -= V_source * Y_source
                elif node1 != reference_node and node2 != reference_node:
                    i = other_nodes.index(node1)
                    j = other_nodes.index(node2)
                    I[i] += V_source * Y_source
                    I[j] -= V_source * Y_source
        
        # Résoudre le système Y⋅V = I
        try:
            # Vérifier si la matrice est singulière
            det = np.linalg.det(Y)
            if abs(det) < 1e-10:
                print("Erreur: La matrice d'admittance est singulière (déterminant proche de zéro).")
                print("Vérifiez qu'il n'y a pas de boucles de sources de tension ou de composants isolés.")
                self._solved = False
                return False
            
            V = np.linalg.solve(Y, I)
            self._solved = True
            
            # Mettre à jour les tensions des nœuds
            for i, node in enumerate(other_nodes):
                node.voltage = V[i]
            
            # Calculer les tensions et courants de chaque composant
            for component in self.components:
                node1, node2 = component.nodes
                if node1 and node2:
                    component.voltage = node1.voltage - node2.voltage
                    component.calc_I(self.freq)
            
            return True
        
        except np.linalg.LinAlgError as e:
            self._solved = False
            print(f"Erreur: Impossible de résoudre le système: {e}")
            print("Assurez-vous que le circuit est bien connecté et qu'il n'y a pas de boucles de sources de tension.")
            return False
    
    def display(self):
        """Affiche l'état actuel du circuit"""
        print("Circuit:")
        print(f"  Fréquence: {self.freq} Hz")
        print(f"  Composants: {len(self.components)}")
        for component in self.components:
            print(f"    {component}")
        print(f"  Noeuds: {len(self.nodes)}")
        for node in self.nodes:
            print(f"    {node}")
    
    
