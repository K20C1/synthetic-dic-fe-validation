# Reading MOOSE FEA Output into Blender - Step 2: Surface and Deformation
# 13 July 2026

# Applied project (MAC465 Python development): extracting a surface mesh and its
# per-timestep deformation from MOOSE output for Blender.

# Draws on: NumPy - Array Basics (preallocation), Fancy Indexing, Broadcasting;
# Modules and File Handling (saving .npz); Collections and Control Flow (loops).

import pyvista as pv
import numpy as np


# ---------------------------------------------------------------------------
# 1. OPEN THE FILE AND SKIN THE SURFACE ONCE
# ---------------------------------------------------------------------------

reader = pv.get_reader("tensile_out.e")
n_steps = reader.number_time_points

# Skin once on the reference mesh so vertex count and ordering stay fixed across timesteps.
reader.set_active_time_point(0)
volume0 = reader.read()['Element Blocks'][0]
surface0 = volume0.extract_surface()

n_surf = surface0.n_points
print(f"Volume: {volume0.n_points} pts, {volume0.n_cells} cells")
print(f"Surface after skinning: {n_surf} pts, {surface0.n_cells} faces")

# Records which volume node each surface node came from.
orig_ids = surface0.point_data['vtkOriginalPointIds']

# .copy() keeps the reference coordinates separate from the mesh's own array.
ref_coords = surface0.points.copy()


# ---------------------------------------------------------------------------
# 2. BUILD THE DEFORMED SURFACE FOR EVERY TIMESTEP
# ---------------------------------------------------------------------------

# Preallocate the full (timesteps, points, xyz) array.
deformed = np.zeros((n_steps, n_surf, 3))
for t in range(n_steps):
    reader.set_active_time_point(t)
    vol = reader.read()['Element Blocks'][0]
    disp = vol.point_data['disp_']
    # Fancy indexing selects the surface-node displacements; broadcasting adds them.
    deformed[t] = ref_coords + disp[orig_ids]


# ---------------------------------------------------------------------------
# 3. VALIDATE AGAINST KNOWN PHYSICS
# ---------------------------------------------------------------------------

# Cube pulled 0.5 along X, fixed at X=0: known values to check the mapping against.
print("\nStep 0 max X:", deformed[0][:, 0].max(), "(expect ~1.0)")
print("Final max X:", deformed[-1][:, 0].max(), "(expect ~1.5 at 0.5 stretch)")
print("Final min X:", deformed[-1][:, 0].min(), "(expect ~0.0)")


# ---------------------------------------------------------------------------
# 4. SAVE FOR BLENDER
# ---------------------------------------------------------------------------

# One archive holds both the faces and the per-step coordinates.
np.savez("cube_deformed.npz", ref_faces=surface0.faces, coords=deformed)
print("\nSaved cube_deformed.npz")
