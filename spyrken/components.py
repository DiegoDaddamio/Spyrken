import numpy as np

class Component:
    """Classe de base pour les composants électriques"""
    def __init__(self, value, name=None):
        self.value = value
        self.name = name
        self.phase = 0
        self.cplx_imp = None
        self.unit = None
        self.voltage = 0
        self.current = 0
        self._firstorder = False
        self.A_imp = None
        self.nodes = [None, None]  # Nœuds auxquels le composant est connecté
    def get_I(self, f=0):
        """Calcule le courant traversant le composant"""
        pass
    
    def get_imp_cplx(self, f=0):
        """Retourne l'impédance complexe du composant"""
        pass
    
    def connect(self, node1, node2):
        """Connecte le composant à deux nœuds du circuit"""
        self.nodes = [node1, node2]
        # Ajouter ce composant à la liste des composants connectés à chaque nœud
        node1.connect(self)
        node2.connect(self)
        
    def __str__(self):
        if hasattr(self, 'source_voltage'):
            return f"{self.name}: {self.source_voltage} V, f={getattr(self, 'freq', 0)} Hz"
        else:
            return f"{self.name}: {self.value}, Z={self.cplx_imp} Ω, I={self.current}A "
        
class Resistor(Component):
    """Sous classe de composant : résistance"""
    def __init__(self, R, name=None):
        super().__init__(R, name)
        self.cplx_imp = R
        self.phase = 0
    
    def calc_I(self, f=0):  # Ajout du paramètre f avec une valeur par défaut
        self.current = self.voltage/self.value
        return self.current
    
    def get_imp_cplx(self, f=0):
        return complex(self.value, 0)
    
class Capacitor(Component):
    """Sous classe de composant : condensateur"""
    def __init__(self, C, name=None):
        super().__init__(C, name)
        self.phase = -1j
    def calc_I(self,f):
        if f != 0:
            self.current = self.voltage/self.cplx_imp
        else :
            self.current = 0 
        return self.current
    
    def get_imp_cplx(self, f=0):
        if f == 0:
            self.cplx_imp = complex(1e12, 0)
            return self.cplx_imp  # Retourner directement la valeur
        else:
            w = 2 * np.pi * f
            self.cplx_imp = complex(0, -1/(w * self.value))
            return self.cplx_imp  # Retourner directement la valeur
    
class Inductor(Component):
    """Sous classe de composant : bobine"""
    def __init__(self, L, name=None):
        super().__init__(L, name)
        self.phase = 1j
    def calc_I(self,f):
        self.get_imp_cplx(f)
        if f != 0:
            self.current = self.voltage/self.cplx_imp
        else :
            self.current = None
        return self.current
    
    def get_imp_cplx(self, f):
            w = 2 * np.pi * f
            self.cplx_imp = complex(0, w * self.value)
            return self.cplx_imp  # Retourner directement la valeur
    
class VoltageSource(Component):
    def __init__(self, voltage, f=0, internal_resistance=0, name=None):
        super().__init__(internal_resistance, name)
        self.source_voltage = voltage
        self.r_int = internal_resistance
        self.freq = f
        self._firstorder = True
        
    def set_frequency(self, f):
        self.freq = f
        
    def get_imp_cplx(self,f):
        return complex(self.value, 0)
    
    def calc_I(self,f):
        """Calcule le courant à travers la source de tension"""
        # Pour une source de tension idéale, le courant est déterminé 
        # par le reste du circuit et non par la source elle-même
        # Cependant, si une résistance interne est spécifiée, on peut calculer:
        if self.r_int > 0:
            self.current = self.voltage / self.r_int
        else:
            # Pour une source idéale, le courant est défini par le circuit
            # Cette valeur sera mise à jour correctement après résolution complète
            pass
        
        return self.current