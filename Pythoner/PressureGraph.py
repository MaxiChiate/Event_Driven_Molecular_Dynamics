#!/usr/bin/env python3
import os
import numpy as np
import matplotlib.pyplot as plt

# ====== CONFIG ======
INPUT_PATH = "../Simulator/src/outputs/N_300_L0.090/output_N300_L0.090_t100_0000_collisions.csv"  # tu csv
DELTA_T    = 2                 # tamaño del bin Δt
MASS       = 1.0                 # masa de partícula
OUT_DIR    = "images"
L          = 0.09

# Longitudes de paredes (m)
# BIG enclosure: paredes con wall id 0..3
L_BIG_WALLS   = [0.09, 0.09, 0.09, 0.09-L]     # TOP, BOTTOM, LEFT, RIGHT del recinto grande
# SMALL enclosure: paredes con wall id 4..7
L_SMALL_WALLS = [0.09, 0.09, L]     # ajustá a tu brazo (o lo que corresponda)
# ====================
def parse_blocks(path):
    """
    Flat format only: one collision per line -> t,wall,vnorm
    - t: float (seconds)
    - wall: int (e.g., 0..7)
    - vnorm: float (absolute normal velocity before bounce)
    Returns: list[{'t': float, 'wall': int, 'vnorm': float}]
    """
    recs = []
    with open(path, "r", encoding="utf-8") as f:
        for ln in f:
            ln = ln.strip()
            if not ln or ln.lstrip().startswith("#"):
                continue
            parts = [p.strip() for p in ln.split(",")]
            try:
                t = float(parts[0])
                wall = int(parts[1])
                vnorm = float(parts[2])
            except ValueError:
                continue
            recs.append({"t": t, "wall": wall, "vnorm": vnorm})

    recs.sort(key=lambda r: r["t"])
    return recs

def pressures_per_bin_split(recs, delta_t, L_big, L_small, mass=1.0):
    """
    Por cada bin [t_k, t_k+Δt):
      Para BIG (wall<4):
        P_j^big = (Σ 2 m |v_c|)/(Δt L_big[j]), j=0..3
      Para SMALL (wall>=4):
        P_j^small = (Σ 2 m |v_c|)/(Δt L_small[j-4]), j=4..7
    Retorna:
      times                  (centros de bin)
      P_big_walls (N,4)      presiones por pared BIG
      P_small_walls (N,4)    presiones por pared SMALL
      P_big_total  (N,)      suma de BIG
      P_small_total (N,)     suma de SMALL
    """
    if not recs:
        z = np.zeros
        return [], z((0,4)), z((0,4)), z((0,)), z((0,))

    t0 = recs[0]["t"]; cur_start = t0
    imp_big   = np.zeros(4, float)
    imp_small = np.zeros(4, float)

    times = []
    P_big_walls_list   = []
    P_small_walls_list = []

    for k in range(1, len(recs)+1):
        r = recs[k-1]
        if r["wall"] is not None and r["wall"] >= 0 and r["vnorm"] is not None:
            dp = 2.0 * mass * abs(r["vnorm"])
            if r["wall"] < 4:
                imp_big[r["wall"]] += dp
            else:
                idx = r["wall"] - 4
                if 0 <= idx < 4:
                    imp_small[idx] += dp

        # cerrar bins hasta alcanzar el próximo tiempo (sin forzar bins vacíos al final)
        t_next = recs[k]["t"] if k < len(recs) else recs[-1]["t"]
        while t_next >= cur_start + delta_t:
            tbin = cur_start + 0.5*delta_t

            # BIG
            P_big = np.zeros(4, float)
            for j in range(4):
                L = max(L_big[j], 1e-30)
                P_big[j] = imp_big[j] / (delta_t * L)

            # SMALL
            P_small = np.zeros(4, float)
            for j in range(3):
                Ls = max(L_small[j], 1e-30)
                P_small[j] = imp_small[j] / (delta_t * Ls)

            times.append(tbin)
            P_big_walls_list.append(P_big)
            P_small_walls_list.append(P_small)

            # reset bin
            imp_big[:]   = 0.0
            imp_small[:] = 0.0
            cur_start += delta_t

    P_big_walls   = np.vstack(P_big_walls_list)   if P_big_walls_list   else np.zeros((0,4))
    P_small_walls = np.vstack(P_small_walls_list) if P_small_walls_list else np.zeros((0,4))
    P_big_total   = P_big_walls.sum(axis=1)   if P_big_walls.size   else np.zeros((0,))
    P_small_total = P_small_walls.sum(axis=1) if P_small_walls.size else np.zeros((0,))
    return times, P_big_walls, P_small_walls, P_big_total, P_small_total

# --------- gráficos ----------
def plot_totals(times, P_big, P_small, tag=""):
    os.makedirs(OUT_DIR, exist_ok=True)
    plt.figure(figsize=(10,6))
    plt.plot(times, P_big,   label="Recinto izquierdo $P_t$")
    plt.plot(times, P_small, label="Recinto derecho $P_t$")
    plt.xlabel("Tiempo (s)")
    plt.ylabel("Presión ($N/m$)")
    plt.grid(); plt.legend(loc="upper right")
    path = os.path.join(OUT_DIR, f"pressure_totals_{tag}_{L}.png")
    plt.savefig(path, dpi=160, bbox_inches="tight"); plt.close()
    print(f"Saved {path}")

def plot_walls(times, Pwalls, which="big", tag=""):
    os.makedirs(OUT_DIR, exist_ok=True)
    plt.figure(figsize=(10,6))
    labels = [r"$P_0$", r"$P_1$", r"$P_2$"]
    for j in range(3):
        plt.plot(times, Pwalls[:,j], label=labels[j])
    plt.xlabel("Tiempo (s)")
    plt.ylabel(f"Presión por pared {which.upper()} ($N/m$)")
    plt.grid(); plt.legend(loc="upper right")
    path = os.path.join(OUT_DIR, f"pressure_walls_{which}_{tag}_{L}.png")
    plt.savefig(path, dpi=160, bbox_inches="tight"); plt.close()
    print(f"Saved {path}")

# --------- main ----------
if __name__ == "__main__":
    recs = parse_blocks(INPUT_PATH)
    times, P_big_w, P_small_w, P_big, P_small = pressures_per_bin_split(
        recs, DELTA_T, L_BIG_WALLS, L_SMALL_WALLS, mass=MASS
    )

    tag = f"dt{DELTA_T}"
    # Totales por recinto
    plot_totals(times, P_big, P_small, tag)
    # (Opcional) por pared dentro de cada recinto
    if len(P_big_w):
        plot_walls(times, P_big_w, which="big", tag=tag)
    if len(P_small_w):
        plot_walls(times, P_small_w, which="small", tag=tag)
