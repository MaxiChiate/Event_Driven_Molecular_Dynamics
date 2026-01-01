import os

import matplotlib.pyplot as plt
import numpy as np

# ====== CONFIG ======
INPUT_PATH = "../Simulator/src/outputs/N_300_L0.090/output_N300_L0.090_t20_0000.csv"
OUT_DIR = "images"
L = 0.09  # box size (m)
T_SS = 0.0  # primer frame con t>=T_SS define t=0 relativo
FIT_MIN_TAU = 5.0  # s; ventana inferior para ajuste
FIT_MAX_TAU = 15.0  # s; ventana superior para ajuste
DIM = 2  # 2D => MSD ≈ 2*DIM*D*t
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

        d2 = (x[:N] - x0[:N]) ** 2 + (y[:N] - y0[:N]) ** 2
        times_rel.append(t_abs - t0)
        msd.append(d2.mean())

    return (
        np.asarray(times_rel, float),
        np.asarray(msd, float),
        float(t0) if t0 is not None else None,
    )


# -------- ajuste lineal (OLS) --------
def ols_generico(x, y):
    n = len(x)
    S = n
    Sx = x.sum()
    Sy = y.sum()
    Sxx = (x * x).sum()
    Sxy = (x * y).sum()
    Delta = S * Sxx - Sx * Sx
    b = (S * Sxy - Sx * Sy) / Delta
    a = (Sxx * Sy - Sx * Sxy) / Delta
    r = y - (a + b * x)
    sigma2 = (r * r).sum() / max(n - 2, 1)
    var_b = sigma2 * (S / Delta)
    var_a = sigma2 * (Sxx / Delta)
    return a, b, sigma2, var_a, var_b


# -------- gráfico --------
def plot_msd_with_fit(
    t_rel, msd, x_fit, y_fit, out_dir=OUT_DIR, fname="msd_fit.png"
):
    """
    Grafica MSD con ajuste lineal. Muestra D en notación científica.
    """
    os.makedirs(out_dir, exist_ok=True)
    plt.figure(figsize=(6, 4))
    # Datos
    plt.plot(t_rel, msd, "-", lw=1, label="Datos")

    b0, c_opt = plot_msd_error_vs_slope(x_fit, y_fit, b0=-0.0013)
    xx = np.linspace(x_fit.min(), x_fit.max(), 200)
    yy = b0 + c_opt * xx

    D = c_opt / (2 * DIM)
    mantissa, exponent = f"{D:.3e}".split("e")
    exponent = int(exponent)  # ej. -5
    label = rf"Regresión lineal: $D={mantissa}\times 10^{{{exponent}}}$"
    plt.plot(xx, yy, "r-", lw=2, label=label)

    plt.xlabel(r"tiempo (s)")
    plt.ylabel(r"MSD $(\mathrm{m^{2}})$")
    plt.grid(True)
    plt.legend()
    out_path = os.path.join(out_dir, fname)
    plt.savefig(out_path, dpi=160, bbox_inches="tight")
    plt.close()
    print(f"Saved figure to {out_path}")


def plot_msd_error_vs_slope(
    t_rel, msd, b0=2.5, out_dir=OUT_DIR, fname="msd_regression_error.png"
):
    """
    Plot quadratic error E(c) = sum((y_i - (c*x_i + b0))^2)
    as a function of slope c, with fixed intercept b0.
    """
    # sweep slope values around a reasonable range
    c_center = (msd[-1] - b0) / (t_rel[-1] - t_rel[0])  # rough estimate
    c_values = np.linspace(
        c_center - abs(c_center) * 2, c_center + abs(c_center) * 2, 400
    )

    errors = []
    for c in c_values:
        y_pred = c * t_rel + b0
        error = np.sum((msd - y_pred) ** 2)
        errors.append(error)

    errors = np.array(errors)
    # find minimum
    min_idx = np.argmin(errors)
    c_opt = c_values[min_idx]
    E_opt = errors[min_idx]

    # plot
    plt.figure(figsize=(6, 4))
    plt.plot(c_values, errors, "b-", lw=1)
    plt.axvline(c_opt, color="r", linestyle="--", label=rf"$c_{{opt}} = {c_opt:.3e}$")
    plt.axhline(E_opt, color="g", linestyle="--", label=rf"$E_{{min}} = {E_opt:.3e}$")

    plt.xlabel(r"Pendiente $c$ (MSD/s)")
    plt.ylabel(r"$E(c) = \sum_i (MSD_i - (c t_i + b_0))^2$")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    os.makedirs(out_dir, exist_ok=True)
    save_path = os.path.join(out_dir, fname)
    plt.savefig(save_path, dpi=300)
    plt.close()
    print(f"Plot saved to {save_path}")
    print(f"c_opt = {c_opt:.6e}, E_min = {E_opt:.6e}")
    return b0, c_opt


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

    # chequeo de confinamiento opcional
    if np.sqrt(np.mean(y_fit)) > 0.2 * L:
        print("Note: sqrt(MSD) grande respecto a L; posible sesgo por confinamiento.")

    # plot
    plot_msd_with_fit(t_rel, msd, x_fit, y_fit)

    # resumen
    print(f"Ancla absoluto t0 = {t_anchor_abs:.3f} s")
    print(f"Ventana de ajuste: t ∈ [{x_fit.min():.3g}, {x_fit.max():.3g}] s")


if __name__ == "__main__":
    main()
