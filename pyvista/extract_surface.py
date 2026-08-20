# Reading MOOSE FEA Output into Blender - Step 2: Surface, Observation Face and Deformation
# 20 August 2026

# Applied project (MAC465 Python development): extracting the specimen surface mesh,
# identifying the observation face, generating UV coordinates, and storing its
# per-timestep deformation from MOOSE output for Blender.

# Draws on: NumPy - Array Basics (preallocation), Fancy Indexing, Boolean Masks,
# Broadcasting; Modules and File Handling (saving .npz); Collections and Control Flow
# (loops and exception handling).

import pyvista as pv
import numpy as np


# ---------------------------------------------------------------------------
# 1. OPEN THE FILE AND SKIN THE REFERENCE SURFACE
# ---------------------------------------------------------------------------

reader = pv.get_reader("tensile_out.e")
n_steps = reader.number_time_points

# Enable global node IDs before reading so PedigreeNodeId is included on the mesh.
try:
    reader.reader.SetGenerateGlobalNodeIdArray(True)
except Exception as e:
    print("Could not enable global node IDs:", e)

# Skin once on the reference mesh so vertex count and ordering stay fixed across timesteps.
reader.set_active_time_point(0)
surface0 = reader.read()['Element Blocks']['specimen'].extract_surface(
    algorithm='dataset_surface')

n_surf = surface0.n_points
print(f"Surface: {n_surf} pts, {surface0.n_cells} faces")

# .copy() keeps the reference coordinates separate from the mesh's own array.
ref_coords = surface0.points.copy()

# Records the original MOOSE/global node ID associated with each surface point.
node_ids = surface0.point_data['PedigreeNodeId']


# ---------------------------------------------------------------------------
# 2. IDENTIFY THE +Z OBSERVATION FACE
# ---------------------------------------------------------------------------

# Compute one normal per surface face so the outward-facing +Z side can be selected.
surface0 = surface0.compute_normals(
    cell_normals=True,
    point_normals=False,
    auto_orient_normals=True)

cell_normals = surface0.cell_data['Normals']

# Select faces whose normal points predominantly in the +Z direction.
# 0.9 corresponds to approximately 26 degrees from +Z.
tol = 0.9
obs_cells = np.where(cell_normals[:, 2] > tol)[0]

print(
    f"Observation-face cells (+Z, tol={tol}): "
    f"{len(obs_cells)} of {surface0.n_cells}"
)

# Boolean mask records which surface nodes belong to the selected observation face.
obs_mask = np.zeros(n_surf, dtype=bool)

for cid in obs_cells:
    obs_mask[surface0.get_cell(cid).point_ids] = True

print(f"Observation-face nodes: {obs_mask.sum()} of {n_surf}")


# ---------------------------------------------------------------------------
# 3. BUILD UV COORDINATES FROM THE REFERENCE GEOMETRY
# ---------------------------------------------------------------------------

# Use only the observation-face nodes to determine its reference XY dimensions.
obs_pts = ref_coords[obs_mask]

x_min, x_max = obs_pts[:, 0].min(), obs_pts[:, 0].max()
y_min, y_max = obs_pts[:, 1].min(), obs_pts[:, 1].max()

print(
    f"Observation face extents: X {x_min:.3f} to {x_max:.3f} "
    f"({x_max - x_min:.3f}), "
    f"Y {y_min:.3f} to {y_max:.3f} ({y_max - y_min:.3f})"
)

print(
    f"Aspect ratio (Y/X): "
    f"{(y_max - y_min) / (x_max - x_min):.3f}"
)

# Linearly map the reference XY coordinates into Blender's 0-1 UV coordinate range.
uvs = np.zeros((n_surf, 2))
uvs[:, 0] = (ref_coords[:, 0] - x_min) / (x_max - x_min)
uvs[:, 1] = (ref_coords[:, 1] - y_min) / (y_max - y_min)


# ---------------------------------------------------------------------------
# 4. BUILD THE DEFORMED SURFACE FOR EVERY TIMESTEP
# ---------------------------------------------------------------------------

# Preallocate the full (timesteps, points, xyz) array.
deformed = np.zeros((n_steps, n_surf, 3))

for t in range(n_steps):
    reader.set_active_time_point(t)

    surface = reader.read()['Element Blocks']['specimen'].extract_surface(
        algorithm='dataset_surface')

    # Broadcasting adds each timestep's displacement to the reference coordinates.
    deformed[t] = ref_coords + surface.point_data['disp_']


# ---------------------------------------------------------------------------
# 5. VALIDATE THE DEFORMATION
# ---------------------------------------------------------------------------

# Compare the maximum Y position between the first and final timestep.
y_growth = deformed[-1][:, 1].max() - deformed[0][:, 1].max()
print("\nY grew by:", y_growth)


# ---------------------------------------------------------------------------
# 6. SAVE FOR BLENDER
# ---------------------------------------------------------------------------

# Ask for a model name so the exported archive can be reused for different specimens.
name = input("Enter model name: ").strip()

# One archive holds the mesh connectivity, deformation, UV mapping, node IDs,
# and the masks identifying the observation face.
np.savez(
    f"{name}_deformed.npz",
    ref_faces=surface0.faces,
    coords=deformed,
    uvs=uvs,
    node_ids=node_ids,
    obs_mask=obs_mask,
    obs_cells=obs_cells
)

print(f"\nSaved {name}_deformed.npz")
