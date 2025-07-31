# electric_circuit_simulator/__init__.py

# Importez les classes principales pour les rendre accessibles directement depuis le package
from .components import Component, Resistor, Capacitor, Inductor, VoltageSource
from .circuit import Circuit, Node
from .draw import *

# Définissez une version pour le package
__version__ = "0.1.7"

# Vous pouvez également ajouter une description du package
__description__ = "Simulateur de circuits électriques linéaire pour l'analyse et la visualisation de ceux-ci."

# Facultatif : Ajouter des informations supplémentaires
# __author__ = "DiegoDaddamio"
# __email__ = "diego.daddamio3110@gmail.com"
# __url__ = "https://github.com/DiegoDaddamio/Spyrken.git"