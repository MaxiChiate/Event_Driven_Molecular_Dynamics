#!/usr/bin/env python3
import os
import numpy as np
import matplotlib.pyplot as plt

# ====== CONFIG ======
INPUT_PATH = "./outputs/N_300_L0.090/output_N300_L0.090_t500_0000.csv"
OUT_DIR    = "images"
L          = 0.09               # box size (m)
T_SS       = 0.0                # primer frame con t>=T_SS define t=0 relativo
FIT_MIN_TAU = 0.0              # s; ventana inferior para ajuste
FIT_MAX_TAU = 200.0              # s; ventana superior para ajuste
DIM        = 2                  # 2D => MSD ≈ 2*DIM*D*t
# =====================

# -------- parsing --------
def parse_frames(path):
    with open(path, "r", encoding="utf-8") as f:
        carry = None
        while True:
            line = carry if carry is not None else f.readline()
            carry = None
            if not line:
                break
            ln = line.strip()
            if not ln:
                continue

            parts = [p.strip() for p in ln.split(",")]
            try:
                t = float(parts[0])
            except ValueError:
                continue  # no es cabecera de tiempo

            xs, ys = [], []
            while True:
                pos_line = f.readline()
                if not pos_line:
                    break
                pl = pos_line.strip()
                if not pl:
                    continue
                ps = [p.strip() for p in pl.split(",")]
                if len(ps) == 5:
                    try:
                        xs.append(float(ps[0]))
                        ys.append(float(ps[1]))
                    except ValueError:
                        pass
                else:
                    carry = pl
                    break

            if xs:
                yield t, np.asarray(xs, float), np.asarray(ys, float)

# -------- MSD anclada en t_ss --------
def msd_anchored_from_blocks(path, t_ss):
    t0 = None
    x0 = y0 = None
    N0 = None
    times_rel, msd = [], []

    for t_abs, x, y in parse_frames(path):
        if t0 is None:
            if t_abs < t_ss:
                continue
            t0 = t_abs
            x0, y0 = x.copy(), y.copy()
            N0 = min(len(x0), len(y0))
            continue

        N = min(N0, len(x), len(y))
        if N == 0:
            continue

        d2 = (x[:N] - x0[:N])**2 + (y[:N] - y0[:N])**2
        times_rel.append(t_abs - t0)
        msd.append(d2.mean())

    return np.asarray(times_rel, float), np.asarray(msd, float), float(t0) if t0 is not None else None

# -------- ajuste lineal (OLS) --------
def ols_generico(x, y):
    n = len(x)
    S = n
    Sx = x.sum()
    Sy = y.sum()
    Sxx = (x*x).sum()
    Sxy = (x*y).sum()
    Delta = S*Sxx - Sx*Sx
    b = (S*Sxy - Sx*Sy)/Delta
    a = (Sxx*Sy - Sx*Sxy)/Delta
    r = y - (a + b*x)
    sigma2 = (r*r).sum()/max(n-2,1)
    var_b = sigma2*(S/Delta)
    var_a = sigma2*(Sxx/Delta)
    return a, b, sigma2, var_a, var_b

# -------- gráfico --------
def plot_msd_with_fit(t_rel, msd, x_fit, a, b, D, D_err, out_dir=OUT_DIR, fname="msd_fit.png"):
    os.makedirs(out_dir, exist_ok=True)
    plt.figure(figsize=(7,5))
    plt.plot(t_rel, msd, '.', ms=2, alpha=0.5, label='MSD (todos)')

    if len(x_fit):
        # expandimos un poco los límites para visualizar mejor
        xx = np.linspace(x_fit.min(), x_fit.max(), 200)
        yy = a + b*xx
        plt.plot(xx, yy, 'r-', lw=2, label='Ajuste lineal')


    plt.xlabel('t [s] desde t_ss')
    plt.ylabel('MSD [m²]')
    plt.title(f'D = {D:.3e} ± {D_err:.1e} m²/s')
    plt.grid(True)
    plt.legend()
    out_path = os.path.join(out_dir, fname)
    plt.savefig(out_path, dpi=160, bbox_inches="tight")
    plt.close()
    print(f"Saved figure to {out_path}")

# -------- main --------
def main():
    t_rel, msd, t_anchor_abs = msd_anchored_from_blocks(INPUT_PATH, T_SS)
    if t_anchor_abs is None or len(t_rel) < 3:
        raise SystemExit("No hay suficientes frames tras T_SS para calcular la MSD.")

    # máscara de ajuste
    fit_mask = (t_rel >= FIT_MIN_TAU) & (t_rel <= FIT_MAX_TAU)
    x_fit = t_rel[fit_mask]
    y_fit = msd[fit_mask]

    if len(x_fit) < 3:
        x_fit = t_rel[:10]
        y_fit = msd[:10]
        fit_mask = (t_rel >= x_fit.min()) & (t_rel <= x_fit.max())
        print("Warning: pocos puntos en ventana de ajuste; usando primeros 10.")

    a, b, sigma2, var_a, var_b = ols_generico(x_fit, y_fit)
    D = b / (2 * DIM)
    D_err = np.sqrt(var_b) / (2 * DIM)

    # chequeo de confinamiento opcional
    if np.sqrt(np.mean(y_fit)) > 0.2*L:
        print("Note: sqrt(MSD) grande respecto a L; posible sesgo por confinamiento.")

    # plot
    plot_msd_with_fit(t_rel, msd, x_fit, a, b, D, D_err)

    # resumen
    print(f"Ancla absoluto t0 = {t_anchor_abs:.3f} s")
    print(f"D = {D:.6e} ± {D_err:.2e} m²/s")
    print(f"Ventana de ajuste: t ∈ [{x_fit.min():.3g}, {x_fit.max():.3g}] s")

if __name__ == "__main__":
    main()
