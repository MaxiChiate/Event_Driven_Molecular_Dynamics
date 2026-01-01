import argparse
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# -----------------------------
# User configuration
# -----------------------------
r = 0.0015
S = 0.09  # system size
t_stable = 30.0  # time after which to start averaging

T = 2.0  # default bin size in seconds

files_and_L = {
    "../Simulator/src/outputs/N_300_L0.030/output_N300_L0.030_t100_0000_collisions.csv": 0.03,
    "../Simulator/src/outputs/N_300_L0.050/output_N300_L0.050_t100_0000_collisions.csv": 0.05,
    "../Simulator/src/outputs/N_300_L0.070/output_N300_L0.070_t100_0000_collisions.csv": 0.07,
    "../Simulator/src/outputs/N_300_L0.090/output_N300_L0.090_t100_0000_collisions.csv": 0.09,
}
# -----------------------------


def wall_lengths(S, L):
    return {
        0: S,
        1: S,
        2: S,
        3: S - L,
        4: S,
        5: S,
        6: L,
    }


# -----------------------------
# Pressure calculations
# -----------------------------
def compute_pressure(filename, t_stable, S, L):
    df = pd.read_csv(filename, header=None, names=["time", "wall", "vel"])
    df = df[df["time"] >= t_stable]
    if df.empty:
        return None

    total_impulse = (2 * df["vel"].abs()).sum()
    time_interval = df["time"].max() - t_stable
    if time_interval <= 0:
        return None

    total_length = sum(wall_lengths(S, L).values())
    avg_pressure = total_impulse / (time_interval * total_length)
    return avg_pressure


def sci_notation(x, sig=2):
    exp = int(np.floor(np.log10(x)))
    mant = x / 10**exp
    return f"{mant:.{sig}f}\\times10^{{{exp}}}"


def plot_regression_error_vs_c(A_inv, Ps):
    """
    Plot quadratic error E(c) as function of slope c,
    using intercept b0 from the line through first and last data points.
    Also marks c0 (endpoints slope) and c_opt (minimizer).
    """
    # first and last points
    A0, P0 = A_inv[0], Ps[0]
    A1, P1 = A_inv[-1], Ps[-1]

    # line through first and last
    c0 = (P1 - P0) / (A1 - A0)
    b0 = P0 - c0 * A0

    # analytic minimizer of E(c)
    num = np.sum(A_inv * (Ps - b0))
    den = np.sum(A_inv**2)
    c_opt = num / den

    # sweep c values around c0 and c_opt
    c_center = c_opt
    c_values = np.linspace(
        c_center - abs(c_center) * 2, c_center + abs(c_center) * 2, 400
    )

    errors = []
    for c in c_values:
        Ps_pred = c * A_inv + b0
        error = np.sum((Ps - Ps_pred) ** 2)
        errors.append(error)

    E_opt = np.sum((Ps - (c_opt * A_inv + b0)) ** 2)

    # Plot
    plt.figure(figsize=(6, 4))
    plt.plot(c_values, errors, "b-")
    plt.axvline(
        c_opt,
        color="r",
        linestyle="--",
        label=rf"$c_{{opt}} = {sci_notation(c_opt)}$",
    )
    plt.axhline(
        E_opt,
        color="g",
        linestyle="--",
        label=rf"$E={sci_notation(E_opt)}$",
    )

    plt.xlabel(r"Pendiente $c$ (Nm)")
    plt.ylabel(r"$E\ (\mathrm{\frac{N^2}{m^2}})$")
    plt.legend()
    plt.grid()
    # plt.tight_layout()

    os.makedirs("./images", exist_ok=True)
    plt.savefig("./images/regression_error.png", dpi=300)
    plt.close()
    print("Plot saved to ./images/regression_error.png")
    print(f"c_opt = {c_opt:.6f}, E(c_opt) = {E_opt:.6e}")


# -----------------------------
# Stationary pressure vs L
# -----------------------------
def compute_pressure_vs_L():
    results = []
    for fname, L in files_and_L.items():
        P = compute_pressure(fname, t_stable, S, L)
        if P is not None:
            results.append((L, P))
            print(f"{fname}: L={L}, P={P:.6f}")
        else:
            print(f"{fname}: no data after t_stable")

    if results:
        results.sort()
        Ls, Ps = zip(*results)
        A_inv = np.array([1 / ((S - 2 * r) ** 2 + (L_val - 2 * r) * S) for L_val in Ls])
        Ps = np.array(Ps)

        b0 = 0
        num = np.sum(A_inv * (Ps - b0))
        den = np.sum(A_inv**2)
        c_opt_0 = num / den
        Ps_pred = c_opt_0 * A_inv + b0
        E_opt_0 = np.sum((Ps - Ps_pred) ** 2)

        # --- slope from first/last points
        A0, P0 = A_inv[0], Ps[0]
        A1, P1 = A_inv[-1], Ps[-1]
        c0 = (P1 - P0) / (A1 - A0)
        b_opt = P0 - c0 * A0

        # --- compute optimal slope that minimizes E(c)
        num = np.sum(A_inv * (Ps - b_opt))
        den = np.sum(A_inv**2)
        c_opt = num / den

        # predictions with optimal slope
        Ps_pred = c_opt * A_inv + b_opt
        E_opt = np.sum((Ps - Ps_pred) ** 2)

        # --- plot pressure vs inverse area
        plt.figure(figsize=(6, 4))
        plt.scatter(A_inv, Ps, label="Datos")

        # regression line using c_opt
        x_fit = np.linspace(A_inv.min(), A_inv.max(), 100)
        plt.plot(
            x_fit,
            c_opt * x_fit + b_opt,
            "r-",
            label=rf"Ajuste $(E={sci_notation(E_opt)})$",
        )
        x_fit = np.linspace(A_inv.min(), A_inv.max(), 100)
        plt.plot(
            x_fit,
            c_opt_0 * x_fit + b0,
            "g-",
            label=rf"Gases ideales $(E={sci_notation(E_opt_0)})$",
        )

        plt.xlabel(r"$\mathrm{Área^{-1}}\ (\mathrm{\frac{1}{m^2}})$")
        plt.ylabel(r"$\langle \mathrm{Presión} \rangle\ (\mathrm{\frac{N}{m}})$")

        plt.legend()
        plt.grid()
        plt.tight_layout()

        os.makedirs("./images", exist_ok=True)
        plt.savefig("./images/pressure.png", dpi=300)
        plt.close()
        print("Plot saved to ./images/pressure.png")
        print(f"c_opt = {c_opt:.6f}, E(c_opt) = {E_opt:.6e}")

        # also make the error vs slope plot
        plot_regression_error_vs_c(A_inv, Ps)


