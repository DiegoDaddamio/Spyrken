from .components import *
from .circuit import *
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.lines import Line2D
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Button, Slider
from matplotlib.ticker import ScalarFormatter, AutoMinorLocator
from concurrent.futures import ThreadPoolExecutor
from matplotlib.patches import FancyArrowPatch
from tqdm import tqdm
    

    
def voltage_phasors(self, duration=10, fps=60, theme='light'):
    """
    Version haute performance de l'animation des vecteurs tournants.
    """
    
    # Configuration du thème
    if theme == 'dark':
        plt.style.use('dark_background')
        grid_color = 'gray'
        text_color = 'white'
        bg_color = '#1e1e1e'
        button_color = '#444444'
        button_text_color = 'white'
        button_hover_color = '#666666'
    else:
        plt.style.use('default')
        grid_color = 'lightgray'
        text_color = 'black'
        bg_color = 'white'
        button_color = '#e0e0e0'
        button_text_color = 'black'
        button_hover_color = '#f0f0f0'
    
    # Créer une figure optimisée
    plt.rcParams['path.simplify'] = True
    plt.rcParams['path.simplify_threshold'] = 1.0
    
    fig = plt.figure(figsize=(10, 8), facecolor=bg_color, dpi=100)
    plt.subplots_adjust(bottom=0.25)
    ax = fig.add_subplot(111)
    
    # Collecter les tensions
    original_voltages = []
    labels = []
    colors = []
    
    component_colors = {
        Resistor: '#FF5733',
        Capacitor: '#33A1FF',
        Inductor: '#33FF57',
        VoltageSource: '#FF33A1'
    }
    
    for component in self.components:
        if hasattr(component, 'voltage') and component.voltage is not None:
            voltage = component.voltage
            if not isinstance(voltage, complex):
                voltage = complex(voltage, 0)
                
            original_voltages.append(voltage)
            labels.append(component.name)
            colors.append(component_colors.get(type(component), '#AAAAAA'))
    
    # Calculer l'échelle du graphique
    max_magnitude = max([abs(v) for v in original_voltages]) * 1.2 if original_voltages else 10
    
    # Configurer les axes
    ax.set_xlim(-max_magnitude, max_magnitude)
    ax.set_ylim(-max_magnitude, max_magnitude)
    ax.set_aspect('equal')
    
    # Dessiner les éléments statiques
    ax.axhline(y=0, color=grid_color, linestyle='-', alpha=0.5, linewidth=1.5)
    ax.axvline(x=0, color=grid_color, linestyle='-', alpha=0.5, linewidth=1.5)
    ax.grid(True, alpha=0.3, color=grid_color, linestyle='--')
    
    # Cercles de magnitude
    circle_radii = np.linspace(max_magnitude/4, max_magnitude, 4)
    for radius in circle_radii:
        circle = plt.Circle((0, 0), radius, fill=False, color=grid_color, alpha=0.3, linestyle='--')
        ax.add_artist(circle)
        ax.text(radius*0.7, radius*0.7, f"{radius:.1f}V", 
            color=text_color, alpha=0.7, fontsize=8)
    
    # Utiliser FancyArrowPatch pour des flèches qui ne tournent pas
    arrows = []
    label_texts = []
    info_texts = []
    
    for color in colors:
        # Créer une flèche élégante avec FancyArrowPatch
        arrow = FancyArrowPatch(
            (0, 0), (0, 0),
            arrowstyle='-|>',
            mutation_scale=15,  # Taille de la tête de flèche
            lw=2,
            color=color,
            zorder=3
        )
        ax.add_patch(arrow)
        arrows.append(arrow)
        
        # Textes
        label_text = ax.text(0, 0, "", fontsize=9, color=color, fontweight='bold')
        info_text = ax.text(0, 0, "", fontsize=8, color=color)
        
        label_texts.append(label_text)
        info_texts.append(info_text)
    
    # Légende
    legend_elements = [Line2D([0], [0], color=color, lw=2, label=label) 
                    for label, color in zip(labels, colors)]
    ax.legend(handles=legend_elements, loc='upper right', framealpha=0.7)
    
    # Textes d'information
    time_text = ax.text(0.02, 0.95, "t = 0.000 s", transform=ax.transAxes, 
                    fontsize=10, color=text_color,
                    bbox=dict(facecolor=bg_color, alpha=0.8, edgecolor='none'))
    
    speed_text = ax.text(0.02, 0.90, "Vitesse: 100%", transform=ax.transAxes, 
                    fontsize=10, color=text_color,
                    bbox=dict(facecolor=bg_color, alpha=0.8, edgecolor='none'))
    
    # Titre et étiquettes
    ax.set_xlabel('Partie réelle (V)', color=text_color)
    ax.set_ylabel('Partie imaginaire (V)', color=text_color)
    ax.set_title(f"Diagramme de Fresnel animé à {self.freq} Hz", 
            fontsize=14, color=text_color, fontweight='bold')
    
    # État de l'animation
    animation_running = [False]  # Commence en pause
    speed_factor = [1.0]
    elapsed_time = [0.0]
    
    # Fonction d'animation
    def animate(frame):
        # Mettre à jour le temps seulement si l'animation est en cours
        if animation_running[0]:
            delta_t = 1.0 / fps * speed_factor[0]
            elapsed_time[0] += delta_t
        t = elapsed_time[0]
        
        # Mettre à jour le texte de temps
        time_text.set_text(f"t = {t:.3f} s")
        
        # Facteur de rotation (wt)
        omega = 2 * np.pi * self.freq
        rotation = np.exp(1j * omega * t)
        
        for i, voltage in enumerate(original_voltages):
            # Rotation du vecteur
            rotated_voltage = voltage * rotation
            x, y = rotated_voltage.real, rotated_voltage.imag
            
            # Mise à jour de la flèche - FancyArrowPatch maintient l'orientation correcte
            arrows[i].set_positions((0, 0), (x, y))
            
            # Mise à jour textes
            label_texts[i].set_position((x*1.1, y*1.1))
            label_texts[i].set_text(labels[i])
            
            magnitude = abs(voltage)
            phase = np.angle(rotated_voltage)
            info_texts[i].set_text(f"{magnitude:.2f}V ∠{np.degrees(phase):.1f}°")
            
            offset = 0.05 * max_magnitude
            text_x = x + offset * np.cos(phase + np.pi/2)
            text_y = y + offset * np.sin(phase + np.pi/2)
            info_texts[i].set_position((text_x, text_y))
        
        # Note: FancyArrowPatch n'est pas inclus dans le retour car blit=False
        return label_texts + info_texts + [time_text, speed_text]
    
    # Fonction pour le bouton Play/Pause
    def toggle_animation(event):
        animation_running[0] = not animation_running[0]
        if animation_running[0]:
            play_button.label.set_text('Pause')
        else:
            play_button.label.set_text('Play')
    
    # Fonction pour le slider de vitesse
    def update_speed(val):
        speed_factor[0] = 10 ** val
        percentage = speed_factor[0] * 100
        
        if percentage >= 100:
            speed_text.set_text(f"Vitesse: {percentage:.0f}%")
        elif percentage >= 10:
            speed_text.set_text(f"Vitesse: {percentage:.1f}%")
        else:
            speed_text.set_text(f"Vitesse: {percentage:.2f}%")
    
    # Fonction pour le bouton Reset
    def reset_animation(event):
        elapsed_time[0] = 0.0
    
    # Ajouter bouton Play/Pause
    play_ax = plt.axes([0.4, 0.05, 0.1, 0.04])
    play_button = Button(play_ax, 'Play', color=button_color, hovercolor=button_hover_color)
    play_button.label.set_color(button_text_color)
    play_button.on_clicked(toggle_animation)
    
    # Ajouter bouton Reset
    reset_ax = plt.axes([0.55, 0.05, 0.1, 0.04])
    reset_button = Button(reset_ax, 'Reset', color=button_color, hovercolor=button_hover_color)
    reset_button.label.set_color(button_text_color)
    reset_button.on_clicked(reset_animation)
    
    # Ajouter slider pour la vitesse
    speed_ax = plt.axes([0.2, 0.12, 0.6, 0.03])
    speed_slider = Slider(speed_ax, 'Vitesse (log)', -8, 0.7, valinit=0, valstep=0.1)
    speed_slider.on_changed(update_speed)
    # Créer l'animation - désactive le blitting pour les FancyArrowPatch
    anim = FuncAnimation(fig, animate, interval=1000/fps, blit=False, 
                        save_count=fps*duration)
    
    plt.show()
    
