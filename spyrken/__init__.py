# electric_circuit_simulator/__init__.py
from .components import Component, Resistor, Capacitor, Inductor, VoltageSource
from .circuit import Circuit, Node
from .draw import *

__version__ = "0.1.7"

__description__ = "Electronic Circuit Solver using Numerical Linear Algebra"
__author__ = "DiegoDaddamio"
__email__ = "diego.daddamio3110@gmail.com"
__url__ = "https://github.com/DiegoDaddamio/Spyrken"
