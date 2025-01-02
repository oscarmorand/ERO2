import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np

def animate(simulation, save=False, fps=10):
    # Extraction des données nécessaires
    tops = simulation.tops
    queue_size = simulation.queue_z
    srv_nb = simulation.srv_z
    time_step = 0.1  # Intervalle de temps pour l'animation

    # Génération des timelines pour les courbes
    mm1_bench, _ = simulation.timeline()
    total_time = tops['t_depart_sys'].max()

    # Configuration de la figure et des axes
    fig, axes = plt.subplots(4, 1, figsize=(12, 16), gridspec_kw={'height_ratios': [2, 1, 1, 1]})

    # Animation principale (file d'attente et serveurs)
    ax_anim = axes[0]
    ax_anim.set_xlim(-0.5, queue_size + 2)
    ax_anim.set_ylim(-srv_nb / 2, srv_nb / 2)
    ax_anim.set_title("Animation of the Queue System")
    ax_anim.axis('off')
    ax_anim.set_aspect('equal', adjustable='box')

    # File d'attente
    queue_background = plt.Rectangle((0, -0.4), queue_size, 0.8, color='gray', visible=True, fill=False)
    queue_background_left = plt.Rectangle((-0.05, -0.4), 0.1, 0.8, color='white', visible=True)
    queue_background_right = plt.Rectangle((queue_size - 0.05, -0.4), 0.1, 0.8, color='white', visible=True)
    ax_anim.add_patch(queue_background)
    ax_anim.add_patch(queue_background_left)
    ax_anim.add_patch(queue_background_right)

    queue_circles = [plt.Circle((queue_size - i - 0.5, 0), 0.2, color='gray', visible=True, fill=False) for i in range(queue_size)]
    for circle in queue_circles:
        ax_anim.add_patch(circle)

    # Serveurs
    server_positions = [(queue_size + 1, srv_nb / 2 - i - 0.5) for i in range(srv_nb)]
    server_circles = [plt.Circle(pos, 0.3, color='red', visible=True, fill=False) for pos in server_positions]
    for circle in server_circles:
        ax_anim.add_patch(circle)

    # Courbes dans les sous-graphes
    counts = ['ag_in_sys', 'ag_in_queue', 'ag_in_service']
    labels = ['System', 'Queue', 'Service']
    colors = ['gray', 'green', 'red']

    lines = []
    for i in range(3):
        axes[i + 1].set_xlim(0, total_time)
        axes[i + 1].set_ylim(0, mm1_bench['ag_in_sys'].max() + 1)
        axes[i + 1].set_title(f"Agents in {labels[i]}")
        axes[i + 1].set_ylabel("Count")
        axes[i + 1].set_xlabel("Time")
        line, = axes[i + 1].plot([], [], drawstyle='steps-mid', color=colors[i], lw=2)
        lines.append(line)

    # Fonction de mise à jour
    def update(frame):
        current_time = frame * time_step

        # Mise à jour de l'animation principale
        active_agents = tops[(tops['t_arval_queue'] <= current_time) & (tops['t_depart_sys'] > current_time)]
        in_queue = active_agents[active_agents['t_arval_srv'] > current_time]
        for i, circle in enumerate(queue_circles):
            if i < len(in_queue):
                circle.set_color('green')
                circle.fill = True
            else:
                circle.set_color('gray')
                circle.fill = False

        in_service = active_agents[active_agents['t_arval_srv'] <= current_time]
        for i, circle in enumerate(server_circles):
            if i < len(in_service):
                circle.fill = True
            else:
                circle.fill = False

        # Mise à jour des courbes
        for i, count in enumerate(counts):
            time_values = mm1_bench.index[mm1_bench.index <= current_time]
            y_values = mm1_bench.loc[mm1_bench.index <= current_time, count]
            lines[i].set_data(time_values, y_values)

    # Création de l'animation
    frames = int(total_time / time_step) + 1
    anim = FuncAnimation(fig, update, frames=frames, interval=100)

    # Affichage de l'animation
    plt.tight_layout()
    plt.show()

    if save:
        anim.save('animation_with_curves.gif', writer='imagemagick', fps=fps)
