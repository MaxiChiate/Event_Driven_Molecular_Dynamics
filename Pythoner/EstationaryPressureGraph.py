#!/usr/bin/env python3
import os
import numpy as np
import matplotlib.pyplot as plt

# ======================= CONFIG =======================
# Cada corrida: path al CSV de eventos y el L de esa geometría (m)
RUNS = [
    # ejemplo (editá con tus paths reales):
    {"path": "../Simulator/src/outputs/N_300_L0.090/output_N300_L0.090_t100_0000_collisions.csv", "L": 0.09},
    # {"path": ".../output_L0.050.csv", "L": 0.05},
    # {"path": ".../output_L0.070.csv", "L": 0.07},
    # {"path": ".../output_L0.090.csv", "L": 0.09},
]

# Bin de tiempo para acumular impulsos
DELTA_T   = 2.0     # s  (igual que tu otro script, ajustable)
MASS      = 1.0     # kg
RADIUS    = 0.0015  # m  (radio de las partículas)
T_STEADY  = 80.0    # s  (umbral de estado estacionario, editable)
OUT_DIR   = "images"

# Paredes activas en tu CSV actual (0..3). Longitudes (m) de cada pared del recinto grande 0.09x0.09
# Mapeo sugerido: 0=TOP, 1=BOTTOM, 2=LEFT, 3=WRITE (todas 0.09 m)
L_WALLS = [0.09, 0.09, 0.09, 0.09-L, 0.09, 0.09, L]
# ======================================================

def parse_blocks(path: str):
    """
    Bloques:
      cabecera: t,(wall?),(v_normal?)  -> 1, 2 o 3 campos
      luego N filas x,y,vx,vy,r
    Devuelve lista: [{'t': float, 'wall': int|-1, 'vnorm': float|None}, ...]
    """
    recs = []
    with open(path, "r", encoding="utf-8") as f:
        lines = [ln.strip() for ln in f if ln.strip()]
    i, n = 0, len(lines)
    while i < n:
        head = [s.strip() for s in lines[i].split(",")]
        t = float(head[0]); wall = -1; vnorm = None
        if len(head) >= 2 and head[1] != "": wall = int(head[1])
        if len(head) >= 3 and head[2] != "": vnorm = float(head[2])
        i += 1
        # saltar N líneas de partículas (5 columnas)
        while i < n:
            parts = lines[i].split(",")
            if len(parts) != 5: break
            i += 1
        recs.append({"t": t, "wall": wall, "vnorm": vnorm})
    return recs

def pressures_per_bin(recs, delta_t, L_walls, mass=1.0):
    """
    Por cada bin [t_k, t_k+Δt):
      P_j = (Σ 2 m |v_c|)/(Δt L_j)  (sumando choques con esa pared en el bin).
    Retorna: times (centros de bin), Ptot (N_bins,)
    """
    if not recs: return [], np.zeros((0,))
    t0 = recs[0]["t"]; cur_start = t0
    imp = np.zeros(4, float)   # impulso acumulado por pared en el bin actual
    times, Ptot = [], []

    for k in range(1, len(recs)+1):
        r = recs[k-1]
        if 0 <= r["wall"] <= 3 and r["vnorm"] is not None:
            imp[r["wall"]] += 2.0 * mass * abs(r["vnorm"])
        # cerrar bins hasta el próximo tiempo (sin forzar bins extra al final)
        t_next = recs[k]["t"] if k < len(recs) else recs[-1]["t"]
        while t_next >= cur_start + delta_t:
            tbin = cur_start + 0.5*delta_t
            # presión total = suma_j (imp_j / (Δt * L_j))
            P_bin = 0.0
            for j in range(len(L_walls)):
                L = max(L_walls[j], 1e-30)
                P_bin += imp[j] / (delta_t * L)
            times.append(tbin)
            Ptot.append(P_bin)
            imp[:] = 0.0
            cur_start += delta_t

    return np.array(times, float), np.array(Ptot, float)

def effective_area_Lshape(L: float, R: float) -> float:
    """
    Área efectiva para el centro de partículas (erosión por R):
      - Bloque principal: 0.09 x 0.09  → (0.09-2R)^2
      - Brazo: ancho 0.09, alto L      → (0.09-2R)*max(L-2R,0)
    (Aproximación conservadora; si tu brazo tiene sólo 3 paredes activas no cambia A_eff del centro).
    """
    W_main, H_main = 0.09, 0.09
    W_arm,  H_arm  = 0.09, max(L - 2*R, 0.0)
    W_eff   = max(W_main - 2*R, 0.0)
    H_eff   = max(H_main - 2*R, 0.0)
    A_eff = W_eff*H_eff + max(W_arm - 2*R, 0.0)*H_arm
    return A_eff

def mean_pressure_after_steady(path: str, L: float, t_steady: float) -> tuple[float,float]:
    """
    Lee archivo, calcula P(t) por bin y devuelve:
      (A_eff, P_mean_en_estado_estacionario)
    """
    recs = parse_blocks(path)
    times, Ptot = pressures_per_bin(recs, DELTA_T, L_WALLS, mass=MASS)
    # filtrar desde t >= t_steady
    mask = times >= t_steady
    if not mask.any():
        raise RuntimeError(f"No hay bins con t >= {t_steady} en {path}")
    P_mean = float(Ptot[mask].mean())
    A_eff  = effective_area_Lshape(L, RADIUS)
    return A_eff, P_mean

def main():
    pairs = []  # (A_eff^-1, P_mean)
    for run in RUNS:
        A_eff, P_mean = mean_pressure_after_steady(run["path"], run["L"], T_STEADY)
        invA = 1.0 / max(A_eff, 1e-30)
        pairs.append((invA, P_mean))
        print(f"L={run['L']:.3f}  A_eff={A_eff:.6e}  1/A={invA:.6e}  <P>={P_mean:.6e}")

    pairs = np.array(pairs, float)
    x = pairs[:,0]  # 1/A_eff
    y = pairs[:,1]  # <P>

    os.makedirs(OUT_DIR, exist_ok=True)

    # Scatter y ajuste lineal opcional
    plt.figure(figsize=(6,4))
    plt.plot(x, y, marker='o', linestyle='', label='Datos (<P> desde estado estacionario)')
    if len(x) >= 2:
        a, b = np.polyfit(x, y, 1)  # y = a x + b
        xs = np.linspace(x.min(), x.max(), 200)
        plt.plot(xs, a*xs + b, label=f"Ajuste lineal: P = {a:.3e}·A⁻¹ + {b:.3e}")
    plt.xlabel(r'$A_\mathrm{efectiva}^{-1}\; (m^{-2})$')
    plt.ylabel(r'$\langle P\rangle\; (N/m)$')
    plt.grid()
    plt.legend(loc='best')
    out_png = os.path.join(OUT_DIR, "P_vs_Ainv.png")
    plt.savefig(out_png, dpi=160, bbox_inches="tight"); plt.close()
    print(f"Saved {out_png}")

if __name__ == "__main__":
    main()