def voltage_phasors2(self, duration=10, fps=60, theme='light'):
    """
    Version haute performance de l'animation des vecteurs tournants.
    """
    
    # Configuration du thème
    if theme == 'dark':
        plt.style.use('dark_background')
        grid_color = 'gray'
        text_color = 'white'
        bg_color = '#1e1e1e'
        button_color = '#444444'
        button_text_color = 'white'
        button_hover_color = '#666666'
    else:
        plt.style.use('default')
        grid_color = 'lightgray'
        text_color = 'black'
        bg_color = 'white'
        button_color = '#e0e0e0'
        button_text_color = 'black'
        button_hover_color = '#f0f0f0'
    
    # Créer une figure optimisée
    plt.rcParams['path.simplify'] = True
    plt.rcParams['path.simplify_threshold'] = 1.0
    
    fig = plt.figure(figsize=(10, 8), facecolor=bg_color, dpi=100)
    plt.subplots_adjust(bottom=0.25)
    ax = fig.add_subplot(111)
    
    # Collecter les tensions
    original_voltages = []
    labels = []
    colors = []
    
    # Utiliser les mêmes couleurs que la version originale
    component_colors = {
        Resistor: '#FF5733',
        Capacitor: '#33A1FF',
        Inductor: '#33FF57',
        VoltageSource: '#FF33A1'
    }
    
    for component in self.components:
        if hasattr(component, 'voltage') and component.voltage is not None:
            voltage = component.voltage
            if not isinstance(voltage, complex):
                voltage = complex(voltage, 0)
                
            original_voltages.append(voltage)
            labels.append(component.name)
            colors.append(component_colors.get(type(component), '#AAAAAA'))
    
    # Calculer l'échelle du graphique
    max_magnitude = max([abs(v) for v in original_voltages]) * 1.2 if original_voltages else 10
    
    # Configurer les axes
    ax.set_xlim(-max_magnitude, max_magnitude)
    ax.set_ylim(-max_magnitude, max_magnitude)
    ax.set_aspect('equal')
    
    # Dessiner les éléments statiques
    ax.axhline(y=0, color=grid_color, linestyle='-', alpha=0.5, linewidth=1.5)
    ax.axvline(x=0, color=grid_color, linestyle='-', alpha=0.5, linewidth=1.5)
    ax.grid(True, alpha=0.3, color=grid_color, linestyle='--')
    
    # Cercles de magnitude
    circle_radii = np.linspace(max_magnitude/4, max_magnitude, 4)
    for radius in circle_radii:
        circle = plt.Circle((0, 0), radius, fill=False, color=grid_color, alpha=0.3, linestyle='--')
        ax.add_artist(circle)
        ax.text(radius*0.7, radius*0.7, f"{radius:.1f}V", 
            color=text_color, alpha=0.7, fontsize=8)
    
    # Préparer les objets pour l'animation
    lines = []        # Corps des vecteurs
    arrow_heads = []  # Têtes de flèches
    label_texts = []  # Noms des composants
    info_texts = []   # Informations de magnitude/phase
    
    for i, color in enumerate(colors):
        # Ligne principale du vecteur
        line, = ax.plot([0, 0], [0, 0], color=color, lw=2, solid_capstyle='round')
        lines.append(line)
        
        # Tête de flèche
        arrow_head, = ax.plot([0], [0], marker='.', color=color, markersize=8)
        arrow_heads.append(arrow_head)
        
        # Textes
        label_text = ax.text(0, 0, labels[i], fontsize=9, color=color, fontweight='bold')
        info_text = ax.text(0, 0, "", fontsize=8, color=color)
        
        label_texts.append(label_text)
        info_texts.append(info_text)
    
    # Légende
    legend_elements = [Line2D([0], [0], color=color, lw=2, label=label) 
                    for label, color in zip(labels, colors)]
    ax.legend(handles=legend_elements, loc='upper right', framealpha=0.7)
    
    # Textes d'information
    time_text = ax.text(0.02, 0.95, "t = 0.000 s", transform=ax.transAxes, 
                    fontsize=10, color=text_color,
                    bbox=dict(facecolor=bg_color, alpha=0.8, edgecolor='none'))
    
    speed_text = ax.text(0.02, 0.90, "Vitesse: 100%", transform=ax.transAxes, 
                    fontsize=10, color=text_color,
                    bbox=dict(facecolor=bg_color, alpha=0.8, edgecolor='none'))
    
    # Titre et étiquettes
    ax.set_xlabel('Partie réelle (V)', color=text_color)
    ax.set_ylabel('Partie imaginaire (V)', color=text_color)
    ax.set_title(f"Diagramme de Fresnel animé à {self.freq} Hz", 
            fontsize=14, color=text_color, fontweight='bold')
    
    # État de l'animation
    animation_running = [False]  # Commence en pause
    speed_factor = [1.0]
    elapsed_time = [0.0]
    
    # Fonction d'animation
    def animate(frame):
        # Mettre à jour le temps seulement si l'animation est en cours
        if animation_running[0]:
            delta_t = 1.0 / fps * speed_factor[0]
            elapsed_time[0] += delta_t
        t = elapsed_time[0]
        
        # Mettre à jour le texte de temps
        time_text.set_text(f"t = {t:.3e} s")
        
        # Facteur de rotation (wt)
        omega = 2 * np.pi * self.freq
        rotation = np.exp(1j * omega * t)  # Utiliser la formule complexe exacte
        
        for i, voltage in enumerate(original_voltages):
            # Rotation du vecteur (maintenir la formule originale)
            rotated_voltage = voltage * rotation
            x, y = rotated_voltage.real, rotated_voltage.imag
            
            # Mise à jour vecteur
            lines[i].set_data([0, x], [0, y])
            arrow_heads[i].set_data([x], [y])
            
            # Mise à jour textes
            label_texts[i].set_position((x*1.1, y*1.1))
            
            # Calculer et mettre à jour les informations
            magnitude = abs(voltage)
            phase = np.angle(rotated_voltage)
            info_texts[i].set_text(f"{magnitude:.2f}V ∠{np.degrees(phase):.1f}°")
            
            offset = 0.05 * max_magnitude
            text_x = x + offset * np.cos(phase + np.pi/2)
            text_y = y + offset * np.sin(phase + np.pi/2)
            info_texts[i].set_position((text_x, text_y))
        
        # Retourner tous les objets à mettre à jour
        return lines + arrow_heads + label_texts + info_texts + [time_text, speed_text]
    
    # Fonction pour le bouton Play/Pause
    def toggle_animation(event):
        animation_running[0] = not animation_running[0]
        if animation_running[0]:
            play_button.label.set_text('Pause')
        else:
            play_button.label.set_text('Play')
    
    # Fonction pour le slider de vitesse
    def update_speed(val):
        speed_factor[0] = 10 ** val
        percentage = speed_factor[0] * 100
        
        # Format selon la magnitude
        if percentage >= 100:
            speed_text.set_text(f"Vitesse: {percentage:.0f}%")
        elif percentage >= 10:
            speed_text.set_text(f"Vitesse: {percentage:.1f}%")
        else:
            speed_text.set_text(f"Vitesse: {percentage:.2e}%")
    
    # Fonction pour le bouton Reset
    def reset_animation(event):
        elapsed_time[0] = 0.0
    
    # Ajouter bouton Play/Pause
    play_ax = plt.axes([0.4, 0.05, 0.1, 0.04])
    play_button = Button(play_ax, 'Play', color=button_color, hovercolor=button_hover_color)
    play_button.label.set_color(button_text_color)
    play_button.on_clicked(toggle_animation)
    
    # Ajouter bouton Reset
    reset_ax = plt.axes([0.55, 0.05, 0.1, 0.04])
    reset_button = Button(reset_ax, 'Reset', color=button_color, hovercolor=button_hover_color)
    reset_button.label.set_color(button_text_color)
    reset_button.on_clicked(reset_animation)
    
    # Ajouter slider pour la vitesse
    speed_ax = plt.axes([0.2, 0.12, 0.6, 0.03])
    speed_slider = Slider(speed_ax, 'Vitesse (log)', -8, 0.7, valinit=0, valstep=0.1)
    speed_slider.on_changed(update_speed)
    
    
    # Créer l'animation optimisée
    anim = FuncAnimation(fig, animate, interval=1000/fps, blit=True, 
                        cache_frame_data=False, save_count=fps*duration)
    
    plt.show()

