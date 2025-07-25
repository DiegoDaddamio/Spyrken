from .components import *
from .circuit import *
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Button, Slider
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
        time_text.set_text(f"t = {t:.3e} s")
        
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

def scope(self, from_node, to_node, interactive=True):
    """
    Affiche un oscilloscope simulé de la tension entre deux nœuds avec contrôles interactifs
    """
    from matplotlib.widgets import Slider, Button, RadioButtons, TextBox
    
    sources = [c for c in self.components if isinstance(c, VoltageSource)]
    if not sources:
        print("Erreur: Aucune source de tension dans le circuit")
        return
        
    if not(self._solved):
        self.solve()
    
    # Source principale à contrôler
    main_source = sources[0]
    
    # Créer une figure avec espaces pour les contrôles
    fig, ax = plt.subplots(figsize=(12, 8))
    plt.subplots_adjust(left=0.1, bottom=0.3, right=0.9, top=0.9)
    
    # Fonctions pour calculer et mettre à jour le signal
    def calculate_signal(time_array):
        # Résoudre le circuit avec les paramètres actuels
        self.solve()
        
        # Tensions aux nœuds
        Vfn = from_node.voltage if from_node else 0
        Vtn = to_node.voltage if to_node else 0
        V = Vtn - Vfn
        
        # Pour le circuit DC
        if self.freq == 0:
            return np.ones_like(time_array) * np.real(V)
        
        # Pour le circuit AC
        omega = 2 * np.pi * self.freq
        if isinstance(V, complex):
            amplitude = abs(V)
            phase = np.angle(V)
            return amplitude * np.sin(omega * time_array + phase)
        else:
            return V * np.sin(omega * time_array)
    
    def calculate_ref_signal(time_array):
        v_ref = main_source.source_voltage
        
        # Pour le circuit DC
        if main_source.freq == 0:
            return np.ones_like(time_array) * v_ref
            
        # Pour le circuit AC
        omega = 2 * np.pi * main_source.freq
        if isinstance(v_ref, complex):
            ref_amplitude = abs(v_ref)
            ref_phase = np.angle(v_ref)
            return ref_amplitude * np.sin(omega * time_array + ref_phase)
        else:
            return v_ref * np.sin(omega * time_array)
    
    # Créer les graphiques initiaux
    t_max_init = 0.1 if main_source.freq == 0 else 3/max(main_source.freq, 1)
    t = np.linspace(0, t_max_init, 1000)
    
    signal_line, = ax.plot([], [], 'b-', linewidth=2, label=f'Tension {from_node.name}-{to_node.name}')
    ref_line, = ax.plot([], [], 'r--', linewidth=1.5, label='Référence')
    
    # Configurer les axes
    ax.set_xlabel('Temps (s)')
    ax.set_ylabel('Tension (V)')
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    # Informations de mesure
    info_text = ax.text(0.02, 0.95, '', transform=ax.transAxes, 
                       fontsize=9, va='top', ha='left',
                       bbox=dict(boxstyle='round', facecolor='white', alpha=0.7))
    
    # Ajouter les contrôles pour la source
    # 1. Amplitude de la source
    ampl_ax = plt.axes([0.1, 0.15, 0.3, 0.03])
    ampl_slider = Slider(ampl_ax, 'Amplitude (V)', 0.1, 20, 
                         valinit=main_source.source_voltage)
    
    # 2. Fréquence (pour les sources AC)
    freq_ax = plt.axes([0.1, 0.1, 0.3, 0.03])
    freq_max = main_source.freq*3 if main_source.freq > 0 else 100
    freq_init = main_source.freq if main_source.freq > 0 else 50
    freq_slider = Slider(freq_ax, 'Fréquence (Hz)', 0, freq_max, 
                         valinit=freq_init)
    
    # 3. Impédance interne
    imp_ax = plt.axes([0.6, 0.15, 0.3, 0.03])
    imp_slider = Slider(imp_ax, 'R interne (Ω)', 0, 1000, 
                        valinit=main_source.r_int)
    
    # 4. Contrôle du temps d'affichage
    time_ax = plt.axes([0.6, 0.1, 0.3, 0.03])
    time_slider = Slider(time_ax, 'Temps (s)', 10e-6, 10e-2, 
                         valinit=t_max_init)
    
    # 5. Boutons DC/AC
    mode_ax = plt.axes([0.1, 0.03, 0.08, 0.04])
    mode_button = Button(mode_ax, 'DC' if main_source.freq == 0 else 'AC')
    
    # 6. Bouton de mise à jour
    update_ax = plt.axes([0.25, 0.03, 0.1, 0.04])
    update_button = Button(update_ax, 'Recalculer')
    
    # 7. Bouton pour afficher/masquer la référence
    ref_ax = plt.axes([0.4, 0.03, 0.15, 0.04])
    ref_button = Button(ref_ax, 'Masquer réf')
    show_ref = [True]  # Utiliser une liste pour pouvoir modifier dans les fonctions
    
    # 8. Bouton de réinitialisation
    reset_ax = plt.axes([0.6, 0.03, 0.1, 0.04])
    reset_button = Button(reset_ax, 'Réinitialiser')
    
    # Fonction de mise à jour de l'affichage
    def update_display():
        # Mettre à jour le temps en fonction de la fréquence si nécessaire
        t_max = time_slider.val
        if self.freq > 0:
            # Ajuster pour montrer au moins 2 périodes
            period = 1.0 / self.freq
            if t_max < 2 * period:
                t_max = 2 * period
                time_slider.set_val(t_max)
        
        t = np.linspace(0, t_max, 1000)
        
        # Calculer les signaux
        signal = calculate_signal(t)
        ref = calculate_ref_signal(t)
        
        # Mettre à jour les lignes
        signal_line.set_data(t, signal)
        ref_line.set_data(t, ref)
        
        # Ajuster les limites des axes
        y_max = max(np.max(np.abs(signal)), np.max(np.abs(ref))) * 1.2
        ax.set_xlim(0, t_max)
        ax.set_ylim(-y_max, y_max)
        
        # Afficher/masquer la référence selon l'état
        ref_line.set_visible(show_ref[0])
        
        # Mise à jour des informations
        if self.freq > 0:
            V = to_node.voltage - from_node.voltage
            amplitude = abs(V)
            phase = np.angle(V) if isinstance(V, complex) else 0
            
            info_str = '\n'.join((
                f'Fréquence: {self.freq:.2f} Hz',
                f'Période: {1/self.freq*1000:.2f} ms',
                f'Amplitude: {amplitude:.3f} V',
                f'Phase: {np.degrees(phase):.1f}°',
                f'V RMS: {amplitude/np.sqrt(2):.3f} V'
            ))
        else:
            V = to_node.voltage - from_node.voltage
            V_real = np.real(V)
            
            info_str = f'Tension DC: {V_real:.3f} V'
        
        info_text.set_text(info_str)
        
        # Dessiner les périodes pour les signaux AC
        if self.freq > 0:
            # Supprimer les lignes verticales existantes
            for line in ax.get_lines():
                if line not in [signal_line, ref_line] and line.get_linestyle() == '--':
                    line.remove()
            
            # Ajouter des lignes pour les périodes
            period = 1.0 / self.freq
            for i in range(1, int(t_max / period) + 1):
                ax.axvline(x=i * period, color='gray', linestyle='--', alpha=0.3)
        
        # Titre du graphique
        if self.freq > 0:
            ax.set_title(f'Tension entre {from_node.name} et {to_node.name} - {self.freq:.2f} Hz')
        else:
            ax.set_title(f'Tension DC entre {from_node.name} et {to_node.name}')
        
        fig.canvas.draw_idle()
    
    # Fonctions de rappel pour les contrôles
    def update_amplitude(val):
        main_source.source_voltage = val
        if interactive:
            self.solve()
            update_display()
    
    def update_frequency(val):
        if val > 0:
            main_source.freq = val
            self.freq = val
            mode_button.label.set_text('AC')
        else:
            main_source.freq = 0
            self.freq = 0
            mode_button.label.set_text('DC')
        
        if interactive:
            self.solve()
            update_display()
    
    def update_impedance(val):
        main_source.r_int = val
        main_source.value = val
        if interactive:
            self.solve()
            update_display()
    
    def update_time(val):
        update_display()
    
    def toggle_mode(event):
        if mode_button.label.get_text() == 'DC':
            mode_button.label.set_text('AC')
            freq = freq_slider.val if freq_slider.val > 0 else 50
            freq_slider.set_val(freq)
            main_source.freq = freq
            self.freq = freq
        else:
            mode_button.label.set_text('DC')
            main_source.freq = 0
            self.freq = 0
            freq_slider.set_val(0)
        
        if interactive:
            self.solve()
            update_display()
    
    def toggle_ref(event):
        show_ref[0] = not show_ref[0]
        ref_button.label.set_text('Afficher réf' if not show_ref[0] else 'Masquer réf')
        update_display()
    
    def force_update(event):
        self.solve()
        update_display()
    
    def reset(event):
        ampl_slider.reset()
        freq_slider.reset()
        imp_slider.reset()
        time_slider.reset()
        main_source.freq = freq_init
        main_source.source_voltage = main_source.source_voltage
        main_source.r_int = main_source.r_int
        mode_button.label.set_text('DC' if freq_init == 0 else 'AC')
        show_ref[0] = True
        ref_button.label.set_text('Masquer réf')
        self.solve()
        update_display()
    
    # Connecter les fonctions de rappel
    ampl_slider.on_changed(update_amplitude)
    freq_slider.on_changed(update_frequency)
    imp_slider.on_changed(update_impedance)
    time_slider.on_changed(update_time)
    mode_button.on_clicked(toggle_mode)
    ref_button.on_clicked(toggle_ref)
    update_button.on_clicked(force_update)
    reset_button.on_clicked(reset)
    
    # Initialiser l'affichage
    self.solve()
    update_display()
    
    plt.show()
    return fig