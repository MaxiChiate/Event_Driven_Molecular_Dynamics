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

        # Linear regression fit
        coeffs = np.polyfit(A_inv, Ps, 1)
        fit_fn = np.poly1d(coeffs)

        # Plot points
        plt.figure(figsize=(6, 4))
        plt.scatter(A_inv, Ps, label="Datos")

        # Regression line
        x_fit = np.linspace(A_inv.min(), A_inv.max(), 100)
        plt.plot(x_fit, fit_fn(x_fit), "r-", label="Ajuste lineal")

        # Labels (your exact request)
        plt.xlabel(r"$Área^{-1}\ (\mathit{\frac{1}{m^2}})$")
        plt.ylabel(r"$Presión\ (\mathit{\frac{N}{m}})$")

        plt.legend()
        plt.tight_layout()
        plt.grid()

        os.makedirs("./images", exist_ok=True)
        plt.savefig("./images/pressure.png", dpi=300)
        plt.close()
        print("Plot saved to ./images/pressure.png")


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
    plt.xlabel(r"Tiempo $(\mathit{s})$")
    plt.ylabel(r"Presión $(\mathit{\frac{N}{m}})$")
    plt.legend()
    plt.grid()
    plt.tight_layout()

    os.makedirs("./images", exist_ok=True)
    save_path = f"./images/pressure_time_{os.path.basename(filename)}.png"
    plt.savefig(save_path, dpi=300)
    plt.close()
    print(f"Saved pressure vs time plot to {save_path}")


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

    if args.mode == "stationary":
        compute_pressure_vs_L()
    elif args.mode == "p_vs_L":
        for fname, L in files_and_L.items():
            plot_pressure_vs_time(fname, S, L, T)


if __name__ == "__main__":
    main()
