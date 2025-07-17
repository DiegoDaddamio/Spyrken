from spyrken import Circuit, Resistor, Capacitor, VoltageSource
import numpy as np
from spyrken.draw import plot_bode2,plot_bode, voltage_phasors

# Création du circuit
circuit = Circuit()

gnd = circuit.add_node("gnd")
n1 = circuit.add_node("n1")
v_source = circuit.add_node("V_source")

# Configuration pour un filtre passe-bas/haut
R1 = Resistor(100, "R1")
C1 = Capacitor(1e-6, "C1")  # Filtre passe-bas à 1.59 kHz 
V = VoltageSource(12, 100,0 ,name="V")  # Fréquence initiale à 0 (ignorée avec plot_bode2)

# Connexions corrigées
circuit.add_component(R1)
circuit.add_component(C1)
circuit.add_component(V)

V.connect(v_source, gnd)
R1.connect(v_source, n1)
C1.connect(n1, gnd)

# Résolution et tracé
circuit.solve()
voltage_phasors(circuit)


plot_bode(circuit, gnd, v_source, np.logspace(0, 5, 1000))  # De 1 Hz à 100 kHz
