from spyrken import *

# Création du circuit et des noeuds (équipotentiels)
circuit = Circuit()

gnd = circuit.add_node("gnd",ground=True)
n1 = circuit.add_node("n1")
n2 = circuit.add_node("n2")
v_source = circuit.add_node("V_source")

# Configuration d'un circuit linéaire
R1 = Resistor(1, "R1")
C1 = Capacitor(1e-6, "C1")  
L1 = Inductor(10e-3,"L1")
V = VoltageSource(12, 1560,0 ,name="V") 

#Rajout des composants dans le circuit
circuit.add_component([V,R1,C1,L1])

#Configuration des noeuds
V.connect(v_source, gnd)
R1.connect(v_source, n1)
L1.connect(n1,n2)
C1.connect(n2, gnd)

# Résolution
circuit.solve()

# Affichage des résultats
circuit.display()