def plot_bode(self,from_node,to_node,freq_range,show_phase=True):
    """ Génère un diagramme de Bode 
    Utilisation : Tel une sonde oscilloscope, il faut partir d'une référence (from, souvent GND) vers une comparaison (to)"""
    gains = []
    phases = []
    frequencies = freq_range

    sources = [c for c in self.components if isinstance(c, VoltageSource)]

    for freq in tqdm(frequencies) :
        self.freq = freq
        for source in sources:
            source.freq = freq
        
        self.solve()

        Vfn = from_node.voltage
        Vtn = to_node.voltage

        V = Vtn - Vfn
        v_ref = sources[0].source_voltage

        # Gain
        if abs(v_ref) < 1e-12:
            gain_db = -100
        else:
            gain = abs(V) / abs(v_ref)
            gain_db = 20 * np.log10(gain) if gain > 0 else -100
        
        # Phase

        v1 = V if isinstance(V, complex) else complex(V, 0)
        v2 = v_ref if isinstance(v_ref, complex) else complex(v_ref, 0)
        phase = np.angle(v1/v2, deg=True)

        
        
        # Stocker les résultats
        gains.append(gain_db)
        phases.append(phase)
    # Créer les graphiques
    if show_phase:
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 7), sharex=True)
        plt.subplots_adjust(hspace=0.3)
    else:
        fig, ax1 = plt.subplots(figsize=(10, 5))
    
    # Graphique du gain
    title = f"Tension entre {from_node.name} et {to_node.name}"

    ax1.semilogx(frequencies, gains, 'b-', linewidth=2)
    ax1.set_ylabel('Gain (dB)')
    ax1.set_title(title)
    ax1.grid(True, which="both", ls="--", alpha=0.3)
    
    # Graphique de la phase
    if show_phase:
        ax2.semilogx(frequencies, phases, 'r-', linewidth=2)
        ax2.set_xlabel('Fréquence (Hz)')
        ax2.set_ylabel('Phase (degrés)')
        ax2.set_ylim(min(phases)-5, max(phases)+5)
        ax2.grid(True, which="both", ls="--", alpha=0.3)
    else:
        ax1.set_xlabel('Fréquence (Hz)')
    
    plt.tight_layout()
    plt.show()
    
    return frequencies, phases, gains

