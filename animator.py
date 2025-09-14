#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import sys
import argparse
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Circle

def parse_args():
    p = argparse.ArgumentParser(description="Animar partículas con radio real (en unidades de datos).")
    p.add_argument("input", help="Ruta al CSV (formato: línea con t, seguidas de N líneas 'x,y,vx,vy,r').")
    p.add_argument("--fps", type=int, default=20, help="FPS del video.")
    p.add_argument("--stride", type=int, default=1, help="Tomar 1 de cada N frames (downsample).")
    p.add_argument("--max-frames", type=int, default=None, help="Limitar cantidad de frames (para pruebas).")
    p.add_argument("--dpi", type=int, default=120)
    p.add_argument("--figsize", type=float, nargs=2, default=(6,6))
    p.add_argument("--writer", choices=["ffmpeg","pillow"], default="ffmpeg",
                   help="ffmpeg (MP4) o pillow (GIF). Usa pillow si no tenés ffmpeg.")
    return p.parse_args()

def load_timesteps_stream(path):
    """
    Devuelve lista de (t, [(x,y,r,vx,vy), ...]) por frame.
    Asume que el N es constante (como N_300).
    """
    frames = []
    with open(path, "r") as f:
        current_t = None
        current = []
        for raw in f:
            line = raw.strip()
            if not line:
                continue
            # Línea de tiempo: solo número (ej. 0.0000)
            if re.match(r"^[+-]?\d+(\.\d+)?(e[+-]?\d+)?$", line, flags=re.IGNORECASE):
                if current_t is not None and current:
                    frames.append((current_t, current))
                current_t = float(line)
                current = []
            else:
                parts = line.split(",")
                if len(parts) < 5:
                    continue
                x, y, vx, vy, r = map(float, parts[:5])
                current.append((x, y, r, vx, vy))
        # último bloque
        if current_t is not None and current:
            frames.append((current_t, current))
    if not frames:
        raise ValueError("No se detectaron frames. Revisá el formato del archivo.")
    # Chequeo rápido de N constante
    n0 = len(frames[0][1])
    for t, plist in frames:
        if len(plist) != n0:
            # No cortamos, pero avisamos
            print(f"[WARN] N variable: frame con t={t} tiene {len(plist)} partículas (esperadas {n0}).")
    return frames

def compute_bounds(frames):
    xs, ys, rs = [], [], []
    for _, plist in frames:
        for (x,y,r,_,_) in plist:
            xs.append(x); ys.append(y); rs.append(r)
    if not xs:
        raise ValueError("No hay partículas para calcular límites.")
    margin = max(rs) if rs else 0.0
    xmin, xmax = min(xs)-margin, max(xs)+margin
    ymin, ymax = min(ys)-margin, max(ys)+margin
    # Evitar límites degenerados
    if xmin == xmax:
        xmin -= 1e-3; xmax += 1e-3
    if ymin == ymax:
        ymin -= 1e-3; ymax += 1e-3
    return xmin, xmax, ymin, ymax

def main():
    args = parse_args()
    csv_path = os.path.abspath(args.input)
    if not os.path.exists(csv_path):
        print(f"Archivo no encontrado: {csv_path}", file=sys.stderr)
        sys.exit(1)

    out_dir = os.path.dirname(csv_path)
    out_ext = ".mp4" if args.writer == "ffmpeg" else ".gif"
    out_file = os.path.join(out_dir, f"animacion_particulas{out_ext}")

    print("[INFO] Cargando frames...")
    frames_all = load_timesteps_stream(csv_path)

    # Downsample y límite
    frames = frames_all[::max(1, args.stride)]
    if args.max_frames is not None:
        frames = frames[:args.max_frames]

    print(f"[INFO] Frames a procesar: {len(frames)} (stride={args.stride})")
    n_particles = len(frames[0][1])
    print(f"[INFO] Partículas por frame (estimado): {n_particles}")

    # Límites
    xmin, xmax, ymin, ymax = compute_bounds(frames)

    # Figura
    fig, ax = plt.subplots(figsize=tuple(args.figsize), dpi=args.dpi)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.set_xlabel("x"); ax.set_ylabel("y")

    # Inicializar N círculos una sola vez (reutilizamos los mismos)
    # Si algún frame trae menos, escondemos los que sobran.
    circles = []
    # Usamos el radio del primer frame como placeholder; se actualiza en cada frame
    for _ in range(n_particles):
        c = Circle((0.0, 0.0), 0.0, facecolor="C0", edgecolor="black", alpha=0.7, linewidth=0.5)
        ax.add_patch(c)
        circles.append(c)

    title = ax.set_title("")

    def init():
        # Posicionar fuera de vista
        for c in circles:
            c.center = (xmin - 10.0, ymin - 10.0)
            c.set_radius(0.0)
        title.set_text("")
        return circles + [title]

    def update(i):
        t, plist = frames[i]
        # Actualizar hasta len(plist)
        m = len(plist)
        for idx in range(m):
            x, y, r, vx, vy = plist[idx]
            circles[idx].center = (x, y)
            circles[idx].set_radius(r)
            # opcional: color por |v|
            # speed = (vx*vx + vy*vy) ** 0.5
            # circles[idx].set_facecolor(plt.cm.viridis(min(1.0, speed / 0.01)))
        # Esconder el resto si existen
        for idx in range(m, n_particles):
            circles[idx].center = (xmin - 10.0, ymin - 10.0)
            circles[idx].set_radius(0.0)
        title.set_text(f"t = {t:.4f}  |  frame {i+1}/{len(frames)}")
        # blit=False para patches
        return circles + [title]

    ani = FuncAnimation(fig, update, frames=len(frames), init_func=init,
                        interval=int(1000 / args.fps), blit=False)

    print(f"[INFO] Exportando a: {out_file}")
    if args.writer == "ffmpeg":
        # Requiere ffmpeg instalado
        ani.save(out_file, writer="ffmpeg", fps=args.fps, dpi=args.dpi)
    else:
        from matplotlib.animation import PillowWriter
        ani.save(out_file, writer=PillowWriter(fps=args.fps), dpi=args.dpi)

    print("[OK] Listo:", out_file)

if __name__ == "__main__":
    main()