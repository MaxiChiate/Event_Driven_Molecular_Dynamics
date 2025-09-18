#!/usr/bin/env python3
import os
import numpy as np
import matplotlib.pyplot as plt

# ====== CONFIG ======
INPUT_PATH = "./Simulator/outputs/N_300_L0.090/output_N300_L0.090_t100000_0000.csv"
OUT_DIR    = "images"
L          = 0.09              # box size (m) - sólo para chequeos
# MSD / ajuste
T_SS         = 50.0            # s; primer frame con t>=T_SS define el anclaje (t=0 relativo)
FIT_MIN_TAU  = 0.15            # s; ventana inferior para el ajuste
FIT_MAX_TAU  = 0.60            # s; ventana superior para el ajuste
DIM          = 2               # 2D => MSD ≈ 2*DIM*D*t
# Muestreo “primer valor luego de…”
START_AT_ABS = 40.0            # s; empezar a pedir el primer punto >= 20 s absolutos
STEP_SEC     = 5.0             # s; luego 25, 30, 35, ...
USE_SAMPLED_FOR_FIT = True     # True: ajustar sólo con los puntos muestreados; False: con todos
# =====================

# -------- parsing --------
def parse_frames(path):
    """
    Devuelve frames (t_abs, x[N], y[N]) para archivos por bloques:
      <time>
      x,y,vx,vy,r   (N líneas)
      <time>
      x,y,vx,vy,r   ...
    """
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
            # tratar de parsear el tiempo
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
                    # próxima cabecera (u otra cosa)
                    carry = pl
                    break

            if xs:
                yield t, np.asarray(xs, float), np.asarray(ys, float)

# -------- MSD anclada en t_ss --------
def msd_anchored_from_blocks(path, t_ss):
    """
    Ancla en el primer frame con t_abs>=t_ss (eso define t_rel=0) y computa:
      MSD(t_k) = (1/N) sum_i |r_i(t_k) - r_i(0)|^2
    Retorna: t_rel[...], msd[...], t_anchor_abs
    """
    t0 = None
    x0 = y0 = None
    N0 = None
    times_rel, msd = [], []

    for t_abs, x, y in parse_frames(path):
        if t0 is None:
            if t_abs < t_ss:
                continue
            # anclaje
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

# -------- muestreo: primero >= umbral --------
def sample_first_after(t_abs, y, start_abs, step_sec):
    """
    Dado t_abs (ordenado) y y(t), devuelve los primeros valores con t >=
    start_abs, start_abs+step_sec, start_abs+2*step_sec, ...
    Retorna: t_abs_s, y_s, thresholds_usados
    """
    if len(t_abs) == 0:
        return np.array([]), np.array([]), np.array([])
    thr = np.arange(start_abs, t_abs[-1] + 1e-12, step_sec, dtype=float)
    idx = np.searchsorted(t_abs, thr, side="left")
    mask = idx < len(t_abs)
    idx = idx[mask]
    # evitar duplicados si varios thresholds caen en el mismo frame
    idx = np.unique(idx)
    return t_abs[idx], y[idx], thr[mask][:len(idx)]

# -------- ajuste lineal (Teórica 0) --------
def ols_generico(x, y):
    """
    Ajusta y = a + b x.
    Retorna a, b, sigma2, var_a, var_b.
    """
    n = len(x)
    S   = n
    Sx  = float(np.sum(x))
    Sy  = float(np.sum(y))
    Sxx = float(np.sum(x*x))
    Sxy = float(np.sum(x*y))
    Delta = S*Sxx - Sx*Sx
    b = (S*Sxy - Sx*Sy) / Delta
    a = (Sxx*Sy - Sx*Sxy) / Delta
    r = y - (a + b*x)
    sigma2 = np.sum(r*r) / max(n-2, 1)
    var_b = sigma2 * (S / Delta)
    var_a = sigma2 * (Sxx / Delta)
    return a, b, sigma2, var_a, var_b

