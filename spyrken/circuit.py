import numpy as np
from .components import *

class Node:
    """Représente un nœud dans le circuit"""
    def __init__(self, name=None):
        self.name = name if name else f"Node_{id(self)}"
        self.components = []  # Composants connectés à ce nœud
        self.voltage = 0      # Potentiel du nœud
        self.current = 0
    
    def connect(self, component):
        self.components.append(component)
        
    def __str__(self):
        return f"{self.name}: V={self.voltage}V, {len(self.components)} élément(s) lié(s)"
    

class Circuit:

    def __init__(self):
        self.components = []
        self.nodes = []
        self.freq = 0
        self._solved = False

    def set_circuit(self,circuit):
        self.components = circuit

    def add_component(self,component):
        self.components.append(component)

    def add_node(self,name=None):
        node = Node(name)
        self.nodes.append(node)
        return node
    
    def set_frequency(self, f):
        self.freq = f

    def solve(self):
        """Résout le circuit en utilisant la méthode des noeuds"""
        # Rechercher les sources de tension AC
        ac_sources = [comp for comp in self.components if isinstance(comp, VoltageSource) and comp.freq > 0]
        
        # Déterminer la fréquence d'analyse
        if ac_sources:
            if len(set(src.freq for src in ac_sources)) > 1:
                print("Attention: Plusieurs sources AC avec des fréquences différentes détectées.")
                print("L'analyse supposera une fréquence dominante.")
            
            # Utiliser la fréquence de la première source AC
            self.freq = ac_sources[0].freq
        if len(self.nodes) < 2:
            print("Erreur: Au moins deux noeuds sont nécessaires.")
            return False
            
        # 2. Prendre le premier noeud comme référence (masse)
        reference_node = self.nodes[0]
        reference_node.voltage = 0  
        other_nodes = self.nodes[1:]
        
        # 3. Construire la matrice d'admittance (Y) et le vecteur de courants (I)
        n = len(other_nodes)
        Y = np.zeros((n, n), dtype=complex)  # Matrice d'admittance
        I = np.zeros(n, dtype=complex)       # Vecteur de courants
        
        # 4. Pour chaque composant, ajouter sa contribution à la matrice Y
        for component in self.components:
            node1, node2 = component.nodes
            
            # Ignorer les composants non connectés
            if node1 is None or node2 is None:
                print(f"Avertissement: Composant {component.name} non connecté.")
                continue
                
            # Calculer l'admittance Y = 1/Z à la fréquence actuelle
            Z = component.get_imp_cplx(self.freq)
            
            # Vérifier si Z est None
            if Z is None:
                print(f"Erreur: get_imp_cplx() a retourné None pour {component.name}")
                return False
                
            Y_comp = 1 / Z if abs(Z) > 1e-12 else 1e12
            # Ajouter la contribution aux éléments appropriés de la matrice Y
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
                
        # 5. Pour chaque source de tension, modifier Y et I
        for component in self.components:
            if isinstance(component, VoltageSource):
                node1, node2 = component.nodes
                V_source = component.source_voltage
                Z_source = component.get_imp_cplx(self.freq)
                Y_source = 1 / Z_source if abs(Z_source) > 1e-12 else 1e12
                
                if node1 != reference_node and node2 == reference_node:
                    i = other_nodes.index(node1)
                    I[i] += V_source * Y_source  # Utiliser Y_source au lieu de Y_comp
                elif node2 != reference_node and node1 == reference_node:
                    j = other_nodes.index(node2)
                    I[j] -= V_source * Y_source  # Utiliser Y_source au lieu de Y_comp
                    
        # 6. Résoudre le système Y⋅V = I
        try:
            V = np.linalg.solve(Y, I)
            self._solved = True
            # 7. Mettre à jour les tensions des nœuds
            for i, node in enumerate(other_nodes):
                node.voltage = V[i]
            
            # 8. Calculer les tensions et courants de chaque composant
            for component in self.components:
                node1, node2 = component.nodes
                if node1 and node2:
                    component.voltage = node1.voltage - node2.voltage
                    component.calc_I(self.freq)
            
            return True
        
        except np.linalg.LinAlgError:
            self._solved = False
            print("Erreur: Impossible de résoudre le système. Vérifiez votre circuit.")
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
    
    