# -----------------------------
# Pressure vs time per file
# -----------------------------
def plot_pressure_vs_time(filename, S, L, T=T):
    df = pd.read_csv(filename, header=None, names=["time", "wall", "vel"])
    if df.empty:
        print(f"{filename} is empty")
        return

    group1_walls = [0, 1, 2, 3]
    group2_walls = [4, 5, 6]

    lengths = wall_lengths(S, L)
    group1_length = sum(lengths[w] for w in group1_walls)
    group2_length = sum(lengths[w] for w in group2_walls)

    t_min = df["time"].min()
    t_max = df["time"].max()
    bins = np.arange(t_min, t_max + T, T)
    df["bin"] = np.digitize(df["time"], bins) - 1

    pressures_group1 = []
    pressures_group2 = []
    bin_centers = []

    for i in range(len(bins) - 1):
        bin_df = df[df["bin"] == i]
        impulse_g1 = (2 * bin_df[bin_df["wall"].isin(group1_walls)]["vel"].abs()).sum()
        impulse_g2 = (2 * bin_df[bin_df["wall"].isin(group2_walls)]["vel"].abs()).sum()

        pressures_group1.append(impulse_g1 / (T * group1_length))
        pressures_group2.append(impulse_g2 / (T * group2_length))
        bin_centers.append((bins[i] + bins[i + 1]) / 2)

    plt.figure(figsize=(6, 4))
    plt.plot(bin_centers, pressures_group1, label="Recinto izquierdo")
    plt.plot(bin_centers, pressures_group2, label="Recinto derecho")

    # vertical line at t_stable
    plt.axvline(x=t_stable, color="k", linestyle="--", linewidth=1)

    plt.xlabel(r"Tiempo (s)")
    plt.ylabel(r"Presión $(\mathrm{\frac{N}{m}})$")
    plt.legend()
    plt.grid()
    plt.tight_layout()

    os.makedirs("./images", exist_ok=True)
    save_path = f"./images/pressure_time_{os.path.basename(filename)}.png"
    plt.savefig(save_path, dpi=300)
    plt.close()
    print(f"Saved pressure vs time plot to {save_path}")


def plot_regression_error_vs_c_asdf(t, z2):
    """
    Plot quadratic error E(c) as function of slope c,
    using intercept b0 from the line through first and last data points.
    Also marks c0 (endpoints slope) and c_opt (minimizer).
    """
    # first and last points
    A0, P0 = t[0], z2[0]
    A1, P1 = t[-1], z2[-1]

    # line through first and last
    c0 = (P1 - P0) / (A1 - A0)
    b0 = P0 - c0 * A0

    # analytic minimizer of E(c)
    num = np.sum(t * (z2 - b0))
    den = np.sum(t**2)
    c_opt = num / den

    # sweep c values around c0 and c_opt
    c_center = c_opt
    c_values = np.linspace(
        c_center - abs(c_center) * 2, c_center + abs(c_center) * 2, 400
    )

    errors = []
    for c in c_values:
        Ps_pred = c * t + b0
        error = np.sum((z2 - Ps_pred) ** 2)
        errors.append(error)

    E_opt = np.sum((z2 - (c_opt * t + b0)) ** 2)

    # Plot
    plt.figure(figsize=(6, 4))
    plt.plot(c_values, errors, "b-")
    plt.axvline(
        c_opt,
        color="r",
        linestyle="--",
        label=rf"$c_{{opt}} = {sci_notation(c_opt)}$",
    )
    plt.axhline(
        E_opt,
        color="g",
        linestyle="--",
        label=rf"$E={sci_notation(E_opt)}$",
    )

    plt.xlabel(r"Pendiente $c$ (Nm)")
    plt.ylabel(r"$E\ (\mathrm{\frac{N^2}{m^2}})$")
    plt.legend()
    plt.grid()
    # plt.tight_layout()

    os.makedirs("./images", exist_ok=True)
    plt.savefig("./images/regression_error.png", dpi=300)
    plt.close()
    print("Plot saved to ./images/regression_error.png")
    print(f"c_opt = {c_opt:.6f}, E(c_opt) = {E_opt:.6e}")


# -----------------------------
# Main
# -----------------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "mode",
        choices=["stationary", "p_vs_L"],
        help="Mode: 'stationary' for avg pressure vs area, 'p_vs_L' for pressure vs time per file",
    )
    args = parser.parse_args()

    if args.mode == "p_vs_L":
        compute_pressure_vs_L()
    elif args.mode == "stationary":
        for fname, L in files_and_L.items():
            plot_pressure_vs_time(fname, S, L, T)


if __name__ == "__main__":
    main()