# -------- gráfico --------
def plot_msd_with_fit(t_rel_all, msd_all, fit_mask, a, b, D, D_err,
                      t_rel_sample=None, msd_sample=None,
                      out_dir=OUT_DIR, fname="msd_fit.png"):
    """
    Plotea MSD(t) (todos los puntos), los puntos muestreados (si hay)
    y la recta ajustada en la región de fit.
    """
    os.makedirs(out_dir, exist_ok=True)
    plt.figure(figsize=(7,5))

    # todos los puntos (suave)
    plt.plot(t_rel_all, msd_all, '.', ms=2, alpha=0.5, label='MSD (todos)')

    # muestreados
    if t_rel_sample is not None and len(t_rel_sample):
        plt.plot(t_rel_sample, msd_sample, 'o', ms=4, label='Muestreados (primer ≥ umbral)')

    # recta de ajuste
    if fit_mask.any():
        xx = np.linspace(t_rel_all[fit_mask].min(), t_rel_all[fit_mask].max(), 200)
        plt.plot(xx, a + b*xx, '-', label='Ajuste lineal')

    plt.xlabel('t [s] desde t_ss')
    plt.ylabel('MSD [m²]')
    plt.title(f'D = {D:.3e} ± {D_err:.1e} m²/s')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    out_path = os.path.join(out_dir, fname)
    plt.savefig(out_path, dpi=160, bbox_inches="tight")
    plt.close()
    print(f"Saved figure to {out_path}")

# -------- main --------
def main():
    # 1) MSD anclada
    t_rel, msd, t_anchor_abs = msd_anchored_from_blocks(INPUT_PATH, T_SS)
    if t_anchor_abs is None or len(t_rel) < 3:
        raise SystemExit("No hay suficientes frames tras T_SS para calcular la MSD.")

    # 2) construir tiempos absolutos de cada punto MSD
    t_abs = t_anchor_abs + t_rel

    # 3) muestrear “primer >= umbral” empezando en START_AT_ABS y saltando STEP_SEC
    t_abs_s, msd_s, thr_used = sample_first_after(t_abs, msd, START_AT_ABS, STEP_SEC)
    # convertir muestreados a tiempo relativo (para el ajuste MSD ≈ 4 D t_rel)
    t_rel_s = t_abs_s - t_anchor_abs

    # 4) elegir datos para el ajuste
    if USE_SAMPLED_FOR_FIT and len(t_rel_s) >= 3:
        # usar sólo muestreados
        fit_mask = (t_rel_s >= FIT_MIN_TAU) & (t_rel_s <= FIT_MAX_TAU)
        x_fit = t_rel_s[fit_mask]; y_fit = msd_s[fit_mask]
        # para graficar máscara sobre el conjunto completo, la replico sobre t_rel_all
        # (sólo estética; no crítico)
        mask_all = np.isin(t_rel, t_rel_s[fit_mask])
    else:
        # usar todos los puntos
        fit_mask = (t_rel >= FIT_MIN_TAU) & (t_rel <= FIT_MAX_TAU)
        x_fit = t_rel[fit_mask]; y_fit = msd[fit_mask]
        mask_all = fit_mask

    if len(x_fit) < 3:
        # fallback: primeros 10 válidos
        x_fit = (t_rel_s if USE_SAMPLED_FOR_FIT and len(t_rel_s) else t_rel)[:10]
        y_fit = (msd_s   if USE_SAMPLED_FOR_FIT and len(msd_s)   else msd)[:10]
        mask_all = (t_rel >= x_fit.min()) & (t_rel <= x_fit.max())
        print("Warning: ventana de ajuste muy chica; usando primeros puntos como fallback.")

    # 5) ajuste lineal genérico y D
    a, b, sigma2, var_a, var_b = ols_generico(x_fit, y_fit)
    D = b / (2 * DIM)
    D_err = np.sqrt(var_b) / (2 * DIM)

    # 6) chequeo de confinamiento (opcional)
    if np.sqrt(np.mean(y_fit)) > 0.2 * L:
        print("Note: sqrt(MSD) en ventana de ajuste es grande respecto a L; puede haber sesgo por confinamiento.")

    # 7) plot
    plot_msd_with_fit(t_rel, msd, mask_all, a, b, D, D_err,
                      t_rel_sample=t_rel_s, msd_sample=msd_s,
                      out_dir=OUT_DIR, fname="msd_fit_sampled.png")

    # 8) resumen
    print(f"Ancla absoluto (t_ss): t0 = {t_anchor_abs:.3f} s")
    if len(t_rel_s):
        print(f"Muestreados desde t_abs ≥ {START_AT_ABS}s cada {STEP_SEC}s: {len(t_rel_s)} puntos")
    print(f"D = {D:.6e} ± {D_err:.2e} m^2/s")
    print(f"Ventana de ajuste usada: t ∈ [{x_fit.min():.3g}, {x_fit.max():.3g}] s (tiempo relativo)")

if __name__ == "__main__":
    main()
