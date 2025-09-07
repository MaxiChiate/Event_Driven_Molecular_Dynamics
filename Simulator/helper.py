from ovito.io import import_file
from ovito.data import DataCollection

def reader(f, data: DataCollection, **kwargs):
    positions = []
    radii = []
    for line in f:
        parts = line.strip().split(",")
        if len(parts) == 5:  # particle line
            x, y, vx, vy, r = map(float, parts)
            positions.append((x, y, 0.0))  # add z=0
            radii.append(r)
    import numpy as np
    data.particles.create_property("Position", data=positions)
    data.particles.create_property("Radius", data=radii)

pipeline = import_file("./outputs/N_300_L0.090/output_N300_L0.090_t1000_0000.csv",
                       format=reader)
pipeline.add_to_scene()
