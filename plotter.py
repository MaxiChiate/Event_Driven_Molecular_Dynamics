import csv
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

def read_csv(csv_path):
    timesteps = []
    with open(csv_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        current_timestep = []
        for row in reader:
            if not row:
                continue
            if len(row) == 1:  # Nombre del timestep
                if current_timestep:
                    timesteps.append(current_timestep)
                current_timestep = []
            else:
                current_timestep.append([float(x) for x in row])
        if current_timestep:
            timesteps.append(current_timestep)
    return timesteps

def main():
    csv_path = "outputs/N_300_L0.090/output_N300_L0.090_t5000_0000.csv"
    timesteps = read_csv(csv_path)

    fig, ax = plt.subplots()

    # Inicializar scatter con el primer timestep
    first_particles = timesteps[0]
    x = [p[0] for p in first_particles]
    y = [p[1] for p in first_particles]
    sizes = [(p[4]*500)**2   for p in first_particles]  # radio mucho más grande
    scat = ax.scatter(x, y, s=sizes)

    # Ajustar límites según datos
    all_x = [p[0] for ts in timesteps for p in ts]
    all_y = [p[1] for ts in timesteps for p in ts]
    margin = 0.05
    ax.set_xlim(min(all_x)-margin, max(all_x)+margin)
    ax.set_ylim(min(all_y)-margin, max(all_y)+margin)
    ax.set_aspect('equal')

    # Función de actualización
    def update(frame):
        particles = timesteps[frame]
        x = [p[0] for p in particles]
        y = [p[1] for p in particles]
        sizes = [(p[4]*500)**2 for p in particles]  # mismo factor grande
        scat.set_offsets(list(zip(x, y)))
        scat.set_sizes(sizes)
        return scat,

    ani = FuncAnimation(fig, update, frames=len(timesteps), interval=50, blit=True)
    plt.show()



if __name__ == "__main__":
    main()
