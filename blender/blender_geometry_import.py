# Reading MOOSE FEA Output into Blender - Step 3: Building the Mesh
# 13 July 2026

# Applied project (MAC465 Python development): rebuilding the extracted surface as
# a Blender mesh via the bpy API. Runs in Blender's Python console.

# Draws on: Modules and File Handling (np.load); Collections and Control Flow
# (while loop, slicing); NumPy - Array Basics (shape unpacking).

import bpy
import numpy as np


# ---------------------------------------------------------------------------
# 1. LOAD THE SAVED SURFACE DATA
# ---------------------------------------------------------------------------

# Archive written by extract_surface.py (on the WSL side).
path = r"\\wsl.localhost\Ubuntu-20.04\home\map25tbw\projects\moose_blender\cube_deformed.npz"

data = np.load(path)
faces_raw = data["ref_faces"]   # VTK face format: [n, i0, i1, ..., n, i0, i1, ...]
coords = data["coords"]         # shape (n_steps, n_points, 3)

# Shape unpacking reports what was loaded.
n_steps, n_points, _ = coords.shape
print(f"Loaded: {n_steps} timesteps, {n_points} surface points")

# Step 0 is the reference (undeformed) shape.
verts = coords[0].tolist()


# ---------------------------------------------------------------------------
# 2. CONVERT THE VTK FACE ARRAY TO BLENDER FACES
# ---------------------------------------------------------------------------

# VTK faces are flattened as [count, v0, v1, ...]; walk the array and slice each into a tuple.
faces = []
i = 0
while i < len(faces_raw):
    count = faces_raw[i]
    faces.append(tuple(faces_raw[i+1 : i+1+count]))
    i += 1 + count

print(f"Parsed {len(faces)} faces")


# ---------------------------------------------------------------------------
# 3. BUILD THE MESH AND ADD IT TO THE SCENE
# ---------------------------------------------------------------------------

# from_pydata: vertices, edges (empty, inferred from faces), faces.
mesh = bpy.data.meshes.new("cube_fea")
mesh.from_pydata(verts, [], faces)
mesh.update()

# Link the object into the current collection so it appears in the scene.
obj = bpy.data.objects.new("cube_fea", mesh)
bpy.context.collection.objects.link(obj)

print("Mesh built and linked.")
