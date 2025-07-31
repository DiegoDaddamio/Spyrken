# Spyrken: Electronic Circuit Solver using Numerical Linear Algebra

## Installation:
```bash
pip install git+https://github.com/DiegoDaddamio/Spyrken.git#egg=spyrken
```
## Usage and Visualization:
This program is designed to solve simple circuits composed of linear components: resistors, capacitors, and inductors.

Several functions are available to visualize and analyze the given circuit:
```
voltage_phasors(circuit): Draws voltage phasors (rotating vectors) with animation.

voltage_phasors2(circuit): Draws voltage phasors with animation, offering smoother rendering.

plot_bode(circuit, from_node, to_node, points_range): Plots the output gain and phase response between two specified nodes (Bode plot).

scope(circuit, from_node, to_node): Simulates an oscilloscope, displaying the voltage waveform between two specified nodes.
```
