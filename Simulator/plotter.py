# %%
import os, re, math, glob
from pathlib import Path
from typing import List, Tuple, Optional
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

# --- CONFIG (you can tweak) ---
INPUT_FILES = sorted(glob.glob("./outputs/N_300_L0.090/output_N300_L0.090_t1000_0000.csv"))
OUT_DIR = Path("./outputs")
OUT_DIR.mkdir(parents=False, exist_ok=True)

# Animation visuals
FPS = 30
STEP_SKIP = 1      # use every Nth frame to speed up
DOT_BASE_SIZE = 18 # base scatter dot size (points^2). Will scale slightly with radius.
SHOW_VELOCITY = True  # draw tiny velocity vectors
ARROW_SCALE = 0.1     # scale for velocity vectors (smaller = smaller arrows)

# --- PARSER ---
def parse_L_from_name(path: str) -> Optional[float]:
    m = re.search(r"L([0-9]+(?:\.[0-9]+)?)", Path(path).name)
    if m:
        return float(m.group(1))
    return None

def read_frames(csv_path: str) -> Tuple[List[np.ndarray], List[float]]:
    """
    Reads custom CSV:
    - First line of each block: time 't' (a single float)
    - Next N lines: x,y,vx,vy,r (5 floats) for each particle
    Repeats for each timestep.

    Returns: (frames, times)
      frames: list of arrays with shape (N, 5)
      times: list of float time values
    """
    frames: List[np.ndarray] = []
    times: List[float] = []
    with open(csv_path, "r", encoding="utf-8") as f:
        buf = []
        current_time = None
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = [p.strip() for p in line.split(",")]
            # Detect time line (single number, may have no commas)
            if len(parts) == 1:
                # flush previous frame if any
                if current_time is not None and buf:
                    frames.append(np.array(buf, dtype=float))
                    times.append(current_time)
                    buf = []
                # set new time
                current_time = float(parts[0])
            else:
                # particle row: x,y,vx,vy,r
                if len(parts) != 5:
                    raise ValueError(f"Invalid particle row in {csv_path}: {line}")
                buf.append([float(v) for v in parts])
        # flush last frame
        if current_time is not None and buf:
            frames.append(np.array(buf, dtype=float))
            times.append(current_time)
    return frames, times

# --- ANIMATION ---
def animate_file(csv_path: str, fps: int = FPS, step_skip: int = STEP_SKIP) -> str:
    frames, times = read_frames(csv_path)
    if not frames:
        raise RuntimeError(f"No frames parsed from {csv_path}")
    # Subsample if needed
    frames = frames[::max(1, step_skip)]
    times = times[::max(1, step_skip)]

    # Domain
    L = parse_L_from_name(csv_path)
    if L is None:
        # fallback to data bounds
        all_xy = np.vstack([fr[:, :2] for fr in frames])
        xmin, ymin = np.min(all_xy, axis=0)
        xmax, ymax = np.max(all_xy, axis=0)
    else:
        xmin = ymin = 0.0
        xmax = ymax = L

    # Base sizes from radius (normalize to median so relative variation is preserved)
    r_median = float(np.median(frames[0][:, 4])) if frames[0].shape[0] > 0 else 1.0
    def sizes_from_r(r: np.ndarray) -> np.ndarray:
        # Keep it simple and proportional
        scale = DOT_BASE_SIZE / max(r_median, 1e-9)
        return (np.clip(r, 1e-9, None) * scale) ** 2

    # Setup figure
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.set_aspect('equal', adjustable='box')
    scat = ax.scatter(frames[0][:,0], frames[0][:,1], s=sizes_from_r(frames[0][:,4]))
    title = ax.text(0.02, 0.98, "", transform=ax.transAxes, va="top")

    quiv = None
    if SHOW_VELOCITY:
        quiv = ax.quiver(
            frames[0][:,0], frames[0][:,1],
            frames[0][:,2], frames[0][:,3],
            angles='xy', scale_units='xy', scale=1.0/ARROW_SCALE, width=0.002
        )

    def update(i):
        fr = frames[i]
        scat.set_offsets(fr[:, :2])
        scat.set_sizes(sizes_from_r(fr[:, 4]))
        if quiv is not None:
            quiv.set_offsets(fr[:, :2])
            quiv.set_UVC(fr[:, 2], fr[:, 3])
        title.set_text(f"{Path(csv_path).name}\nframe {i+1}/{len(frames)} • t={times[i]:.3f}")
        return scat, quiv, title

    anim = FuncAnimation(fig, update, frames=len(frames), interval=1000/fps, blit=False)

    out_gif = OUT_DIR / (Path(csv_path).stem + ".gif")
    anim.save(out_gif, writer=PillowWriter(fps=fps))
    plt.close(fig)
    return str(out_gif)

# Run on available input files
outputs = []
for f in INPUT_FILES:
    try:
        outputs.append(animate_file(f))
    except Exception as e:
        outputs.append(f"ERROR {f}: {e}")

outputs
