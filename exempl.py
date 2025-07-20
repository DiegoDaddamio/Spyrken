from Spyrken import *

circuit = Circuit()

# Créez les nœuds d'abord
n3 = circuit.add_node("n3",True)
n1 = circuit.add_node("n1")
n2 = circuit.add_node("n2")


# Créez vos composants
V = VoltageSource(12, 30, 0, name="V_source")  # Ajoutez la fréquence (0 pour DC)
R = Resistor(200, "R")
R_mid = Resistor(400, "R_mid")


# Connectez les composants aux nœuds
V.connect(n1, n3)
R.connect(n1, n2)
R_mid.connect(n2, n3)


# Ajoutez les composants au circuit
circuit.add_component(V)
circuit.add_component(R)
circuit.add_component(R_mid)

# Résolvez
circuit.solve()
scope(circuit,n3,n2)