def plot_bode2(self, from_node=None, to_node=None, component=None, 
            freq_range=None, num_points=200, show_phase=True):
    """
    Génère un diagramme de Bode simple pour analyser la réponse en fréquence.
    
    Paramètres :
    -----------
    from_node : Node, optional
        Nœud de départ pour la mesure de tension
    to_node : Node, optional
        Nœud d'arrivée pour la mesure de tension
    component : Component, optional
        Composant aux bornes duquel mesurer la tension
    freq_range : tuple, optional
        Plage de fréquence (f_min, f_max) en Hz
    num_points : int, optional
        Nombre de points de calcul
    show_phase : bool, optional
        Afficher la courbe de phase
    """
    
    # Déterminer les nœuds à utiliser
    if component is not None:
        # Mesure aux bornes d'un composant
        if None in component.nodes or len(component.nodes) != 2:
            print("Erreur: Composant non connecté correctement")
            return None
        from_node, to_node = component.nodes
        title = f"Tension aux bornes de {component.name}"
    elif from_node is not None and to_node is not None:
        # Mesure entre deux nœuds spécifiés
        title = f"Tension entre {from_node.name} et {to_node.name}"
    else:
        # Auto-détection de base
        sources = [c for c in self.components if isinstance(c, VoltageSource)]
        if not sources:
            print("Erreur: Aucune source trouvée")
            return None
            
        # Trouver un nœud non-GND connecté à la source
        for node in self.nodes:
            if node.name.upper() != "GND" and any(node in s.nodes for s in sources):
                from_node = node
                break
                
        # Trouver un autre nœud non-GND
        for node in self.nodes:
            if node != from_node and node.name.upper() != "GND":
                to_node = node
                break
                
        if from_node is None or to_node is None:
            print("Erreur: Impossible de déterminer les nœuds automatiquement")
            return None
            
        title = f"Tension entre {from_node.name} et {to_node.name}"
    
    # Déterminer la plage de fréquence
    if freq_range is None:
        # Estimation simple basée sur les composants
        caps = [c for c in self.components if isinstance(c, Capacitor)]
        inds = [i for i in self.components if isinstance(i, Inductor)]
        resistors = [r for r in self.components if isinstance(r, Resistor)]
        
        frequencies = []
        
        # Constantes RC
        if caps and resistors:
            for r in resistors:
                for c in caps:
                    f_rc = 1 / (2 * np.pi * r.value * c.value)
                    frequencies.append(f_rc)
        
        # Résonance LC
        if caps and inds:
            for c in caps:
                for l in inds:
                    f_res = 1 / (2 * np.pi * np.sqrt(l.value * c.value))
                    frequencies.append(f_res)
        
        if frequencies:
            f_min = min(frequencies) / 100
            f_max = max(frequencies) * 100
            print(f"Plage auto: {f_min:.2e} Hz - {f_max:.2e} Hz")
        else:
            f_min, f_max = 1, 1e6
    else:
        f_min, f_max = freq_range
    
    # Générer les fréquences
    frequencies = np.logspace(np.log10(f_min), np.log10(f_max), num_points)
    
    # Sauvegarder l'état du circuit
    original_freq = self.freq
    sources = [c for c in self.components if isinstance(c, VoltageSource)]
    original_source_freqs = {s: s.freq for s in sources}
    
    # Tableaux pour stocker les résultats
    gains = []
    phases = []
    
    # Calcul pour chaque fréquence

    for freq in tqdm(frequencies):
            
        # Configurer la fréquence
        self.freq = freq
        for source in sources:
            source.freq = freq
            
        # Résoudre le circuit
        self.solve()
        
        # Mesurer la tension
        v_from = 0 if from_node.name.upper() == "GND" else from_node.voltage
        v_to = 0 if to_node.name.upper() == "GND" else to_node.voltage
        v_diff = v_to - v_from
        
        # Référence (tension de la première source)
        v_ref = sources[0].source_voltage
        
        # Gain
        if abs(v_ref) < 1e-12:
            gain_db = -100
        else:
            gain = abs(v_diff) / abs(v_ref)
            gain_db = 20 * np.log10(gain) if gain > 0 else -100
        
        # Phase
        if abs(v_ref) < 1e-12 or abs(v_diff) < 1e-12:
            phase = 0
        else:
            v1 = v_diff if isinstance(v_diff, complex) else complex(v_diff, 0)
            v2 = v_ref if isinstance(v_ref, complex) else complex(v_ref, 0)
            phase = np.angle(v1 / v2, deg=True)
            phase = ((phase + 180) % 360) - 180
        
        # Stocker les résultats
        gains.append(gain_db)
        phases.append(phase)
    
    # Restaurer l'état original
    self.freq = original_freq
    for source, freq in original_source_freqs.items():
        source.freq = freq
    self.solve()
    
    # Créer les graphiques
    if show_phase:
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 7), sharex=True)
        plt.subplots_adjust(hspace=0.3)
    else:
        fig, ax1 = plt.subplots(figsize=(10, 5))
    
    # Graphique du gain
    ax1.semilogx(frequencies, gains, 'b-', linewidth=2)
    ax1.set_ylabel('Gain (dB)')
    ax1.set_title(title)
    ax1.grid(True, which="both", ls="--", alpha=0.3)
    
    # Graphique de la phase
    if show_phase:
        ax2.semilogx(frequencies, phases, 'r-', linewidth=2)
        ax2.set_xlabel('Fréquence (Hz)')
        ax2.set_ylabel('Phase (degrés)')
        ax2.set_ylim(min(phases)-5, max(phases)+5)
        ax2.grid(True, which="both", ls="--", alpha=0.3)
    else:
        ax1.set_xlabel('Fréquence (Hz)')
    
    plt.tight_layout()
    plt.show()
    
    return {
        'frequencies': frequencies,
        'gains': gains,
        'phases': phases
    }

def probe(self,from_node,to_node):

    sources = [c for c in self.components if isinstance(c, VoltageSource)]

    if not(self._solved) :
        self.solve()
    
    Vfn = from_node.voltage
    Vtn = to_node.voltage

    V = Vtn - Vfn
    v_ref = sources[0].source_voltage

    # On work