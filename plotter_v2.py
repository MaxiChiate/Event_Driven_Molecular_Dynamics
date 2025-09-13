import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.animation as animation

# -------------------- Lectura de archivo --------------------
def read_particle_file(filename):
    timesteps = []
    with open(filename, 'r') as f:
        lines = f.readlines()

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        # timestep
        t = float(line)
        i += 1
        particles = []
        while i < len(lines) and lines[i].strip() and ',' in lines[i]:
            px, py, vx, vy, r = map(float, lines[i].strip().split(','))
            particles.append({'x': px, 'y': py, 'vx': vx, 'vy': vy, 'r': r})
            i += 1
        timesteps.append({'t': t, 'particles': particles})
    return timesteps

# -------------------- Animación --------------------
def animate_timesteps(timesteps, map_size=0.09, interval=50):
    fig, ax = plt.subplots()
    ax.set_xlim(0, map_size)
    ax.set_ylim(0, map_size)
    ax.set_aspect('equal')

    # Círculos iniciales
    circles = [patches.Circle((0,0), 0.01, color='blue') for _ in timesteps[0]['particles']]
    for c in circles:
        ax.add_patch(c)

    def update(frame):
        ax.set_title(f"Timestep: {frame['t']:.4f}")
        for c, p in zip(circles, frame['particles']):
            c.center = (p['x'], p['y'])
            c.radius = p['r']
        return circles

    ani = animation.FuncAnimation(fig, update, frames=timesteps, interval=interval, blit=False)
    plt.show()

# -------------------- MAIN --------------------
if __name__ == "__main__":
    filename = "outputs/N_300_L0.090/output_N300_L0.090_t1000_0001.csv"
    timesteps = read_particle_file(filename)
    animate_timesteps(timesteps)
