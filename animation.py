import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np

def animate_simple_qs(simulation, save=False, fps=10):
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


def animate_waterfall(simulation, save=False, fps=10):

    # Extraction des données nécessaires

    test_tops = simulation.q_test.tops
    test_queue_size = simulation.q_test_size
    test_srv_nb = simulation.nb_servers_test

    front_tops = simulation.q_front.tops
    front_queue_size = simulation.q_front_size
    front_srv_nb = simulation.nb_servers_front

    time_step = 0.1  # Intervalle de temps pour l'animation

    # Génération des timelines pour les courbes
    timeline = simulation.timeline()
    total_time = max(test_tops['t_depart_sys'].max(), front_tops['t_depart_sys'].max())

    # Configuration de la figure et des axes
    rectangles = [
        (0.1, 0.85, 0.8, 0.1),  # Grand rectangle en haut
        (0.1, 0.7, 0.35, 0.1),  # Rectangle en haut à gauche
        (0.55, 0.7, 0.35, 0.1), # Rectangle en haut à droite
        (0.1, 0.55, 0.35, 0.1), # Rectangle du milieu gauche
        (0.55, 0.55, 0.35, 0.1),# Rectangle du milieu droit
        (0.1, 0.4, 0.35, 0.1), # Rectangle du bas gauche
        (0.55, 0.4, 0.35, 0.1),# Rectangle du bas droit
        (0.1, 0.25, 0.8, 0.1), # Rectangle inférieur 1
        (0.1, 0.15, 0.8, 0.1), # Rectangle inférieur 2
        (0.1, 0.05, 0.8, 0.1)  # Rectangle inférieur 3
    ]

    # Création de la figure
    fig = plt.figure(figsize=(8, 12))

    # Animation principale (file d'attente et serveurs)
    ax_anim = fig.add_axes(rectangles[0])
    ax_anim.set_xlim(-0.5, front_queue_size + test_queue_size + 4)
    max_srv_nb = max(test_srv_nb, front_srv_nb)
    ax_anim.set_ylim(-max_srv_nb / 2, max_srv_nb / 2)
    ax_anim.set_title("Animation of the Queue System")
    ax_anim.axis('off')
    ax_anim.set_aspect('equal', adjustable='box')

    test_queue_background = plt.Rectangle((0, -0.4), test_queue_size, 0.8, color='gray', visible=True, fill=False)
    test_queue_background_left = plt.Rectangle((-0.05, -0.4), 0.1, 0.8, color='white', visible=True)
    test_queue_background_right = plt.Rectangle((test_queue_size - 0.05, -0.4), 0.1, 0.8, color='white', visible=True)
    ax_anim.add_patch(test_queue_background)
    ax_anim.add_patch(test_queue_background_left)
    ax_anim.add_patch(test_queue_background_right)

    front_queue_background = plt.Rectangle((test_queue_size + 2, -0.4), front_queue_size, 0.8, color='gray', visible=True, fill=False)
    #front_queue_background_left = plt.Rectangle((0.45, 0.55), 0.1, 0.8, color='white', visible=True)
    #front_queue_background_right = plt.Rectangle((front_queue_size, -0.4), 0.1, 0.8, color='white', visible=True)
    ax_anim.add_patch(front_queue_background)
    #ax_anim.add_patch(front_queue_background_left)
    #ax_anim.add_patch(front_queue_background_right)

    # Test queue
    test_queue_circles = [plt.Circle((test_queue_size - i - 0.5, 0), 0.2, color='gray', visible=True, fill=False) for i in range(test_queue_size)]
    for circle in test_queue_circles:
        ax_anim.add_patch(circle)

    # Test Serveurs
    test_server_positions = [(test_queue_size + 1, test_srv_nb / 2 - i - 0.5) for i in range(test_srv_nb)]
    test_server_circles = [plt.Circle(pos, 0.3, color='red', visible=True, fill=False) for pos in test_server_positions]
    for circle in test_server_circles:
        ax_anim.add_patch(circle)

    # Front queue
    front_queue_circles = [plt.Circle((test_queue_size + 2 + i + 0.5, 0), 0.2, color='gray', visible=True, fill=False) for i in range(front_queue_size)]
    for circle in front_queue_circles:
        ax_anim.add_patch(circle)

    # Front Serveurs
    front_server_positions = [(test_queue_size + 2 + front_queue_size + 1, front_srv_nb / 2 - i - 0.5) for i in range(front_srv_nb)]
    front_server_circles = [plt.Circle(pos, 0.3, color='red', visible=True, fill=False) for pos in front_server_positions]
    for circle in front_server_circles:
        ax_anim.add_patch(circle)

    # Courbes dans les sous-graphes
    counts = ['ag_in_sys', 'ag_in_queue', 'ag_in_service', 'ag_in_sys', 'ag_in_queue', 'ag_in_service']
    labels = ['System', 'Queue', 'Service']
    colors = ['gray', 'green', 'red']

    lines = []
    for i in range(6):
        line = i // 2
        side = i % 2 
        ax = fig.add_axes(rectangles[i + 1])

        ax.set_xlim(0, total_time)
        if side == 0:
            ax.set_ylim(0, timeline['Test Process']['ag_in_sys'].max() + 1)
        else:
            ax.set_ylim(0, timeline['Front Process']['ag_in_sys'].max() + 1)
            
        ax.set_title(f"Agents in {labels[line]}")
        line, = ax.plot([], [], drawstyle='steps-mid', color=colors[line], lw=2)
        lines.append(line)

    last_lines = []
    for i in range(3):
        ax = fig.add_axes(rectangles[i + 7])
        ax.set_xlim(0, total_time)
        ax.set_ylim(0, timeline["Sum Process"]['ag_in_sys'].max() + 1)
        ax.set_title(f"Agents in {labels[i]}")
        line, = ax.plot([], [], drawstyle='steps-mid', color=colors[i], lw=2)
        last_lines.append(line)

    # Fonction de mise à jour
    def update(frame):
        current_time = frame * time_step

        # Mise à jour de l'animation principale
        active_agents = test_tops[(test_tops['t_arval_queue'] <= current_time) & (test_tops['t_depart_sys'] > current_time)]
        in_queue = active_agents[active_agents['t_arval_srv'] > current_time]
        for i, circle in enumerate(test_queue_circles):
            if i < len(in_queue):
                circle.set_color('green')
                circle.fill = True
            else:
                circle.set_color('gray')
                circle.fill = False

        in_service = active_agents[active_agents['t_arval_srv'] <= current_time]
        for i, circle in enumerate(test_server_circles):
            if i < len(in_service):
                circle.fill = True
            else:
                circle.fill = False

        active_agents = front_tops[(front_tops['t_arval_queue'] <= current_time) & (front_tops['t_depart_sys'] > current_time)]
        in_queue = active_agents[active_agents['t_arval_srv'] > current_time]
        for i, circle in enumerate(front_queue_circles):
            if i < len(in_queue):
                circle.set_color('green')
                circle.fill = True
            else:
                circle.set_color('gray')
                circle.fill = False

        in_service = active_agents[active_agents['t_arval_srv'] <= current_time]
        for i, circle in enumerate(front_server_circles):
            if i < len(in_service):
                circle.fill = True
            else:
                circle.fill = False

        # Mise à jour des courbes
        for i, count in enumerate(counts):
            line = i % 3
            side = i // 3
            if side == 0:
                time_values = timeline['Test Process'].index[timeline['Test Process'].index <= current_time]
                y_values = timeline['Test Process'].loc[timeline['Test Process'].index <= current_time, count]
                lines[line * 2 + side].set_data(time_values, y_values)
            else:
                time_values = timeline['Front Process'].index[timeline['Front Process'].index <= current_time]
                y_values = timeline['Front Process'].loc[timeline['Front Process'].index <= current_time, count]
                lines[line * 2 + side].set_data(time_values, y_values)

        for i, count in enumerate(['ag_in_sys', 'ag_in_queue', 'ag_in_service']):
            time_values = timeline['Sum Process'].index[timeline['Sum Process'].index <= current_time]
            y_values = timeline['Sum Process'].loc[timeline['Sum Process'].index <= current_time, count]
            last_lines[i].set_data(time_values, y_values)

        

    # Création de l'animation
    frames = int(total_time / time_step) + 1
    anim = FuncAnimation(fig, update, frames=frames, interval=100)

    # Affichage de l'animation
    plt.tight_layout()
    plt.show()

    if save:
        anim.save('animation_waterfall.gif', writer='imagemagick', fps=fps)
