# Spyrken : Projet de résolution de circuit électronique par l'algèbre linéaire numérique

## Installation :
```bash
pip install git+https://github.com/DiegoDaddamio/Spyrken.git#egg=spyrken
```
## Utilisation et visualisation :
Le programme est fait pour résoudre des circuits simples à composants linéaires; résistance, condensateur et bobine.

Il existe plusieurs fonctions pour visualiser/analyser le circuit donné :

```
voltage_phasors(circuit) : Dessine les vecteurs tourants de Fresnel avec animation.

voltage_phasors2(circuit) : Dessine les vecteurs tourants de Fresnel avec animation mais avec plus de fluidité.

plot_bode(circuit,from_node,to_node,points_range) : Dessine, entre deux noeuds, le gain en sortie ainsi que la phase.

scope(circuit,from_node,to_node) : Dessine la tension, entre deux noeuds, sur oscilloscope.
```
